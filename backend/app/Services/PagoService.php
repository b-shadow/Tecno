<?php

namespace App\Services;

use App\Models\ComprobantePago;
use App\Models\Interes;
use App\Models\MetodoPago;
use App\Models\OrdenPago;
use App\Models\Prospecto;
use App\Models\Usuario;
use App\Repositories\PagoRepository;
use App\Services\Alcance;
use App\Services\Conversion;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Str;
use Illuminate\Validation\Rule;
use Illuminate\Validation\ValidationException;

/**
 * CU6 y enunciado 10: métodos de pago del prospecto, orden con pago único o plan de cuotas,
 * comprobantes, pasarela simulada con tarjeta y validación por coordinación.
 * Aprobar la 1.ª cuota dispara la conversión (matrícula) si los datos están completos (RF3.4).
 */
class PagoService
{
    private const MARCAS = ['Visa', 'Mastercard', 'American Express'];

    public function __construct(private readonly PagoRepository $pagos)
    {
    }

    public function descuentos(): JsonResponse
    {
        return response()->json(['descuentos' => $this->pagos->descuentos()]);
    }

    // ---------------------------------------------------------------- métodos de pago

    public function metodos(Request $request, Prospecto $prospecto): JsonResponse
    {
        $this->autorizarProspecto($request, $prospecto);

        return response()->json(['metodos' => $this->pagos->metodos($prospecto), 'marcas' => self::MARCAS]);
    }

    public function registrarMetodo(Request $request, Prospecto $prospecto): JsonResponse
    {
        $this->autorizarProspecto($request, $prospecto);
        $data = $request->validate([
            'tipo' => ['required', Rule::in(MetodoPago::TIPOS)],
            'titular' => ['required', 'string', 'max:120', "regex:/^[\\pL\\s'.-]+$/u"],
            'numero' => ['nullable', 'required_if:tipo,Tarjeta', 'string', 'regex:/^[0-9 ]{13,23}$/'],
            'vencimiento' => ['nullable', 'required_if:tipo,Tarjeta', 'regex:/^(0[1-9]|1[0-2])\/[0-9]{2}$/'],
        ], [
            'numero.regex' => 'El número de tarjeta debe tener entre 13 y 19 dígitos.',
            'vencimiento.regex' => 'El vencimiento debe tener el formato MM/AA.',
        ], ['numero' => 'número de tarjeta', 'vencimiento' => 'vencimiento']);

        $fila = ['documento' => $prospecto->documento, 'tipo' => $data['tipo'], 'titular' => trim($data['titular']), 'estado' => 'activo'];

        if ($data['tipo'] === 'Tarjeta') {
            $numero = preg_replace('/\D/', '', $data['numero']);
            [$mes, $anio] = explode('/', $data['vencimiento']);
            $errores = [];
            if (! $this->luhn($numero)) {
                $errores['numero'] = 'El número de tarjeta no es válido.';
            }
            if (Carbon::create(2000 + (int) $anio, (int) $mes)->endOfMonth()->isPast()) {
                $errores['vencimiento'] = 'La tarjeta está vencida.';
            }
            if ($errores) {
                throw ValidationException::withMessages($errores);
            }
            // Nunca se guarda el número completo ni el CVV: solo marca, últimos 4 dígitos y vencimiento.
            $fila += ['marca' => $this->marca($numero), 'ultimos_digitos' => substr($numero, -4), 'vencimiento' => $data['vencimiento']];
        }

        return response()->json(['mensaje' => 'Método de pago registrado.', 'metodo' => $this->pagos->crearMetodo($fila)], 201);
    }

    public function cambiarEstadoMetodo(Request $request, MetodoPago $metodo): JsonResponse
    {
        $this->pagos->metodoConProspecto($metodo);
        $this->autorizarProspecto($request, $metodo->prospecto);
        $data = $request->validate(['estado' => ['required', Rule::in(['activo', 'inactivo'])]]);
        $this->pagos->actualizarMetodo($metodo, $data);

        return response()->json(['mensaje' => $data['estado'] === 'activo' ? 'Método activado.' : 'Método desactivado.', 'metodo' => $metodo]);
    }

    // ---------------------------------------------------------------- órdenes y cuotas

    public function ordenes(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $ordenes = $this->pagos->ordenes($usuario);

        return response()->json(['ordenes' => $ordenes]);
    }

    /** Orden de pago: pago único (1 cuota) o plan de 2 a 12 cuotas mensuales. La genera el vendedor de la tarjeta. */
    public function crearOrden(Request $request, Interes $interes): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_if($interes->vendedor_correo !== $usuario->correo, 403, 'Solo el vendedor asignado genera la orden de pago.');
        abort_if(in_array($interes->estado, ['Convertido', 'Perdido'], true), 422, 'La tarjeta ya está cerrada.');

        $data = $request->validate([
            'modulos' => ['required', 'array', 'min:1'],
            'modulos.*' => ['required', 'string', 'distinct', Rule::exists('catalogo_cache', 'codigo')->where('estado', 'abierto')],
            'descuentos' => ['nullable', 'array'],
            'descuentos.*' => ['string', Rule::exists('descuentos', 'codigo')->where('estado', 'activo')],
            'cuotas' => ['required', 'integer', 'between:1,12'],
            'primer_vencimiento' => ['required', 'date', 'after_or_equal:today'],
        ], [], ['modulos' => 'módulos', 'cuotas' => 'número de cuotas', 'primer_vencimiento' => 'primer vencimiento']);

        $orden = $this->pagos->transaccion(function () use ($interes, $usuario, $data) {
            $modulos = $this->pagos->modulos($data['modulos']);
            $descuentos = $this->pagos->descuentosPorCodigo($data['descuentos'] ?? []);
            $subtotal = round($modulos->sum(fn ($m) => (float) $m->precio), 2);
            $descuentoTotal = 0.0;

            $orden = $this->pagos->crearOrden([
                'nro_tarjeta' => $interes->nro_tarjeta, 'vendedor_correo' => $usuario->correo,
                'subtotal' => $subtotal, 'descuento_total' => 0, 'total' => $subtotal, 'fecha_generacion' => now(),
            ]);

            foreach ($descuentos as $descuento) {
                $monto = round($subtotal * (float) $descuento->porcentaje / 100, 2);
                $descuentoTotal += $monto;
                $filasDescuento[] = [
                    'nro_orden' => $orden->nro_orden, 'descuento_codigo' => $descuento->codigo,
                    'porcentaje' => $descuento->porcentaje, 'monto' => $monto, 'created_at' => now(), 'updated_at' => now(),
                ];
            }
            $this->pagos->insertarDescuentosOrden($filasDescuento ?? []);
            $total = max(round($subtotal - $descuentoTotal, 2), 0);
            abort_if($total <= 0, 422, 'El total de la orden debe ser mayor a cero.');
            $this->pagos->actualizarOrden($orden, ['descuento_total' => round($descuentoTotal, 2), 'total' => $total]);

            $items = [];
            foreach ($modulos as $m) {
                $items[] = [
                    'anuncio_codigo' => $m->anuncio_codigo, 'modulo_codigo' => $m->codigo, 'programa_nombre' => $m->programa->nombre,
                    'modulo_nombre' => $m->nombre, 'modulo_descripcion' => $m->descripcion, 'anuncio_titulo' => 'Inscripción abierta: '.$m->nombre,
                    'precio_acordado' => $m->precio, 'fecha' => now(),
                ];
            }
            $this->pagos->insertarItems($orden, $items);

            // Plan de pagos: cuotas mensuales iguales; la última absorbe el redondeo.
            $n = (int) $data['cuotas'];
            $base = floor($total / $n * 100) / 100;
            $filasCuota = [];
            for ($i = 1; $i <= $n; $i++) {
                $filasCuota[] = [
                    'nro_orden' => $orden->nro_orden, 'nro_cuota' => $i,
                    'monto' => $i === $n ? round($total - $base * ($n - 1), 2) : $base,
                    'fecha_vencimiento' => Carbon::parse($data['primer_vencimiento'])->addMonthsNoOverflow($i - 1)->toDateString(),
                    'estado' => 'Pendiente de pago', 'created_at' => now(), 'updated_at' => now(),
                ];
            }
            $this->pagos->insertarCuotas($filasCuota);
            $this->pagos->crearPago(['nro_orden' => $orden->nro_orden, 'codigo_qr' => 'CRM-QR-ORD-'.$orden->nro_orden.'-'.Str::upper(Str::random(10)), 'estado' => 'Pendiente de pago']);

            $plan = $n === 1 ? 'pago único' : "plan de {$n} cuotas";
            $this->pagos->registrarInteraccion($interes, [
                'usuario_correo' => $usuario->correo, 'tipo' => 'Orden de pago enviada', 'fecha' => now(),
                'descripcion' => "Orden #{$orden->nro_orden} por {$total} Bs ({$plan}) para {$modulos->count()} módulo(s).",
                'resultado' => 'Orden pendiente de pago',
            ]);
            $this->pagos->actualizarInteres($interes, ['estado' => 'Promesa de Pago', 'ultima_actividad_en' => now()]);

            return $orden;
        });

        return response()->json(['mensaje' => 'Orden de pago generada.', 'orden' => $this->pagos->ordenCompleta($orden)], 201);
    }

    /** Cuotas para validar (coordinación): por defecto las que esperan revisión. */
    public function cuotas(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $cuotas = $this->pagos->cuotas($usuario, $request->query('estado'));

        return response()->json(['cuotas' => $cuotas]);
    }

    /** El vendedor registra el comprobante que el prospecto le envió (imagen o PDF, hasta 5 MB). */
    public function registrarComprobante(Request $request, OrdenPago $orden, int $cuota): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $interes = $this->pagos->interesDeOrden($orden);
        Alcance::autorizarTarjeta($usuario, $interes);
        $data = $request->validate([
            'archivo' => ['required', 'string', 'max:8388608'],
            'nro_metodo' => ['nullable', Rule::exists('metodos_pago', 'nro_metodo')->where('documento', $interes->documento)->where('estado', 'activo')],
            'remitente' => ['nullable', 'string', 'max:160'],
            'hora_pago' => ['nullable', 'date', 'before_or_equal:now'],
            'observacion' => ['nullable', 'string', 'max:1000'],
        ], [], ['archivo' => 'comprobante', 'nro_metodo' => 'método de pago', 'hora_pago' => 'hora del pago']);

        $mime = $this->validarArchivo($data['archivo']);

        $this->pagos->transaccion(function () use ($orden, $interes, $cuota, $data, $mime, $usuario) {
            $fila = $this->cuotaBloqueada($orden->nro_orden, $cuota);
            abort_if($fila->estado === 'Pago aprobado', 422, 'Esta cuota ya está pagada.');
            abort_if($fila->estado === 'En revision', 422, 'Ya hay un comprobante en revisión para esta cuota.');

            $prospecto = $interes->prospecto;
            // Clase 40: nombre legible y ligado al dato.
            $nombre = Str::slug("{$prospecto->apellido} {$prospecto->nombre}", '_')."_orden{$orden->nro_orden}_cuota{$cuota}.".($mime === 'application/pdf' ? 'pdf' : explode('/', $mime)[1]);

            $this->pagos->crearComprobante([
                'nro_orden' => $orden->nro_orden, 'nro_cuota' => $cuota, 'archivo' => $data['archivo'], 'nombre_archivo' => $nombre, 'mime' => $mime,
                'remitente' => $data['remitente'] ?? null, 'hora_pago' => $data['hora_pago'] ?? null, 'observacion' => $data['observacion'] ?? null,
                'fecha_envio' => now(), 'estado_revision' => 'En revision',
            ]);
            $this->pagos->cambiarEstadoCuota($orden->nro_orden, $cuota, 'En revision', ['nro_metodo' => $data['nro_metodo'] ?? null]);
            $this->pagos->registrarInteraccion($interes, [
                'usuario_correo' => $usuario->correo, 'tipo' => 'Pago informado', 'fecha' => now(),
                'descripcion' => "Comprobante de la cuota {$cuota} de la orden #{$orden->nro_orden} enviado a revisión.", 'resultado' => 'Pago en revisión',
            ]);
            $this->pagos->actualizarInteres($interes, ['ultima_actividad_en' => now()]);
        });

        return response()->json(['mensaje' => 'Comprobante enviado a revisión.'], 201);
    }

    /** Pasarela simulada: cobra la cuota con una tarjeta registrada y la aprueba al instante. */
    public function pagarConTarjeta(Request $request, OrdenPago $orden, int $cuota): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $interes = $this->pagos->interesDeOrden($orden);
        Alcance::autorizarTarjeta($usuario, $interes);
        $data = $request->validate([
            'nro_metodo' => ['required', Rule::exists('metodos_pago', 'nro_metodo')->where('documento', $interes->documento)->where('tipo', 'Tarjeta')->where('estado', 'activo')],
        ], [], ['nro_metodo' => 'tarjeta']);

        $metodo = $this->pagos->metodo((int) $data['nro_metodo']);
        [$mes, $anio] = explode('/', $metodo->vencimiento);
        abort_if(Carbon::create(2000 + (int) $anio, (int) $mes)->endOfMonth()->isPast(), 422, 'La tarjeta está vencida.');

        $resultado = $this->pagos->transaccion(function () use ($orden, $cuota, $metodo, $usuario) {
            $fila = $this->cuotaBloqueada($orden->nro_orden, $cuota);
            abort_if(in_array($fila->estado, ['Pago aprobado', 'En revision'], true), 422, 'Esta cuota no está pendiente de pago.');
            $transaccion = 'SIM-'.Str::upper(Str::random(12));

            $this->pagos->cambiarEstadoCuota($orden->nro_orden, $cuota, 'Pago aprobado', [
                'nro_metodo' => $metodo->nro_metodo, 'observacion' => "Pasarela simulada {$transaccion} con {$metodo->marca} ****{$metodo->ultimos_digitos}",
            ]);

            return [$transaccion, $this->trasAprobar($orden, $cuota, $usuario, "Cuota {$cuota} cobrada con {$metodo->marca} ****{$metodo->ultimos_digitos} (transacción {$transaccion}).")];
        });

        return response()->json(['mensaje' => 'Pago aprobado por la pasarela simulada.', 'transaccion' => $resultado[0], 'faltantes_conversion' => $resultado[1]]);
    }

    public function aprobar(Request $request, OrdenPago $orden, int $cuota): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $interes = $this->pagos->interesDeOrden($orden);
        Alcance::autorizarTarjeta($usuario, $interes);
        $data = $request->validate(['observacion' => ['nullable', 'string', 'max:1000']]);

        $faltantes = $this->pagos->transaccion(function () use ($orden, $cuota, $data, $usuario) {
            $fila = $this->cuotaBloqueada($orden->nro_orden, $cuota);
            abort_if($fila->estado !== 'En revision', 422, 'Solo se aprueba una cuota con comprobante en revisión.');

            $this->pagos->cambiarEstadoCuota($orden->nro_orden, $cuota, 'Pago aprobado', ['observacion' => $data['observacion'] ?? null]);
            $this->pagos->actualizarComprobantes($orden->nro_orden, $cuota, 'Pago aprobado');

            return $this->trasAprobar($orden, $cuota, $usuario, "Cuota {$cuota} de la orden #{$orden->nro_orden} aprobada por coordinación.");
        });

        $mensaje = $cuota === 1 && ! $faltantes ? 'Pago aprobado. El prospecto quedó matriculado (Convertido).' : 'Pago aprobado.';

        return response()->json(['mensaje' => $mensaje, 'faltantes_conversion' => $faltantes]);
    }

    public function rechazar(Request $request, OrdenPago $orden, int $cuota): JsonResponse
    {
        $interes = $this->pagos->interesDeOrden($orden);
        Alcance::autorizarTarjeta($request->attributes->get('auth_usuario'), $interes);
        $data = $request->validate(['observacion' => ['required', 'string', 'max:1000']], ['observacion.required' => 'Indique el motivo del rechazo para el vendedor.']);

        $this->pagos->transaccion(function () use ($orden, $cuota, $data) {
            $fila = $this->cuotaBloqueada($orden->nro_orden, $cuota);
            abort_if($fila->estado !== 'En revision', 422, 'Solo se rechaza una cuota con comprobante en revisión.');
            $this->pagos->cambiarEstadoCuota($orden->nro_orden, $cuota, 'Pago rechazado', ['observacion' => $data['observacion']]);
            $this->pagos->actualizarComprobantes($orden->nro_orden, $cuota, 'Pago rechazado', $data['observacion']);
        });

        return response()->json(['mensaje' => 'Comprobante rechazado. El vendedor verá el motivo.']);
    }

    public function comprobante(Request $request, ComprobantePago $comprobante): JsonResponse
    {
        $orden = $this->pagos->ordenDeComprobante($comprobante->nro_orden);
        Alcance::autorizarTarjeta($request->attributes->get('auth_usuario'), $orden->interes);

        return response()->json(['comprobante' => $comprobante->makeVisible('archivo')]);
    }

    // ---------------------------------------------------------------- apoyo

    /** Cuota 1: se cambia pagos.estado y el trigger lo copia a la cuota (así el P1 ve lo mismo). */
    private function cambiarEstadoCuota(int $nroOrden, int $cuota, string $estado, array $extra = []): void
    {
        $extra = array_filter($extra, fn ($v) => $v !== null);
        $this->pagos->cambiarEstadoCuota($nroOrden, $cuota, $estado, $extra);
    }

    /** Tras aprobar: interacción y, si es la 1.ª cuota, conversión (RF3.4). Devuelve lo que falte para convertir. */
    private function trasAprobar(OrdenPago $orden, int $cuota, Usuario $usuario, string $descripcion): array
    {
        $interes = $this->pagos->interesBloqueado($orden->nro_tarjeta);
        $this->pagos->registrarInteraccion($interes, ['usuario_correo' => $usuario->correo, 'tipo' => 'Compra validada', 'descripcion' => $descripcion, 'resultado' => 'Pago aprobado', 'fecha' => now()]);

        if ($cuota !== 1 || $interes->estado === 'Convertido') {
            return [];
        }
        $faltan = Conversion::faltantes($interes);
        if (! $faltan) {
            Conversion::procesar($interes, $usuario);
        }

        return $faltan;
    }

    private function cuotaBloqueada(int $nroOrden, int $cuota): object
    {
        $fila = $this->pagos->cuotaBloqueada($nroOrden, $cuota);
        abort_unless($fila, 404, 'La cuota no existe.');

        return $fila;
    }

    private function autorizarProspecto(Request $request, ?Prospecto $prospecto): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_unless($prospecto && $this->pagos->prospectoEnCartera($prospecto, $usuario), 403, 'Este prospecto no está dentro de su cartera.');
    }

    private function validarArchivo(string $archivo): string
    {
        $valido = preg_match('~^data:(image/(?:png|jpeg|webp)|application/pdf);base64,([A-Za-z0-9+/=\r\n]+)$~', $archivo, $partes);
        $contenido = $valido ? base64_decode($partes[2], true) : false;
        $mime = $contenido !== false ? (new \finfo(FILEINFO_MIME_TYPE))->buffer($contenido) : false;
        if (! $contenido || strlen($contenido) > 5 * 1024 * 1024 || $mime !== ($partes[1] ?? null)) {
            throw ValidationException::withMessages(['archivo' => 'Adjunte una imagen (JPG, PNG, WEBP) o un PDF de hasta 5 MB.']);
        }

        return $mime;
    }

    private function luhn(string $numero): bool
    {
        $suma = 0;
        foreach (array_reverse(str_split($numero)) as $i => $d) {
            $d = (int) $d * ($i % 2 ? 2 : 1);
            $suma += $d > 9 ? $d - 9 : $d;
        }

        return strlen($numero) >= 13 && strlen($numero) <= 19 && $suma % 10 === 0;
    }

    private function marca(string $numero): string
    {
        return match (true) {
            str_starts_with($numero, '4') => 'Visa',
            (bool) preg_match('/^(5[1-5]|2[2-7])/', $numero) => 'Mastercard',
            (bool) preg_match('/^3[47]/', $numero) => 'American Express',
            default => 'Otra',
        };
    }
}

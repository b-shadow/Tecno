<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\CatalogoCache;
use App\Models\ComprobantePago;
use App\Models\Cuota;
use App\Models\Descuento;
use App\Models\Interes;
use App\Models\MetodoPago;
use App\Models\OrdenPago;
use App\Models\Pago;
use App\Models\Prospecto;
use App\Models\Usuario;
use App\Services\Alcance;
use App\Services\Conversion;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Illuminate\Validation\Rule;
use Illuminate\Validation\ValidationException;

/**
 * CU6 y enunciado 10: métodos de pago del prospecto, orden con pago único o plan de cuotas,
 * comprobantes, pasarela simulada con tarjeta y validación por coordinación.
 * Aprobar la 1.ª cuota dispara la conversión (matrícula) si los datos están completos (RF3.4).
 */
class PagoController extends Controller
{
    private const MARCAS = ['Visa', 'Mastercard', 'American Express'];

    public function descuentos(): JsonResponse
    {
        return response()->json(['descuentos' => Descuento::query()->where('estado', 'activo')->orderBy('nombre')->get()]);
    }

    // ---------------------------------------------------------------- métodos de pago

    public function metodos(Request $request, Prospecto $prospecto): JsonResponse
    {
        $this->autorizarProspecto($request, $prospecto);

        return response()->json(['metodos' => $prospecto->metodosPago()->orderByDesc('nro_metodo')->get(), 'marcas' => self::MARCAS]);
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

        return response()->json(['mensaje' => 'Método de pago registrado.', 'metodo' => MetodoPago::query()->create($fila)], 201);
    }

    public function cambiarEstadoMetodo(Request $request, MetodoPago $metodo): JsonResponse
    {
        $this->autorizarProspecto($request, $metodo->prospecto);
        $data = $request->validate(['estado' => ['required', Rule::in(['activo', 'inactivo'])]]);
        $metodo->update($data);

        return response()->json(['mensaje' => $data['estado'] === 'activo' ? 'Método activado.' : 'Método desactivado.', 'metodo' => $metodo]);
    }

    // ---------------------------------------------------------------- órdenes y cuotas

    public function ordenes(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $ordenes = OrdenPago::query()
            ->whereHas('interes', fn ($q) => Alcance::intereses($q, $usuario))
            ->with('interes.prospecto', 'vendedor:correo,nombre,apellido', 'items', 'descuentos.descuento', 'pago', 'cuotas.metodo')
            ->orderByDesc('nro_orden')
            ->get();

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

        $orden = DB::transaction(function () use ($interes, $usuario, $data) {
            $modulos = CatalogoCache::query()->with('programa')->whereIn('codigo', $data['modulos'])->get();
            $descuentos = Descuento::query()->whereIn('codigo', $data['descuentos'] ?? [])->get();
            $subtotal = round($modulos->sum(fn ($m) => (float) $m->precio), 2);
            $descuentoTotal = 0.0;

            $orden = OrdenPago::query()->create([
                'nro_tarjeta' => $interes->nro_tarjeta, 'vendedor_correo' => $usuario->correo,
                'subtotal' => $subtotal, 'descuento_total' => 0, 'total' => $subtotal, 'fecha_generacion' => now(),
            ]);

            foreach ($descuentos as $descuento) {
                $monto = round($subtotal * (float) $descuento->porcentaje / 100, 2);
                $descuentoTotal += $monto;
                DB::table('orden_pago_descuentos')->insert([
                    'nro_orden' => $orden->nro_orden, 'descuento_codigo' => $descuento->codigo,
                    'porcentaje' => $descuento->porcentaje, 'monto' => $monto, 'created_at' => now(), 'updated_at' => now(),
                ]);
            }
            $total = max(round($subtotal - $descuentoTotal, 2), 0);
            abort_if($total <= 0, 422, 'El total de la orden debe ser mayor a cero.');
            $orden->update(['descuento_total' => round($descuentoTotal, 2), 'total' => $total]);

            foreach ($modulos as $m) {
                $orden->items()->create([
                    'anuncio_codigo' => $m->anuncio_codigo, 'modulo_codigo' => $m->codigo, 'programa_nombre' => $m->programa->nombre,
                    'modulo_nombre' => $m->nombre, 'modulo_descripcion' => $m->descripcion, 'anuncio_titulo' => 'Inscripción abierta: '.$m->nombre,
                    'precio_acordado' => $m->precio, 'fecha' => now(),
                ]);
            }

            // Plan de pagos: cuotas mensuales iguales; la última absorbe el redondeo.
            $n = (int) $data['cuotas'];
            $base = floor($total / $n * 100) / 100;
            for ($i = 1; $i <= $n; $i++) {
                Cuota::query()->insert([
                    'nro_orden' => $orden->nro_orden, 'nro_cuota' => $i,
                    'monto' => $i === $n ? round($total - $base * ($n - 1), 2) : $base,
                    'fecha_vencimiento' => Carbon::parse($data['primer_vencimiento'])->addMonthsNoOverflow($i - 1)->toDateString(),
                    'estado' => 'Pendiente de pago', 'created_at' => now(), 'updated_at' => now(),
                ]);
            }
            Pago::query()->create(['nro_orden' => $orden->nro_orden, 'codigo_qr' => 'CRM-QR-ORD-'.$orden->nro_orden.'-'.Str::upper(Str::random(10)), 'estado' => 'Pendiente de pago']);

            $plan = $n === 1 ? 'pago único' : "plan de {$n} cuotas";
            $interes->interacciones()->create([
                'usuario_correo' => $usuario->correo, 'tipo' => 'Orden de pago enviada', 'fecha' => now(),
                'descripcion' => "Orden #{$orden->nro_orden} por {$total} Bs ({$plan}) para {$modulos->count()} módulo(s).",
                'resultado' => 'Orden pendiente de pago',
            ]);
            $interes->update(['estado' => 'Promesa de Pago', 'ultima_actividad_en' => now()]);

            return $orden;
        });

        return response()->json(['mensaje' => 'Orden de pago generada.', 'orden' => $orden->load('items', 'descuentos.descuento', 'pago', 'cuotas')], 201);
    }

    /** Cuotas para validar (coordinación): por defecto las que esperan revisión. */
    public function cuotas(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $cuotas = Cuota::query()
            ->join('ordenes_pago as o', 'o.nro_orden', '=', 'cuotas.nro_orden')
            ->join('intereses as i', 'i.nro_tarjeta', '=', 'o.nro_tarjeta')
            ->join('prospectos as p', 'p.documento', '=', 'i.documento')
            ->join('usuarios as v', 'v.correo', '=', 'o.vendedor_correo')
            ->tap(fn ($q) => Alcance::intereses($q, $usuario, 'i'))
            ->when($request->query('estado'), fn ($q, $estado) => $q->where('cuotas.estado', $estado))
            ->orderByRaw("cuotas.estado = 'En revision' desc")
            ->orderBy('cuotas.fecha_vencimiento')
            ->select('cuotas.*', 'o.total as total_orden', 'o.nro_tarjeta', 'i.programa_nombre', 'i.modulo_nombre',
                DB::raw("p.nombre || ' ' || p.apellido as prospecto"), 'p.documento', 'p.telefono',
                DB::raw("v.nombre || ' ' || v.apellido as vendedor"))
            ->get()
            ->map(function ($c) {
                $c->comprobantes = ComprobantePago::query()->where('nro_orden', $c->nro_orden)
                    ->where(fn ($q) => $q->where('nro_cuota', $c->nro_cuota)->orWhere(fn ($s) => $s->whereNull('nro_cuota')->whereRaw('? = 1', [$c->nro_cuota])))
                    ->orderByDesc('nro_comprobante')->get();

                return $c;
            });

        return response()->json(['cuotas' => $cuotas]);
    }

    /** El vendedor registra el comprobante que el prospecto le envió (imagen o PDF, hasta 5 MB). */
    public function registrarComprobante(Request $request, OrdenPago $orden, int $cuota): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        Alcance::autorizarTarjeta($usuario, $orden->interes);
        $data = $request->validate([
            'archivo' => ['required', 'string', 'max:8388608'],
            'nro_metodo' => ['nullable', Rule::exists('metodos_pago', 'nro_metodo')->where('documento', $orden->interes->documento)->where('estado', 'activo')],
            'remitente' => ['nullable', 'string', 'max:160'],
            'hora_pago' => ['nullable', 'date', 'before_or_equal:now'],
            'observacion' => ['nullable', 'string', 'max:1000'],
        ], [], ['archivo' => 'comprobante', 'nro_metodo' => 'método de pago', 'hora_pago' => 'hora del pago']);

        $mime = $this->validarArchivo($data['archivo']);

        DB::transaction(function () use ($orden, $cuota, $data, $mime, $usuario) {
            $fila = $this->cuotaBloqueada($orden->nro_orden, $cuota);
            abort_if($fila->estado === 'Pago aprobado', 422, 'Esta cuota ya está pagada.');
            abort_if($fila->estado === 'En revision', 422, 'Ya hay un comprobante en revisión para esta cuota.');

            $prospecto = $orden->interes->prospecto;
            // Clase 40: nombre legible y ligado al dato.
            $nombre = Str::slug("{$prospecto->apellido} {$prospecto->nombre}", '_')."_orden{$orden->nro_orden}_cuota{$cuota}.".($mime === 'application/pdf' ? 'pdf' : explode('/', $mime)[1]);

            ComprobantePago::query()->create([
                'nro_orden' => $orden->nro_orden, 'nro_cuota' => $cuota, 'archivo' => $data['archivo'], 'nombre_archivo' => $nombre, 'mime' => $mime,
                'remitente' => $data['remitente'] ?? null, 'hora_pago' => $data['hora_pago'] ?? null, 'observacion' => $data['observacion'] ?? null,
                'fecha_envio' => now(), 'estado_revision' => 'En revision',
            ]);
            $this->cambiarEstadoCuota($orden->nro_orden, $cuota, 'En revision', ['nro_metodo' => $data['nro_metodo'] ?? null]);
            $orden->interes->interacciones()->create([
                'usuario_correo' => $usuario->correo, 'tipo' => 'Pago informado', 'fecha' => now(),
                'descripcion' => "Comprobante de la cuota {$cuota} de la orden #{$orden->nro_orden} enviado a revisión.", 'resultado' => 'Pago en revisión',
            ]);
            $orden->interes->update(['ultima_actividad_en' => now()]);
        });

        return response()->json(['mensaje' => 'Comprobante enviado a revisión.'], 201);
    }

    /** Pasarela simulada: cobra la cuota con una tarjeta registrada y la aprueba al instante. */
    public function pagarConTarjeta(Request $request, OrdenPago $orden, int $cuota): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        Alcance::autorizarTarjeta($usuario, $orden->interes);
        $data = $request->validate([
            'nro_metodo' => ['required', Rule::exists('metodos_pago', 'nro_metodo')->where('documento', $orden->interes->documento)->where('tipo', 'Tarjeta')->where('estado', 'activo')],
        ], [], ['nro_metodo' => 'tarjeta']);

        $metodo = MetodoPago::query()->findOrFail($data['nro_metodo']);
        [$mes, $anio] = explode('/', $metodo->vencimiento);
        abort_if(Carbon::create(2000 + (int) $anio, (int) $mes)->endOfMonth()->isPast(), 422, 'La tarjeta está vencida.');

        $resultado = DB::transaction(function () use ($orden, $cuota, $metodo, $usuario) {
            $fila = $this->cuotaBloqueada($orden->nro_orden, $cuota);
            abort_if(in_array($fila->estado, ['Pago aprobado', 'En revision'], true), 422, 'Esta cuota no está pendiente de pago.');
            $transaccion = 'SIM-'.Str::upper(Str::random(12));

            $this->cambiarEstadoCuota($orden->nro_orden, $cuota, 'Pago aprobado', [
                'nro_metodo' => $metodo->nro_metodo, 'observacion' => "Pasarela simulada {$transaccion} con {$metodo->marca} ****{$metodo->ultimos_digitos}",
            ]);

            return [$transaccion, $this->trasAprobar($orden, $cuota, $usuario, "Cuota {$cuota} cobrada con {$metodo->marca} ****{$metodo->ultimos_digitos} (transacción {$transaccion}).")];
        });

        return response()->json(['mensaje' => 'Pago aprobado por la pasarela simulada.', 'transaccion' => $resultado[0], 'faltantes_conversion' => $resultado[1]]);
    }

    public function aprobar(Request $request, OrdenPago $orden, int $cuota): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        Alcance::autorizarTarjeta($usuario, $orden->interes);
        $data = $request->validate(['observacion' => ['nullable', 'string', 'max:1000']]);

        $faltantes = DB::transaction(function () use ($orden, $cuota, $data, $usuario) {
            $fila = $this->cuotaBloqueada($orden->nro_orden, $cuota);
            abort_if($fila->estado !== 'En revision', 422, 'Solo se aprueba una cuota con comprobante en revisión.');

            $this->cambiarEstadoCuota($orden->nro_orden, $cuota, 'Pago aprobado', ['observacion' => $data['observacion'] ?? null]);
            ComprobantePago::query()->where('nro_orden', $orden->nro_orden)->where('nro_cuota', $cuota)->where('estado_revision', 'En revision')->update(['estado_revision' => 'Pago aprobado', 'updated_at' => now()]);

            return $this->trasAprobar($orden, $cuota, $usuario, "Cuota {$cuota} de la orden #{$orden->nro_orden} aprobada por coordinación.");
        });

        $mensaje = $cuota === 1 && ! $faltantes ? 'Pago aprobado. El prospecto quedó matriculado (Convertido).' : 'Pago aprobado.';

        return response()->json(['mensaje' => $mensaje, 'faltantes_conversion' => $faltantes]);
    }

    public function rechazar(Request $request, OrdenPago $orden, int $cuota): JsonResponse
    {
        Alcance::autorizarTarjeta($request->attributes->get('auth_usuario'), $orden->interes);
        $data = $request->validate(['observacion' => ['required', 'string', 'max:1000']], ['observacion.required' => 'Indique el motivo del rechazo para el vendedor.']);

        DB::transaction(function () use ($orden, $cuota, $data) {
            $fila = $this->cuotaBloqueada($orden->nro_orden, $cuota);
            abort_if($fila->estado !== 'En revision', 422, 'Solo se rechaza una cuota con comprobante en revisión.');
            $this->cambiarEstadoCuota($orden->nro_orden, $cuota, 'Pago rechazado', ['observacion' => $data['observacion']]);
            ComprobantePago::query()->where('nro_orden', $orden->nro_orden)->where('nro_cuota', $cuota)->where('estado_revision', 'En revision')
                ->update(['estado_revision' => 'Pago rechazado', 'observacion' => $data['observacion'], 'updated_at' => now()]);
        });

        return response()->json(['mensaje' => 'Comprobante rechazado. El vendedor verá el motivo.']);
    }

    public function comprobante(Request $request, ComprobantePago $comprobante): JsonResponse
    {
        $orden = OrdenPago::query()->with('interes')->findOrFail($comprobante->nro_orden);
        Alcance::autorizarTarjeta($request->attributes->get('auth_usuario'), $orden->interes);

        return response()->json(['comprobante' => $comprobante->makeVisible('archivo')]);
    }

    // ---------------------------------------------------------------- apoyo

    /** Cuota 1: se cambia pagos.estado y el trigger lo copia a la cuota (así el P1 ve lo mismo). */
    private function cambiarEstadoCuota(int $nroOrden, int $cuota, string $estado, array $extra = []): void
    {
        $extra = array_filter($extra, fn ($v) => $v !== null);
        if ($cuota === 1) {
            Pago::query()->whereKey($nroOrden)->update(['estado' => $estado, 'updated_at' => now()]
                + ($estado === 'Pago aprobado' || $estado === 'Pago rechazado' ? ['fecha_validacion' => now(), 'observacion_validacion' => $extra['observacion'] ?? null] : []));
        }
        Cuota::query()->where('nro_orden', $nroOrden)->where('nro_cuota', $cuota)->update(['estado' => $estado, 'updated_at' => now()]
            + ($estado === 'Pago aprobado' ? ['fecha_pago' => now()] : []) + $extra);
    }

    /** Tras aprobar: interacción y, si es la 1.ª cuota, conversión (RF3.4). Devuelve lo que falte para convertir. */
    private function trasAprobar(OrdenPago $orden, int $cuota, Usuario $usuario, string $descripcion): array
    {
        $interes = Interes::query()->lockForUpdate()->findOrFail($orden->nro_tarjeta);
        $interes->interacciones()->create(['usuario_correo' => $usuario->correo, 'tipo' => 'Compra validada', 'descripcion' => $descripcion, 'resultado' => 'Pago aprobado', 'fecha' => now()]);

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
        $fila = DB::table('cuotas')->where('nro_orden', $nroOrden)->where('nro_cuota', $cuota)->lockForUpdate()->first();
        abort_unless($fila, 404, 'La cuota no existe.');

        return $fila;
    }

    private function autorizarProspecto(Request $request, ?Prospecto $prospecto): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_unless($prospecto && Alcance::prospectos(Prospecto::query()->whereKey($prospecto->documento), $usuario)->exists(), 403, 'Este prospecto no está dentro de su cartera.');
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

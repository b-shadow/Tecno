<?php

namespace App\Services;

use App\Exceptions\ReglaNegocioException;
use Datos\Modelos\ComprobantePago;
use Datos\Modelos\Interes;
use Datos\Modelos\MetodoPago;
use Datos\Modelos\OrdenPago;
use Datos\Modelos\Prospecto;
use Datos\Modelos\Usuario;
use Datos\Repositorios\PagoRepository;
use Illuminate\Support\Carbon;
use Illuminate\Support\Collection;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;

/**
 * CU6 y enunciado 10: métodos de pago del prospecto, orden con pago único o plan de cuotas,
 * comprobantes, pasarela simulada con tarjeta y validación por coordinación.
 * Aprobar la 1.ª cuota dispara la conversión (matrícula) si los datos están completos (RF3.4).
 */
class PagoService
{
    public const MARCAS = ['Visa', 'Mastercard', 'American Express'];

    public function __construct(private readonly PagoRepository $pagos)
    {
    }

    public function descuentos(): Collection
    {
        return $this->pagos->descuentos();
    }

    // ---------------------------------------------------------------- métodos de pago

    public function metodos(Usuario $usuario, Prospecto $prospecto): Collection
    {
        $this->autorizarProspecto($usuario, $prospecto);

        return $this->pagos->metodos($prospecto);
    }

    /** Tarjeta (Luhn y vencimiento), QR o transferencia. De la tarjeta solo se guarda marca, últimos 4 y vencimiento. */
    public function registrarMetodo(Usuario $usuario, Prospecto $prospecto, array $datos): MetodoPago
    {
        $this->autorizarProspecto($usuario, $prospecto);
        $fila = ['documento' => $prospecto->documento, 'tipo' => $datos['tipo'], 'titular' => trim($datos['titular']), 'estado' => 'activo'];

        if ($datos['tipo'] === 'Tarjeta') {
            $numero = preg_replace('/\D/', '', $datos['numero']);
            $errores = [];
            if (! $this->luhn($numero)) {
                $errores['numero'] = 'El número de tarjeta no es válido.';
            }
            if ($this->vencida($datos['vencimiento'])) {
                $errores['vencimiento'] = 'La tarjeta está vencida.';
            }
            if ($errores) {
                throw ValidationException::withMessages($errores);
            }
            // Nunca se guarda el número completo ni el CVV.
            $fila += ['marca' => $this->marca($numero), 'ultimos_digitos' => substr($numero, -4), 'vencimiento' => $datos['vencimiento']];
        }

        return $this->pagos->crearMetodo($fila);
    }

    public function cambiarEstadoMetodo(Usuario $usuario, MetodoPago $metodo, string $estado): MetodoPago
    {
        $this->autorizarProspecto($usuario, $this->pagos->metodoConProspecto($metodo)->prospecto);
        $this->pagos->actualizarMetodo($metodo, ['estado' => $estado]);

        return $metodo;
    }

    // ---------------------------------------------------------------- órdenes y cuotas

    public function ordenes(Usuario $usuario): Collection
    {
        return $this->pagos->ordenes($usuario);
    }

    /** Orden de pago: pago único (1 cuota) o plan de 2 a 12 cuotas mensuales. La genera el vendedor de la tarjeta. */
    public function crearOrden(Usuario $usuario, Interes $interes, array $datos): OrdenPago
    {
        ReglaNegocioException::si($interes->vendedor_correo !== $usuario->correo, 'Solo el vendedor asignado genera la orden de pago.', 403);
        ReglaNegocioException::si(in_array($interes->estado, ['Convertido', 'Perdido'], true), 'La tarjeta ya está cerrada.');

        $orden = $this->pagos->transaccion(function () use ($interes, $usuario, $datos) {
            // Igual que el P1: una sola orden abierta por tarjeta (evita la venta duplicada).
            $abierta = $this->pagos->ordenAbierta($interes->nro_tarjeta);
            ReglaNegocioException::si((bool) $abierta, $abierta
                ? "La tarjeta ya tiene la orden #{$abierta->nro_orden} ({$abierta->estado}). Registre su comprobante o espere su revisión."
                : '');

            $modulos = $this->pagos->modulos($datos['modulos']);
            $descuentos = $this->pagos->descuentosPorCodigo($datos['descuentos'] ?? []);
            $subtotal = round($modulos->sum(fn ($m) => (float) $m->precio), 2);
            $descuentoTotal = 0.0;

            $orden = $this->pagos->crearOrden([
                'nro_tarjeta' => $interes->nro_tarjeta, 'vendedor_correo' => $usuario->correo,
                'subtotal' => $subtotal, 'descuento_total' => 0, 'total' => $subtotal, 'fecha_generacion' => now(),
            ]);

            $filasDescuento = [];
            foreach ($descuentos as $descuento) {
                $monto = round($subtotal * (float) $descuento->porcentaje / 100, 2);
                $descuentoTotal += $monto;
                $filasDescuento[] = [
                    'nro_orden' => $orden->nro_orden, 'descuento_codigo' => $descuento->codigo,
                    'porcentaje' => $descuento->porcentaje, 'monto' => $monto, 'created_at' => now(), 'updated_at' => now(),
                ];
            }
            $this->pagos->insertarDescuentosOrden($filasDescuento);
            $total = max(round($subtotal - $descuentoTotal, 2), 0);
            ReglaNegocioException::si($total <= 0, 'El total de la orden debe ser mayor a cero.');
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
            $n = (int) $datos['cuotas'];
            $base = floor($total / $n * 100) / 100;
            $filasCuota = [];
            for ($i = 1; $i <= $n; $i++) {
                $filasCuota[] = [
                    'nro_orden' => $orden->nro_orden, 'nro_cuota' => $i,
                    'monto' => $i === $n ? round($total - $base * ($n - 1), 2) : $base,
                    'fecha_vencimiento' => Carbon::parse($datos['primer_vencimiento'])->addMonthsNoOverflow($i - 1)->toDateString(),
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

        return $this->pagos->ordenCompleta($orden);
    }

    /** Cuotas para validar (coordinación): por defecto las que esperan revisión. */
    public function cuotas(Usuario $usuario, ?string $estado): Collection
    {
        return $this->pagos->cuotas($usuario, $estado);
    }

    /** El vendedor registra el comprobante que el prospecto le envió (imagen o PDF, hasta 5 MB). */
    public function registrarComprobante(Usuario $usuario, OrdenPago $orden, int $cuota, array $datos): void
    {
        $interes = $this->pagos->interesDeOrden($orden);
        AlcanceService::autorizarTarjeta($usuario, $interes);
        if (! empty($datos['nro_metodo'])) {
            $this->metodoActivo($interes->documento, (int) $datos['nro_metodo'], null, 'El método de pago seleccionado no es válido.');
        }
        $mime = $this->validarArchivo($datos['archivo']);

        $this->pagos->transaccion(function () use ($orden, $interes, $cuota, $datos, $mime, $usuario) {
            $fila = $this->cuotaBloqueada($orden->nro_orden, $cuota);
            ReglaNegocioException::si($fila->estado === 'Pago aprobado', 'Esta cuota ya está pagada.');
            ReglaNegocioException::si($fila->estado === 'En revision', 'Ya hay un comprobante en revisión para esta cuota.');

            $prospecto = $interes->prospecto;
            // Clase 40: nombre legible y ligado al dato.
            $nombre = Str::slug("{$prospecto->apellido} {$prospecto->nombre}", '_')."_orden{$orden->nro_orden}_cuota{$cuota}.".($mime === 'application/pdf' ? 'pdf' : explode('/', $mime)[1]);

            $this->pagos->crearComprobante([
                'nro_orden' => $orden->nro_orden, 'nro_cuota' => $cuota, 'archivo' => $datos['archivo'], 'nombre_archivo' => $nombre, 'mime' => $mime,
                'remitente' => $datos['remitente'] ?? null, 'hora_pago' => $datos['hora_pago'] ?? null, 'observacion' => $datos['observacion'] ?? null,
                'fecha_envio' => now(), 'estado_revision' => 'En revision',
            ]);
            $this->pagos->cambiarEstadoCuota($orden->nro_orden, $cuota, 'En revision', ['nro_metodo' => $datos['nro_metodo'] ?? null]);
            $this->pagos->registrarInteraccion($interes, [
                'usuario_correo' => $usuario->correo, 'tipo' => 'Pago informado', 'fecha' => now(),
                'descripcion' => "Comprobante de la cuota {$cuota} de la orden #{$orden->nro_orden} enviado a revisión.", 'resultado' => 'Pago en revisión',
            ]);
            $this->pagos->actualizarInteres($interes, ['ultima_actividad_en' => now()]);
        });
    }

    /**
     * Pasarela simulada: cobra la cuota con una tarjeta registrada del prospecto y la deja En revisión.
     * El vendedor no aprueba su propia venta: coordinación la valida (aprobar) y recién ahí se matricula.
     * Devuelve el código de la transacción simulada.
     */
    public function pagarConTarjeta(Usuario $usuario, OrdenPago $orden, int $cuota, int $nroMetodo): string
    {
        $interes = $this->pagos->interesDeOrden($orden);
        AlcanceService::autorizarTarjeta($usuario, $interes);
        $metodo = $this->metodoActivo($interes->documento, $nroMetodo, 'Tarjeta', 'Seleccione una tarjeta activa del prospecto.');
        ReglaNegocioException::si($this->vencida($metodo->vencimiento), 'La tarjeta está vencida.');

        return $this->pagos->transaccion(function () use ($orden, $interes, $cuota, $metodo, $usuario) {
            $fila = $this->cuotaBloqueada($orden->nro_orden, $cuota);
            ReglaNegocioException::si(in_array($fila->estado, ['Pago aprobado', 'En revision'], true), 'Esta cuota no está pendiente de pago.');
            $transaccion = 'SIM-'.Str::upper(Str::random(12));
            $tarjeta = "{$metodo->marca} ****{$metodo->ultimos_digitos}";

            $this->pagos->cambiarEstadoCuota($orden->nro_orden, $cuota, 'En revision', [
                'nro_metodo' => $metodo->nro_metodo, 'observacion' => "Pasarela simulada {$transaccion} con {$tarjeta}",
            ]);
            $this->pagos->registrarInteraccion($interes, [
                'usuario_correo' => $usuario->correo, 'tipo' => 'Pago informado', 'fecha' => now(),
                'descripcion' => "Cuota {$cuota} cobrada con {$tarjeta} (transacción {$transaccion}); pendiente de validación.",
                'resultado' => 'Pago en revisión',
            ]);
            $this->pagos->actualizarInteres($interes, ['ultima_actividad_en' => now()]);

            return $transaccion;
        });
    }

    /** Coordinación aprueba una cuota En revisión. Devuelve lo que falte para la conversión (vacío si se matriculó). */
    public function aprobar(Usuario $usuario, OrdenPago $orden, int $cuota, ?string $observacion): array
    {
        AlcanceService::autorizarTarjeta($usuario, $this->pagos->interesDeOrden($orden));

        return $this->pagos->transaccion(function () use ($orden, $cuota, $observacion, $usuario) {
            $fila = $this->cuotaBloqueada($orden->nro_orden, $cuota);
            ReglaNegocioException::si($fila->estado !== 'En revision', 'Solo se aprueba una cuota en revisión.');

            $this->pagos->cambiarEstadoCuota($orden->nro_orden, $cuota, 'Pago aprobado', ['observacion' => $observacion]);
            $this->pagos->actualizarComprobantes($orden->nro_orden, $cuota, 'Pago aprobado');

            return $this->trasAprobar($orden, $cuota, $usuario, "Cuota {$cuota} de la orden #{$orden->nro_orden} aprobada por coordinación.");
        });
    }

    public function rechazar(Usuario $usuario, OrdenPago $orden, int $cuota, string $observacion): void
    {
        AlcanceService::autorizarTarjeta($usuario, $this->pagos->interesDeOrden($orden));

        $this->pagos->transaccion(function () use ($orden, $cuota, $observacion) {
            $fila = $this->cuotaBloqueada($orden->nro_orden, $cuota);
            ReglaNegocioException::si($fila->estado !== 'En revision', 'Solo se rechaza una cuota en revisión.');
            $this->pagos->cambiarEstadoCuota($orden->nro_orden, $cuota, 'Pago rechazado', ['observacion' => $observacion]);
            $this->pagos->actualizarComprobantes($orden->nro_orden, $cuota, 'Pago rechazado', $observacion);
        });
    }

    public function comprobante(Usuario $usuario, ComprobantePago $comprobante): ComprobantePago
    {
        AlcanceService::autorizarTarjeta($usuario, $this->pagos->ordenDeComprobante($comprobante->nro_orden)->interes);

        return $comprobante->makeVisible('archivo');
    }

    // ---------------------------------------------------------------- apoyo

    /** Tras aprobar: interacción y, si es la 1.ª cuota, conversión (RF3.4). Devuelve lo que falte para convertir. */
    private function trasAprobar(OrdenPago $orden, int $cuota, Usuario $usuario, string $descripcion): array
    {
        $interes = $this->pagos->interesBloqueado($orden->nro_tarjeta);
        $this->pagos->registrarInteraccion($interes, ['usuario_correo' => $usuario->correo, 'tipo' => 'Compra validada', 'descripcion' => $descripcion, 'resultado' => 'Pago aprobado', 'fecha' => now()]);

        if ($cuota !== 1 || $interes->estado === 'Convertido') {
            return [];
        }
        $faltan = ConversionService::faltantes($interes);
        if (! $faltan) {
            ConversionService::procesar($interes, $usuario);
        }

        return $faltan;
    }

    private function cuotaBloqueada(int $nroOrden, int $cuota): object
    {
        $fila = $this->pagos->cuotaBloqueada($nroOrden, $cuota);
        ReglaNegocioException::si(! $fila, 'La cuota no existe.', 404);

        return $fila;
    }

    private function metodoActivo(string $documento, int $numero, ?string $tipo, string $mensaje): MetodoPago
    {
        return $this->pagos->metodoActivo($documento, $numero, $tipo)
            ?? throw ValidationException::withMessages(['nro_metodo' => $mensaje]);
    }

    private function autorizarProspecto(Usuario $usuario, ?Prospecto $prospecto): void
    {
        ReglaNegocioException::si(! $prospecto || ! $this->pagos->prospectoEnCartera($prospecto, $usuario), 'Este prospecto no está dentro de su cartera.', 403);
    }

    private function vencida(string $vencimiento): bool
    {
        [$mes, $anio] = explode('/', $vencimiento);

        return Carbon::create(2000 + (int) $anio, (int) $mes)->endOfMonth()->isPast();
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

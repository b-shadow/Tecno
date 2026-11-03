<?php

namespace App\Negocio;

use App\Exceptions\ReglaNegocioException;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Pago\AnularOrdenRequest;
use App\Http\Requests\Pago\AprobarCuotaRequest;
use App\Http\Requests\Pago\CambiarEstadoMetodoRequest;
use App\Http\Requests\Pago\CrearCheckoutRequest;
use App\Http\Requests\Pago\CrearOrdenRequest;
use App\Http\Requests\Pago\CrearSetupTarjetaRequest;
use App\Http\Requests\Pago\RechazarCuotaRequest;
use App\Http\Requests\Pago\RegistrarComprobanteRequest;
use App\Http\Requests\Pago\RegistrarMetodoRequest;
use Datos\DPago;
use Datos\Modelos\MetodoPago;
use Datos\Modelos\OrdenPago;
use Datos\Modelos\Prospecto;
use Datos\Modelos\Usuario;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;

/**
 * Capa de negocio — CU6 y enunciado 10: métodos de pago del prospecto (Stripe Setup, QR, transferencia),
 * órdenes con pago único o plan de cuotas, anulación controlada, comprobantes y Stripe Checkout Sandbox.
 * Aprobar la 1.ª cuota (por Stripe o validación manual de comprobante) dispara la matrícula si los datos están completos (RF3.4).
 */
class NPago
{
    public const MARCAS = ['Visa', 'Mastercard', 'American Express'];

    public function __construct(
        private readonly DPago $pagos,
        private readonly NStripe $stripe,
    ) {
    }

    public function descuentos(): JsonResponse
    {
        return response()->json(['descuentos' => $this->pagos->descuentos()]);
    }

    // ---------------------------------------------------------------- métodos de pago

    public function metodos(ConsultaRequest $r, string $prospecto): JsonResponse
    {
        $registro = $this->pagos->prospecto($prospecto);
        $this->autorizarProspecto($r->usuario(), $registro);

        return response()->json(['metodos' => $this->pagos->metodos($registro), 'marcas' => self::MARCAS]);
    }

    /** Registro manual únicamente para QR o transferencia; las tarjetas se registran mediante Stripe Checkout (mode=setup). */
    public function registrarMetodo(RegistrarMetodoRequest $r, string $prospecto): JsonResponse
    {
        $datos = $r->validated();
        $registro = $this->pagos->prospecto($prospecto);
        $this->autorizarProspecto($r->usuario(), $registro);
        $fila = [
            'documento' => $registro->documento,
            'tipo' => $datos['tipo'],
            'titular' => trim($datos['titular']),
            'estado' => 'activo',
            'proveedor' => 'manual',
            'registrado_por' => $r->usuario()->correo,
        ];

        return response()->json(['mensaje' => 'Método de pago registrado.', 'metodo' => $this->pagos->crearMetodo($fila)], 201);
    }

    public function crearSetupTarjeta(CrearSetupTarjetaRequest $r, string $prospecto): JsonResponse
    {
        $sesion = $this->stripe->iniciarSetupTarjeta(
            $prospecto,
            $r->usuario(),
            $r->validated('nro_tarjeta') ? (int) $r->validated('nro_tarjeta') : null
        );

        return response()->json($sesion, 201);
    }

    public function cambiarEstadoMetodo(CambiarEstadoMetodoRequest $r, int $metodo): JsonResponse
    {
        $estado = $r->validated('estado');
        $registro = $this->pagos->metodo($metodo);
        $this->autorizarProspecto($r->usuario(), $this->pagos->metodoConProspecto($registro)->prospecto);
        $this->pagos->actualizarMetodo($registro, ['estado' => $estado]);

        return response()->json(['mensaje' => $estado === 'activo' ? 'Método activado.' : 'Método desactivado.', 'metodo' => $registro]);
    }

    // ---------------------------------------------------------------- órdenes y cuotas

    public function ordenes(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['ordenes' => $this->pagos->ordenes($r->usuario())]);
    }

    /** Orden de pago: pago único (1 cuota) o plan de 2 a 12 cuotas mensuales. La genera el vendedor de la tarjeta. */
    public function crearOrden(CrearOrdenRequest $r, int $interes): JsonResponse
    {
        $usuario = $r->usuario();
        $datos = $r->validated();
        $tarjeta = $this->pagos->interes($interes);
        ReglaNegocioException::si($tarjeta->vendedor_correo !== $usuario->correo, 'Solo el vendedor asignado genera la orden de pago.', 403);
        ReglaNegocioException::si(in_array($tarjeta->estado, ['Convertido', 'Perdido'], true), 'La tarjeta ya está cerrada.');

        $orden = $this->pagos->transaccion(function () use ($tarjeta, $usuario, $datos) {
            // Igual que el P1: una sola orden abierta por tarjeta (evita la venta duplicada).
            $abierta = $this->pagos->ordenAbierta($tarjeta->nro_tarjeta);
            ReglaNegocioException::si((bool) $abierta, $abierta
                ? "La tarjeta ya tiene la orden #{$abierta->nro_orden} ({$abierta->estado}). Registre su comprobante o espere su revisión."
                : '');

            $modulos = $this->pagos->modulos($datos['modulos']);
            $descuentos = $this->pagos->descuentosPorCodigo($datos['descuentos'] ?? []);
            $subtotal = round($modulos->sum(fn ($m) => (float) $m->precio), 2);
            $descuentoTotal = 0.0;

            $orden = $this->pagos->crearOrden([
                'nro_tarjeta' => $tarjeta->nro_tarjeta, 'vendedor_correo' => $usuario->correo,
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
            $this->pagos->registrarInteraccion($tarjeta, [
                'usuario_correo' => $usuario->correo, 'tipo' => 'Orden de pago enviada', 'fecha' => now(),
                'descripcion' => "Orden #{$orden->nro_orden} por {$total} Bs ({$plan}) para {$modulos->count()} módulo(s).",
                'resultado' => 'Orden pendiente de pago',
            ]);
            $this->pagos->actualizarInteres($tarjeta, ['estado' => 'Promesa de Pago', 'ultima_actividad_en' => now()]);

            return $orden;
        });

        return response()->json(['mensaje' => 'Orden de pago generada.', 'orden' => $this->pagos->ordenCompleta($orden)], 201);
    }

    /** Cuotas para validar (coordinación): por defecto las que esperan revisión. */
    public function cuotas(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['cuotas' => $this->pagos->cuotas($r->usuario(), $r->query('estado'))]);
    }

    /** El vendedor registra el comprobante manual (QR/transferencia) que el prospecto le envió (imagen o PDF, hasta 5 MB). */
    public function registrarComprobante(RegistrarComprobanteRequest $r, int $orden, int $cuota): JsonResponse
    {
        $usuario = $r->usuario();
        $datos = $r->validated();
        $registro = $this->pagos->orden($orden);
        ReglaNegocioException::si($registro->estado !== 'Activa', 'La orden fue anulada.');
        $interes = $this->pagos->interesDeOrden($registro);
        NAlcance::autorizarTarjeta($usuario, $interes);
        if (! empty($datos['nro_metodo'])) {
            $this->metodoActivo($interes->documento, (int) $datos['nro_metodo'], null, 'El método de pago seleccionado no es válido.');
        }
        $mime = $this->validarArchivo($datos['archivo']);

        $this->pagos->transaccion(function () use ($registro, $interes, $cuota, $datos, $mime, $usuario) {
            $fila = $this->cuotaBloqueada($registro->nro_orden, $cuota);
            ReglaNegocioException::si($fila->estado === 'Pago aprobado', 'Esta cuota ya está pagada.');
            ReglaNegocioException::si($fila->estado === 'En revision', 'Ya hay un comprobante en revisión para esta cuota.');

            $prospecto = $interes->prospecto;
            // Clase 40: nombre legible y ligado al dato.
            $nombre = Str::slug("{$prospecto->apellido} {$prospecto->nombre}", '_')."_orden{$registro->nro_orden}_cuota{$cuota}.".($mime === 'application/pdf' ? 'pdf' : explode('/', $mime)[1]);

            $this->pagos->crearComprobante([
                'nro_orden' => $registro->nro_orden, 'nro_cuota' => $cuota, 'archivo' => $datos['archivo'], 'nombre_archivo' => $nombre, 'mime' => $mime,
                'remitente' => $datos['remitente'] ?? null, 'hora_pago' => $datos['hora_pago'] ?? null, 'observacion' => $datos['observacion'] ?? null,
                'fecha_envio' => now(), 'estado_revision' => 'En revision',
            ]);
            $this->pagos->cambiarEstadoCuota($registro->nro_orden, $cuota, 'En revision', ['nro_metodo' => $datos['nro_metodo'] ?? null]);
            $this->pagos->registrarInteraccion($interes, [
                'usuario_correo' => $usuario->correo, 'tipo' => 'Pago informado', 'fecha' => now(),
                'descripcion' => "Comprobante de la cuota {$cuota} de la orden #{$registro->nro_orden} enviado a revisión.", 'resultado' => 'Pago en revisión',
            ]);
            $this->pagos->actualizarInteres($interes, ['ultima_actividad_en' => now()]);
        });

        return response()->json(['mensaje' => 'Comprobante enviado a revisión.'], 201);
    }

    /** Inicia una sesión oficial de Stripe Checkout (moneda BOB) para pagar una cuota pendiente. */
    public function crearCheckout(CrearCheckoutRequest $r, int $orden, int $cuota): JsonResponse
    {
        $r->validated();
        $resultado = $this->stripe->iniciarCheckoutCuota($orden, $cuota, $r->usuario());

        return response()->json($resultado, 201);
    }

    /** Consulta y confirma de manera idempotente una Checkout Session real en Stripe Sandbox. */
    public function confirmarCheckout(ConsultaRequest $r, string $sessionId): JsonResponse
    {
        return response()->json($this->stripe->verificarSesion($sessionId, $r->usuario()));
    }

    /** Gestiona el retorno desde Stripe Checkout cuando el usuario cancela o abandona el flujo. */
    public function cancelarCheckout(ConsultaRequest $r, string $sessionId): JsonResponse
    {
        return response()->json($this->stripe->cancelarSesion($sessionId, $r->usuario()));
    }

    /** Anula una orden sin pagos confirmados ni en revisión, expirando sesiones Stripe pendientes. */
    public function anularOrden(AnularOrdenRequest $r, int $orden): JsonResponse
    {
        $anulada = $this->stripe->anularOrden($orden, $r->usuario(), (string) $r->validated('motivo'));

        return response()->json(['mensaje' => "Orden #{$anulada->nro_orden} anulada.", 'orden' => $anulada]);
    }

    /** Webhook oficial de Stripe: verifica la firma HMAC y concilia pagos/eventos en modo Sandbox. */
    public function webhook(Request $r): JsonResponse
    {
        $resultado = $this->stripe->procesarWebhook((string) $r->getContent(), (string) $r->header('Stripe-Signature', ''));

        return response()->json($resultado);
    }

    /** Coordinación aprueba un comprobante manual En revisión; si es la 1.ª cuota y los datos están completos, se matricula. */
    public function aprobar(AprobarCuotaRequest $r, int $orden, int $cuota): JsonResponse
    {
        $usuario = $r->usuario();
        $observacion = $r->validated('observacion');
        $registro = $this->pagos->orden($orden);
        ReglaNegocioException::si($registro->estado !== 'Activa', 'La orden fue anulada.');
        NAlcance::autorizarTarjeta($usuario, $this->pagos->interesDeOrden($registro));

        $faltantes = $this->pagos->transaccion(function () use ($registro, $cuota, $observacion, $usuario) {
            $fila = $this->cuotaBloqueada($registro->nro_orden, $cuota);
            ReglaNegocioException::si(($fila->proveedor ?? 'manual') === 'stripe', 'Las cuotas procesadas por Stripe solo se confirman mediante la pasarela oficial.', 422);
            ReglaNegocioException::si($fila->estado !== 'En revision', 'Solo se aprueba una cuota en revisión.');

            $this->pagos->cambiarEstadoCuota($registro->nro_orden, $cuota, 'Pago aprobado', ['observacion' => $observacion]);
            $this->pagos->actualizarComprobantes($registro->nro_orden, $cuota, 'Pago aprobado');

            return $this->trasAprobar($registro, $cuota, $usuario, "Cuota {$cuota} de la orden #{$registro->nro_orden} aprobada por coordinación.");
        });
        $mensaje = $cuota === 1 && ! $faltantes ? 'Pago aprobado. El prospecto quedó matriculado (Convertido).' : 'Pago aprobado.';

        return response()->json(['mensaje' => $mensaje, 'faltantes_conversion' => $faltantes]);
    }

    public function rechazar(RechazarCuotaRequest $r, int $orden, int $cuota): JsonResponse
    {
        $observacion = $r->validated('observacion');
        $registro = $this->pagos->orden($orden);
        ReglaNegocioException::si($registro->estado !== 'Activa', 'La orden fue anulada.');
        NAlcance::autorizarTarjeta($r->usuario(), $this->pagos->interesDeOrden($registro));

        $this->pagos->transaccion(function () use ($registro, $cuota, $observacion) {
            $fila = $this->cuotaBloqueada($registro->nro_orden, $cuota);
            ReglaNegocioException::si(($fila->proveedor ?? 'manual') === 'stripe', 'Las cuotas procesadas por Stripe reflejan directamente el resultado de la pasarela.');
            ReglaNegocioException::si($fila->estado !== 'En revision', 'Solo se rechaza una cuota en revisión.');
            $this->pagos->cambiarEstadoCuota($registro->nro_orden, $cuota, 'Pago rechazado', ['observacion' => $observacion]);
            $this->pagos->actualizarComprobantes($registro->nro_orden, $cuota, 'Pago rechazado', $observacion);
        });

        return response()->json(['mensaje' => 'Comprobante rechazado. El vendedor verá el motivo.']);
    }

    public function comprobante(ConsultaRequest $r, int $comprobante): JsonResponse
    {
        $registro = $this->pagos->comprobante($comprobante);
        NAlcance::autorizarTarjeta($r->usuario(), $this->pagos->ordenDeComprobante($registro->nro_orden)->interes);

        return response()->json(['comprobante' => $registro->makeVisible('archivo')]);
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
        $faltan = NConversion::faltantes($interes);
        if (! $faltan) {
            NConversion::procesar($interes, $usuario);
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
}

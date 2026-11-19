<?php

namespace App\Negocio;

use App\Exceptions\ReglaNegocioException;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Pago\AnularOrdenRequest;
use App\Http\Requests\Pago\AprobarCuotaRequest;
use App\Http\Requests\Pago\CambiarEstadoMetodoRequest;
use App\Http\Requests\Pago\ConfigurarEnvioOrdenRequest;
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
        private readonly NNotificacion $notificaciones,
    ) {
    }

    /**
     * Cambia el estado de una cuota. La 1.ª cuota además fija el estado del Pago de la orden (modelo del P1: el Pago
     * es la 1.ª cuota) y, al validarse, su fecha y observación. Lo usan el flujo manual y el de Stripe.
     */
    public static function estadoCuota(DPago $pagos, int $orden, int $numero, string $estado, array $cuota = [], ?string $observacionPago = null): void
    {
        if ($numero === 1) {
            $validado = in_array($estado, ['Pago aprobado', 'Pago rechazado'], true);
            $pagos->actualizarPago($orden, ['estado' => $estado]
                + ($validado ? ['fecha_validacion' => now(), 'observacion_validacion' => $observacionPago] : []));
        }
        $pagos->actualizarCuota($orden, $numero, ['estado' => $estado] + ($estado === 'Pago aprobado' ? ['fecha_pago' => now()] : []) + $cuota);
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

    /** Los nuevos métodos de pago se registran únicamente mediante Stripe Setup; se prohíbe crear QR/transferencia manual. */
    public function registrarMetodo(RegistrarMetodoRequest $r, string $prospecto): JsonResponse
    {
        $r->validated();
        $registro = $this->pagos->prospecto($prospecto);
        $this->autorizarProspecto($r->usuario(), $registro);

        throw new ReglaNegocioException(
            'Los cobros actuales utilizan exclusivamente Stripe Sandbox. Utilice «Solicitar registro de tarjeta» o genere el enlace de pago.',
            422
        );
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

    /** Orden de pago: pago único (1 cuota) o plan de 2 a 12 cuotas mensuales. Valida descuentos y programación automática. */
    public function crearOrden(CrearOrdenRequest $r, int $interes): JsonResponse
    {
        $usuario = $r->usuario();
        $datos = $r->validated();
        $tarjeta = $this->pagos->interes($interes);
        ReglaNegocioException::si($tarjeta->vendedor_correo !== $usuario->correo, 'Solo el vendedor asignado genera la orden de pago.', 403);
        ReglaNegocioException::si(in_array($tarjeta->estado, ['Convertido', 'Perdido'], true), 'La tarjeta ya está cerrada.');

        $correoProspecto = trim((string) ($tarjeta->prospecto?->correo ?? ''));
        $tieneCorreoValido = $correoProspecto !== '' && filter_var($correoProspecto, FILTER_VALIDATE_EMAIL) !== false;
        if (array_key_exists('envio_automatico', $datos) && $datos['envio_automatico'] === true && ! $tieneCorreoValido) {
            throw ValidationException::withMessages([
                'envio_automatico' => 'Registre un correo electrónico válido en el prospecto para habilitar los envíos automáticos.',
            ]);
        }
        $envioAutomatico = array_key_exists('envio_automatico', $datos) ? (bool) $datos['envio_automatico'] : $tieneCorreoValido;

        [$orden, $filasCuota] = $this->pagos->transaccion(function () use ($tarjeta, $usuario, $datos, $envioAutomatico) {
            // Igual que el P1: una sola orden abierta por tarjeta (evita la venta duplicada). El bloqueo de la tarjeta
            // hace esperar a un segundo pedido simultáneo hasta que este confirme, y entonces ve la orden abierta.
            $this->pagos->interesBloqueado($tarjeta->nro_tarjeta);
            $abierta = $this->pagos->ordenAbierta($tarjeta->nro_tarjeta);
            ReglaNegocioException::si((bool) $abierta, $abierta
                ? "La tarjeta ya tiene la orden #{$abierta->nro_orden} ({$abierta->estado}). Complete o anule la orden abierta antes de crear otra."
                : '');

            $modulos = $this->pagos->modulos($datos['modulos']);
            $descuentos = $this->pagos->descuentosPorCodigo($datos['descuentos'] ?? []);
            $this->validarReglasDescuentos($descuentos, $modulos);

            $subtotal = round($modulos->sum(fn ($m) => (float) $m->precio), 2);
            $descuentoTotal = 0.0;
            $filasDescuento = [];
            foreach ($descuentos as $descuento) {
                $monto = round($subtotal * (float) $descuento->porcentaje / 100, 2);
                $descuentoTotal += $monto;
                $filasDescuento[] = [
                    'descuento_codigo' => $descuento->codigo,
                    'porcentaje' => $descuento->porcentaje, 'monto' => $monto, 'created_at' => now(), 'updated_at' => now(),
                ];
            }
            $total = max(round($subtotal - $descuentoTotal, 2), 0);
            ReglaNegocioException::si($total <= 0, 'El total de la orden debe ser mayor a cero.');

            $orden = $this->pagos->crearOrden([
                'nro_tarjeta' => $tarjeta->nro_tarjeta, 'vendedor_correo' => $usuario->correo,
                'subtotal' => $subtotal, 'descuento_total' => round($descuentoTotal, 2), 'total' => $total,
                'envio_automatico' => $envioAutomatico, 'fecha_generacion' => now(),
            ]);

            if ($filasDescuento) {
                $this->pagos->insertarDescuentosOrden(array_map(fn ($f) => ['nro_orden' => $orden->nro_orden] + $f, $filasDescuento));
            }

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
                    'token_pago' => bin2hex(random_bytes(24)),
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

            return [$orden, $filasCuota];
        });

        $avisoCorreo = null;
        if ($envioAutomatico && config('pagos_recordatorios.enviar_al_crear_orden', true)) {
            $avisoCorreo = $this->enviarSolicitudInicialOrden($orden, $tarjeta, $filasCuota, $usuario->correo);
        }

        return response()->json([
            'mensaje' => 'Orden de pago generada.',
            'aviso_correo' => $avisoCorreo,
            'orden' => $this->pagos->ordenCompleta($orden),
        ], 201);
    }

    /** Activa o desactiva el envío automático de recordatorios para una orden activa. */
    public function configurarEnvioAutomatico(ConfigurarEnvioOrdenRequest $r, int $orden): JsonResponse
    {
        $registro = $this->pagos->orden($orden);
        ReglaNegocioException::si($registro->estado !== 'Activa', 'No se puede modificar una orden anulada.');
        $interes = $this->pagos->interesDeOrden($registro);
        NAlcance::autorizarTarjeta($r->usuario(), $interes);

        $activar = (bool) $r->validated('envio_automatico');
        if ($activar && ! filter_var((string) ($interes->prospecto?->correo ?? ''), FILTER_VALIDATE_EMAIL)) {
            throw ValidationException::withMessages([
                'envio_automatico' => 'El prospecto no tiene un correo electrónico válido para habilitar los envíos automáticos.',
            ]);
        }

        $this->pagos->actualizarOrden($registro, ['envio_automatico' => $activar]);

        return response()->json([
            'mensaje' => $activar ? 'Envíos automáticos activados.' : 'Envíos automáticos desactivados.',
            'orden' => $this->pagos->ordenCompleta($registro),
        ]);
    }

    /** Cuotas para validar (coordinación): conserva la resolución de comprobantes históricos pendientes. */
    public function cuotas(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['cuotas' => $this->pagos->cuotas($r->usuario(), $r->query('estado'))]);
    }

    /** Bloquea la carga de nuevos comprobantes QR/transferencia para exigir Stripe Checkout como pasarela única. */
    public function registrarComprobante(RegistrarComprobanteRequest $r, int $orden, int $cuota): JsonResponse
    {
        $r->validated();
        $registro = $this->pagos->orden($orden);
        NAlcance::autorizarTarjeta($r->usuario(), $this->pagos->interesDeOrden($registro));

        throw new ReglaNegocioException(
            'Los pagos de órdenes activas se realizan exclusivamente mediante Stripe Checkout Sandbox; no se admiten comprobantes manuales nuevos.',
            422
        );
    }

    /** Inicia una sesión oficial de Stripe Checkout (moneda BOB) para pagar una cuota pendiente. */
    public function crearCheckout(CrearCheckoutRequest $r, int $orden, int $cuota): JsonResponse
    {
        $r->validated();
        $resultado = $this->stripe->iniciarCheckoutCuota($orden, $cuota, $r->usuario());

        return response()->json($resultado, 201);
    }

    /** Consulta y confirma de manera idempotente una Checkout Session real en Stripe Sandbox (vendedor/coordinación autenticados). */
    public function confirmarCheckout(ConsultaRequest $r, string $sessionId): JsonResponse
    {
        return response()->json($this->stripe->verificarSesion($sessionId, $r->usuario()));
    }

    /** Gestiona el retorno desde Stripe Checkout cuando un usuario autenticado cancela o abandona el flujo. */
    public function cancelarCheckout(ConsultaRequest $r, string $sessionId): JsonResponse
    {
        return response()->json($this->stripe->cancelarSesion($sessionId, $r->usuario()));
    }

    /** Retorno público seguro para el cliente después de pagar en Stripe Checkout (autorizado por token único). */
    public function consultarRetornoPublico(ConsultaRequest $r, string $sessionId): JsonResponse
    {
        $token = trim((string) $r->query('token', ''));
        ReglaNegocioException::si($token === '', 'Falta el token de verificación del enlace.', 400);

        return response()->json($this->stripe->verificarRetornoPublico($sessionId, $token));
    }

    /** Retorno público seguro cuando el cliente cancela en Stripe Checkout (mantiene la orden activa para continuar). */
    public function cancelarRetornoPublico(ConsultaRequest $r, string $sessionId): JsonResponse
    {
        $token = trim((string) ($r->input('token') ?: $r->query('token', '')));
        ReglaNegocioException::si($token === '', 'Falta el token de verificación del enlace.', 400);

        return response()->json($this->stripe->cancelarRetornoPublico($sessionId, $token));
    }

    /** Enlace público seguro por cuota: verifica estado en BD y recupera o genera una sesión Stripe vigente. */
    public function abrirEnlaceCuotaPublico(ConsultaRequest $r, string $token): JsonResponse
    {
        return response()->json($this->stripe->resolverEnlacePublicoCuota($token));
    }

    /** Ejecutado por Laravel Scheduler: evalúa cuotas pendientes con envío automático habilitado y envía recordatorios sin duplicados. */
    public function procesarEnviosAutomaticos(?Carbon $fechaReferencia = null): array
    {
        $tz = (string) config('pagos_recordatorios.zona_horaria', 'America/La_Paz');
        $hoy = ($fechaReferencia ? $fechaReferencia->copy()->timezone($tz) : now($tz))->startOfDay();
        $diasAntes = max((int) config('pagos_recordatorios.dias_antes_vencimiento', 3), 0);
        $enviarDia = (bool) config('pagos_recordatorios.enviar_dia_vencimiento', true);
        $diasDespues = max((int) config('pagos_recordatorios.dias_despues_vencimiento', 3), 0);
        $frontend = rtrim((string) config('services.frontend.url', 'http://localhost:5173'), '/');

        $cuotas = $this->pagos->cuotasPendientesParaRecordatorio();
        $enviados = 0;
        $fallidos = 0;
        $omitidos = 0;

        foreach ($cuotas as $c) {
            $correo = trim((string) ($c->prospecto_correo ?? ''));
            if ($correo === '' || ! filter_var($correo, FILTER_VALIDATE_EMAIL)) {
                $omitidos++;
                continue;
            }

            $vence = Carbon::parse($c->fecha_vencimiento, $tz)->startOfDay();
            $yaEnviadoHoy = $c->primer_envio_en && Carbon::parse($c->primer_envio_en, $tz)->isSameDay($hoy);

            $columnaMarca = null;
            $asunto = null;
            $tituloDetalle = null;

            if ($diasAntes > 0 && $vence->copy()->subDays($diasAntes)->isSameDay($hoy) && is_null($c->recordatorio_previo_en) && ! $yaEnviadoHoy) {
                $columnaMarca = 'recordatorio_previo_en';
                $asunto = "UNEXO — Recordatorio: tu cuota {$c->nro_cuota} vence el ".$vence->format('d/m/Y');
                $tituloDetalle = "Te recordamos que dentro de {$diasAntes} días vence tu cuota en UNEXO.";
            } elseif ($enviarDia && $vence->isSameDay($hoy) && is_null($c->recordatorio_vencimiento_en) && ! $yaEnviadoHoy) {
                $columnaMarca = 'recordatorio_vencimiento_en';
                $asunto = "UNEXO — Hoy vence tu cuota {$c->nro_cuota} de {$c->programa_nombre}";
                $tituloDetalle = 'Hoy es la fecha de vencimiento de tu cuota en UNEXO.';
            } elseif ($diasDespues > 0 && $vence->copy()->addDays($diasDespues)->isSameDay($hoy) && is_null($c->recordatorio_mora_en)) {
                $columnaMarca = 'recordatorio_mora_en';
                $asunto = "UNEXO — Aviso de cuota pendiente (Orden #{$c->nro_orden} · Cuota {$c->nro_cuota})";
                $tituloDetalle = "Tu cuota {$c->nro_cuota} venció el ".$vence->format('d/m/Y').' y continúa pendiente de pago.';
            }

            if (! $columnaMarca) {
                $omitidos++;
                continue;
            }

            $token = $c->token_pago ?: $this->pagos->asegurarTokenCuota((int) $c->nro_orden, (int) $c->nro_cuota);
            $enlace = "{$frontend}/pagos/cuota?token={$token}";
            $monto = number_format((float) $c->monto, 2, '.', '');
            $clienteNombre = trim("{$c->prospecto_nombre} {$c->prospecto_apellido}");
            $totalCuotas = max((int) ($c->total_cuotas ?? 1), 1);

            $cuerpo = implode("\n", [
                "Hola, {$clienteNombre}.",
                '',
                $tituloDetalle,
                '',
                "Programa: {$c->programa_nombre}".($c->modulo_nombre ? " — {$c->modulo_nombre}" : ''),
                "Orden: #{$c->nro_orden}",
                "Cuota: {$c->nro_cuota} de {$totalCuotas}",
                "Importe: Bs {$monto} (BOB)",
                'Vencimiento: '.$vence->format('d/m/Y'),
                '',
                'Haz clic en «Completar pago» para abrir de forma segura la pasarela de Stripe Sandbox.',
                'Operación de demostración mediante Stripe Sandbox.',
            ]);

            $res = $this->notificaciones->enviarCorreoSistema($correo, $asunto, $cuerpo, $c->vendedor_correo, $enlace, 'Completar pago');
            if ($res['notificacion']->estado === 'enviada') {
                $this->pagos->marcarEnvioCuota((int) $c->nro_orden, (int) $c->nro_cuota, $columnaMarca);
                $enviados++;
            } else {
                $fallidos++;
            }
        }

        return [
            'fecha' => $hoy->toDateString(),
            'evaluadas' => $cuotas->count(),
            'enviados' => $enviados,
            'fallidos' => $fallidos,
            'omitidos' => $omitidos,
        ];
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

            self::estadoCuota($this->pagos, $registro->nro_orden, $cuota, 'Pago aprobado', array_filter(['observacion' => $observacion]), $observacion);
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
            self::estadoCuota($this->pagos, $registro->nro_orden, $cuota, 'Pago rechazado', array_filter(['observacion' => $observacion]), $observacion);
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

    private function validarReglasDescuentos($descuentos, $modulos): void
    {
        foreach ($descuentos as $descuento) {
            if ($descuento->codigo === '3_MAS_MODULOS' && $modulos->count() < 3) {
                throw ValidationException::withMessages([
                    'descuentos' => 'El descuento «3 o más módulos» requiere seleccionar al menos 3 módulos.',
                ]);
            }
            if ($descuento->codigo === 'PROGRAMA_COMPLETO') {
                $programas = $modulos->pluck('programa_codigo')->unique();
                $totalAbiertos = $programas->count() === 1 ? $this->pagos->cantidadModulosAbiertos((string) $programas->first()) : 0;
                if ($programas->count() !== 1 || $totalAbiertos === 0 || $modulos->count() < $totalAbiertos) {
                    throw ValidationException::withMessages([
                        'descuentos' => 'El descuento «Programa completo» requiere seleccionar todos los módulos del programa.',
                    ]);
                }
            }
        }
    }

    private function enviarSolicitudInicialOrden(OrdenPago $orden, $tarjeta, array $filasCuota, string $vendedorCorreo): ?string
    {
        $prospecto = $tarjeta->prospecto;
        $correo = trim((string) ($prospecto?->correo ?? ''));
        if ($correo === '' || ! filter_var($correo, FILTER_VALIDATE_EMAIL)) {
            return null;
        }

        $primera = $filasCuota[0] ?? null;
        if (! $primera) {
            return null;
        }

        $tz = (string) config('pagos_recordatorios.zona_horaria', 'America/La_Paz');
        $hoy = now($tz)->startOfDay();
        $frontend = rtrim((string) config('services.frontend.url', 'http://localhost:5173'), '/');
        $enlace = "{$frontend}/pagos/cuota?token={$primera['token_pago']}";
        $totalCuotas = count($filasCuota);
        $clienteNombre = trim("{$prospecto->nombre} {$prospecto->apellido}");

        $lineasPlan = array_map(
            fn ($c) => "· Cuota {$c['nro_cuota']} de {$totalCuotas}: Bs ".number_format((float) $c['monto'], 2, '.', '').' — vence '.Carbon::parse($c['fecha_vencimiento'])->format('d/m/Y'),
            $filasCuota
        );

        $cuerpo = implode("\n", array_merge([
            "Hola, {$clienteNombre}.",
            '',
            "Se generó tu orden de pago #{$orden->nro_orden} en UNEXO para {$tarjeta->programa_nombre}.",
            'Total contratado: Bs '.number_format((float) $orden->total, 2, '.', '').' (BOB)',
            '',
            'Resumen de tu plan de pagos:',
        ], $lineasPlan, [
            '',
            'Puedes completar el pago de tu primera cuota haciendo clic en «Completar pago».',
            'Operación de demostración mediante Stripe Sandbox.',
        ]));

        try {
            $res = $this->notificaciones->enviarCorreoSistema(
                $correo,
                "UNEXO — Enlace de pago y plan de cuotas (Orden #{$orden->nro_orden})",
                $cuerpo,
                $vendedorCorreo,
                $enlace,
                'Completar pago'
            );

            if ($res['notificacion']->estado === 'enviada') {
                $this->pagos->marcarEnvioCuota($orden->nro_orden, 1, 'primer_envio_en');
                if (Carbon::parse($primera['fecha_vencimiento'], $tz)->startOfDay()->isSameDay($hoy)) {
                    $this->pagos->marcarEnvioCuota($orden->nro_orden, 1, 'recordatorio_vencimiento_en');
                }

                return null;
            }

            return 'La orden se generó correctamente, pero no se pudo enviar el correo inicial por SMTP. Puede compartir el enlace manualmente.';
        } catch (\Throwable) {
            return 'La orden se generó correctamente, pero ocurrió un error SMTP al enviar la notificación inicial. Puede reintentarlo manualmente.';
        }
    }

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

    private function metodoActivo(string $documento, int $numero, string|array|null $tipo, string $mensaje): MetodoPago
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

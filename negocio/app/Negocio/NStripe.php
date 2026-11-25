<?php

namespace App\Negocio;

use App\Exceptions\ReglaNegocioException;
use Datos\DPago;
use Datos\DStripe;
use Datos\Modelos\Interes;
use Datos\Modelos\OrdenPago;
use Datos\Modelos\Prospecto;
use Datos\Modelos\TransaccionStripe;
use Datos\Modelos\Usuario;
use Illuminate\Support\Carbon;
use Stripe\Checkout\Session;
use Stripe\Exception\ApiErrorException;
use Stripe\Exception\SignatureVerificationException;
use Stripe\StripeClient;
use Stripe\Webhook;

/**
 * Capa de negocio — Integración auténtica con Stripe Checkout Sandbox (moneda BOB),
 * Setup de tarjetas oficiales, confirmación idempotente, anulación segura y webhooks firmados.
 */
class NStripe
{
    public function __construct(
        private readonly DStripe $datos,
        private readonly DPago $pagos,
    ) {
    }

    public function iniciarCheckoutCuota(int $nroOrden, int $nroCuota, Usuario $usuario): array
    {
        $orden = $this->datos->ordenConDetalle($nroOrden);
        $interes = $orden->interes;
        NAlcance::autorizarTarjeta($usuario, $interes);
        ReglaNegocioException::si($orden->estado !== 'Activa', 'La orden de pago fue anulada y no admite cobros.');
        ReglaNegocioException::si($interes->estado === 'Perdido', 'La tarjeta fue marcada como Perdida.');

        $cuota = $this->datos->transaccion(function () use ($orden, $nroCuota) {
            $fila = $this->datos->cuotaBloqueada($orden->nro_orden, $nroCuota);
            ReglaNegocioException::si(! $fila, 'La cuota solicitada no existe.', 404);
            ReglaNegocioException::si($fila->estado === 'Pago aprobado', 'Esta cuota ya fue pagada.');
            ReglaNegocioException::si($fila->estado === 'En revision', 'Esta cuota tiene un comprobante manual en revisión.');

            return $fila;
        });

        $centavos = $this->aCentavos($cuota->monto);
        ReglaNegocioException::si($centavos <= 0, 'El monto de la cuota debe ser mayor a cero.');

        $stripe = $this->cliente();
        $abierta = $this->datos->transaccionAbiertaPorCuota($orden->nro_orden, $nroCuota);
        if ($abierta) {
            $sesion = $this->recuperarSesion($stripe, $abierta->stripe_sesion);
            $this->validarSandbox($sesion->livemode);

            if ($sesion->payment_status === 'paid') {
                $this->confirmarPagoDesdeSesion($sesion, $abierta, $usuario);
                ReglaNegocioException::si(true, 'Esta cuota ya fue pagada en Stripe y acaba de confirmarse.', 409);
            }

            if ($sesion->status === 'open' && (int) $sesion->amount_total === $centavos && $sesion->url) {
                return [
                    'url' => $sesion->url,
                    'session_id' => $sesion->id,
                    'moneda' => 'BOB',
                    'monto' => (float) $cuota->monto,
                    'reutilizada' => true,
                ];
            }

            if ($sesion->status === 'expired') {
                $this->datos->actualizarTransaccion($abierta, [
                    'estado_sesion' => 'expired',
                    'estado_interno' => 'expirado',
                ]);
            }
        }

        $prospecto = $interes->prospecto;
        $customerId = $this->asegurarCustomer($stripe, $prospecto);
        $intento = $this->datos->contarIntentosCuota($orden->nro_orden, $nroCuota) + 1;
        $totalCuotas = max($orden->cuotas->count(), 1);
        $frontend = $this->urlFrontend();
        $meta = [
            'tipo' => 'payment',
            'nro_orden' => (string) $orden->nro_orden,
            'nro_cuota' => (string) $nroCuota,
            'nro_tarjeta' => (string) $interes->nro_tarjeta,
            'documento' => (string) $prospecto->documento,
            'usuario_correo' => (string) $usuario->correo,
            'moneda' => 'bob',
            'monto_bob' => number_format((float) $cuota->monto, 2, '.', ''),
        ];

        $claveIdemp = "unexo-chk-ord-{$orden->nro_orden}-cta-{$nroCuota}-i{$intento}";
        try {
            $sesion = $stripe->checkout->sessions->create([
                'mode' => 'payment',
                'allowed_payment_method_types' => ['card'],
                'locale' => 'es',
                'customer' => $customerId,
                'line_items' => [[
                    'price_data' => [
                        'currency' => $this->moneda(),
                        'product_data' => [
                            'name' => "{$interes->modulo_nombre} ({$interes->programa_nombre})",
                            'description' => "Orden #{$orden->nro_orden} · Cuota {$nroCuota} de {$totalCuotas} · {$prospecto->nombre} {$prospecto->apellido}",
                        ],
                        'unit_amount' => $centavos,
                    ],
                    'quantity' => 1,
                ]],
                'payment_intent_data' => [
                    'setup_future_usage' => 'off_session',
                    'metadata' => $meta,
                ],
                'success_url' => "{$frontend}/pagos/confirmacion?session_id={CHECKOUT_SESSION_ID}",
                'cancel_url' => "{$frontend}/pagos/cancelado?session_id={CHECKOUT_SESSION_ID}",
                'metadata' => $meta,
            ], ['idempotency_key' => $claveIdemp]);
        } catch (ApiErrorException $e) {
            throw new ReglaNegocioException('Stripe no pudo iniciar la sesión de pago: '.$e->getMessage(), 502);
        }

        $this->validarSandbox($sesion->livemode);
        ReglaNegocioException::si(strtolower((string) $sesion->currency) !== 'bob', 'Stripe devolvió una moneda distinta de BOB.', 502);
        ReglaNegocioException::si((int) $sesion->amount_total !== $centavos, 'El monto devuelto por Stripe no coincide con la cuota.', 502);

        $this->datos->transaccion(function () use ($orden, $nroCuota, $prospecto, $usuario, $sesion, $customerId, $cuota, $centavos, $claveIdemp, $interes): void {
            if (! $this->datos->transaccionPorSesionBloqueada($sesion->id)) {
                $this->datos->crearTransaccion([
                    'tipo' => 'payment',
                    'nro_orden' => $orden->nro_orden,
                    'nro_cuota' => $nroCuota,
                    'documento' => $prospecto->documento,
                    'usuario_correo' => $usuario->correo,
                    'stripe_sesion' => $sesion->id,
                    'stripe_pago_intent' => is_string($sesion->payment_intent) ? $sesion->payment_intent : $sesion->payment_intent?->id,
                    'stripe_cliente' => $customerId,
                    'moneda' => 'bob',
                    'monto_esperado' => $cuota->monto,
                    'monto_centavos' => $centavos,
                    'estado_sesion' => (string) $sesion->status,
                    'estado_pago' => (string) $sesion->payment_status,
                    'estado_interno' => 'pendiente',
                    'livemode' => (bool) $sesion->livemode,
                    'url_checkout' => $sesion->url,
                    'clave_idempotencia' => $claveIdemp,
                ]);
            }

            $this->pagos->registrarInteraccion($interes, [
                'usuario_correo' => $usuario->correo,
                'tipo' => 'Pago informado',
                'fecha' => now(),
                'descripcion' => "Sesión Stripe Checkout iniciada para cuota {$nroCuota} de la orden #{$orden->nro_orden} (Bs ".number_format((float) $cuota->monto, 2, '.', '').").",
                'resultado' => 'Checkout abierto',
            ]);
            $this->pagos->actualizarInteres($interes, ['ultima_actividad_en' => now()]);
        });

        return [
            'url' => $sesion->url,
            'session_id' => $sesion->id,
            'moneda' => 'BOB',
            'monto' => (float) $cuota->monto,
            'reutilizada' => false,
        ];
    }

    public function iniciarSetupTarjeta(string $documento, Usuario $usuario, ?int $nroTarjeta = null): array
    {
        $prospecto = $this->pagos->prospecto($documento);
        ReglaNegocioException::si(! $this->pagos->prospectoEnCartera($prospecto, $usuario), 'Este prospecto no está dentro de su cartera.', 403);

        $stripe = $this->cliente();
        $customerId = $this->asegurarCustomer($stripe, $prospecto);
        $frontend = $this->urlFrontend();
        $meta = [
            'tipo' => 'setup',
            'documento' => (string) $prospecto->documento,
            'usuario_correo' => (string) $usuario->correo,
            'nro_tarjeta' => (string) ($nroTarjeta ?? ''),
        ];

        try {
            $sesion = $stripe->checkout->sessions->create([
                'mode' => 'setup',
                'allowed_payment_method_types' => ['card'],
                'locale' => 'es',
                'customer' => $customerId,
                'setup_intent_data' => ['metadata' => $meta],
                'success_url' => "{$frontend}/pagos/confirmacion?session_id={CHECKOUT_SESSION_ID}",
                'cancel_url' => "{$frontend}/pagos/cancelado?session_id={CHECKOUT_SESSION_ID}",
                'metadata' => $meta,
            ]);
        } catch (ApiErrorException $e) {
            throw new ReglaNegocioException('Stripe no pudo iniciar el registro de tarjeta: '.$e->getMessage(), 502);
        }

        $this->validarSandbox($sesion->livemode);

        $this->datos->crearTransaccion([
            'tipo' => 'setup',
            'documento' => $prospecto->documento,
            'usuario_correo' => $usuario->correo,
            'stripe_sesion' => $sesion->id,
            'stripe_setup_intent' => is_string($sesion->setup_intent) ? $sesion->setup_intent : $sesion->setup_intent?->id,
            'stripe_cliente' => $customerId,
            'moneda' => 'bob',
            'estado_sesion' => (string) $sesion->status,
            'estado_pago' => (string) ($sesion->payment_status ?? 'no_payment_required'),
            'estado_interno' => 'pendiente',
            'livemode' => (bool) $sesion->livemode,
            'url_checkout' => $sesion->url,
        ]);

        return ['url' => $sesion->url, 'session_id' => $sesion->id];
    }

    public function verificarSesion(string $sessionId, ?Usuario $actor = null, bool $exigirAutorizacion = true): array
    {
        $tx = $this->datos->transaccionPorSesion($sessionId);
        ReglaNegocioException::si(! $tx, 'La sesión de pago solicitada no existe en UNEXO.', 404);

        if ($exigirAutorizacion && $actor) {
            if ($tx->tipo === 'payment' && $tx->orden?->interes) {
                NAlcance::autorizarTarjeta($actor, $tx->orden->interes);
            } else {
                $prospecto = $tx->prospecto ?? $this->pagos->prospecto((string) $tx->documento);
                ReglaNegocioException::si(! $this->pagos->prospectoEnCartera($prospecto, $actor), 'Este prospecto no está dentro de su cartera.', 403);
            }
        }

        $stripe = $this->cliente();
        $sesion = $this->recuperarSesion($stripe, $sessionId);
        $this->validarSandbox($sesion->livemode);

        if ($tx->tipo === 'setup' || $sesion->mode === 'setup') {
            return $this->confirmarSetupDesdeSesion($sesion, $tx);
        }

        return $this->confirmarPagoDesdeSesion($sesion, $tx, $actor);
    }

    public function cancelarSesion(string $sessionId, Usuario $actor): array
    {
        $tx = $this->datos->transaccionPorSesion($sessionId);
        ReglaNegocioException::si(! $tx, 'La sesión de pago solicitada no existe.', 404);

        if ($tx->tipo === 'payment' && $tx->orden?->interes) {
            NAlcance::autorizarTarjeta($actor, $tx->orden->interes);
        } else {
            $prospecto = $tx->prospecto ?? $this->pagos->prospecto((string) $tx->documento);
            ReglaNegocioException::si(! $this->pagos->prospectoEnCartera($prospecto, $actor), 'Este prospecto no está dentro de su cartera.', 403);
        }

        $stripe = $this->cliente();
        $sesion = $this->recuperarSesion($stripe, $sessionId);
        $this->validarSandbox($sesion->livemode);

        if ($sesion->mode === 'payment' && $sesion->payment_status === 'paid') {
            return $this->confirmarPagoDesdeSesion($sesion, $tx, $actor);
        }

        if ($tx->estado_interno === 'pendiente') {
            $nuevoEstado = $sesion->status === 'expired' ? 'expirado' : 'cancelado';
            $this->datos->actualizarTransaccion($tx, [
                'estado_sesion' => (string) $sesion->status,
                'estado_pago' => (string) ($sesion->payment_status ?? 'unpaid'),
                'estado_interno' => $nuevoEstado,
            ]);
        }

        return $this->armarRespuestaPago($this->datos->transaccionPorSesion($sessionId), [], 'Pago no completado');
    }

    public function anularOrden(int $nroOrden, Usuario $actor, string $motivo): OrdenPago
    {
        $orden = $this->datos->ordenConDetalle($nroOrden);
        $interes = $orden->interes;
        NAlcance::autorizarTarjeta($actor, $interes);
        ReglaNegocioException::si($orden->estado !== 'Activa', 'La orden ya fue anulada previamente.');
        ReglaNegocioException::si($this->datos->tienePagosNoAnulables($orden->nro_orden), 'No se puede anular una orden que ya tiene cuotas pagadas o en revisión.');

        $pendientes = $this->datos->transaccionesPendientesDeOrden($orden->nro_orden);
        if ($pendientes->isNotEmpty()) {
            $stripe = $this->cliente();
            foreach ($pendientes as $tx) {
                try {
                    $sesion = $this->recuperarSesion($stripe, $tx->stripe_sesion);
                    if ($sesion->payment_status === 'paid') {
                        $this->confirmarPagoDesdeSesion($sesion, $tx, $actor);
                        throw new ReglaNegocioException('Una cuota ya fue pagada en Stripe. No se puede anular la orden.', 409);
                    }
                    if ($sesion->status === 'open') {
                        $stripe->checkout->sessions->expire($tx->stripe_sesion);
                    }
                } catch (ReglaNegocioException $e) {
                    throw $e;
                } catch (ApiErrorException) {
                    // Si la sesión ya expiró en Stripe, se continúa con la anulación local.
                }
            }
        }

        $this->datos->transaccion(function () use ($orden, $actor, $motivo, $pendientes, $interes): void {
            $bloqueada = $this->datos->ordenBloqueada($orden->nro_orden);
            ReglaNegocioException::si($bloqueada->estado !== 'Activa', 'La orden ya fue anulada.');
            ReglaNegocioException::si($this->datos->tienePagosNoAnulables($bloqueada->nro_orden), 'No se puede anular una orden con pagos confirmados.');

            foreach ($pendientes as $tx) {
                $this->datos->actualizarTransaccion($tx, [
                    'estado_sesion' => 'expired',
                    'estado_interno' => 'expirado',
                    'detalle_error' => 'Orden anulada antes de completar el pago.',
                ]);
            }

            $this->pagos->actualizarOrden($bloqueada, [
                'estado' => 'Anulada',
                'motivo_anulacion' => trim($motivo),
                'fecha_anulacion' => now(),
                'anulada_por' => $actor->correo,
            ]);

            $this->pagos->registrarInteraccion($interes, [
                'usuario_correo' => $actor->correo,
                'tipo' => 'Nota comercial',
                'fecha' => now(),
                'descripcion' => "Orden #{$bloqueada->nro_orden} anulada. Motivo: ".trim($motivo),
                'resultado' => 'Orden anulada',
            ]);
            $this->pagos->actualizarInteres($interes, ['ultima_actividad_en' => now()]);
        });

        return $this->datos->ordenConDetalle($nroOrden);
    }

    public function procesarWebhook(string $payload, string $firma): array
    {
        $secret = (string) config('services.stripe.webhook_secret');
        ReglaNegocioException::si(! str_starts_with($secret, 'whsec_'), 'El secreto de webhook de Stripe no está configurado.', 500);

        try {
            $evento = Webhook::constructEvent($payload, $firma, $secret);
        } catch (SignatureVerificationException|\UnexpectedValueException $e) {
            throw new ReglaNegocioException('Firma de webhook Stripe inválida.', 400);
        }

        $this->validarSandbox($evento->livemode);

        if ($this->datos->eventoWebhook($evento->id)) {
            return ['recibido' => true, 'duplicado' => true, 'evento' => $evento->id];
        }

        $objeto = $evento->data->object;
        $nroTx = null;
        $sessionId = null;
        $piId = null;
        $resumen = "Evento {$evento->type}";
        $estadoWebhook = 'procesado';

        switch ($evento->type) {
            case 'checkout.session.completed':
                $sessionId = $objeto->id;
                $tx = $this->datos->transaccionPorSesion($sessionId);
                if ($tx) {
                    $nroTx = $tx->nro_transaccion;
                    $res = $this->verificarSesion($sessionId, null, false);
                    $piId = $res['stripe_pago_intent'] ?? null;
                    $resumen = "Checkout {$sessionId} ({$res['estado_interno']})";
                } else {
                    $estadoWebhook = 'ignorado';
                    $resumen = "Sesión externa {$sessionId} sin referencia en UNEXO";
                }
                break;

            case 'checkout.session.expired':
                $sessionId = $objeto->id;
                $tx = $this->datos->transaccionPorSesion($sessionId);
                if ($tx) {
                    $nroTx = $tx->nro_transaccion;
                    if ($tx->estado_interno === 'pendiente') {
                        $this->datos->actualizarTransaccion($tx, [
                            'estado_sesion' => 'expired',
                            'estado_interno' => 'expirado',
                        ]);
                    }
                    $resumen = "Sesión {$sessionId} marcada como expirada";
                } else {
                    $estadoWebhook = 'ignorado';
                }
                break;

            case 'payment_intent.succeeded':
                $piId = $objeto->id;
                $tx = $this->datos->transaccionPorPaymentIntent($piId);
                if (! $tx && isset($objeto->metadata['nro_orden'], $objeto->metadata['nro_cuota'])) {
                    $tx = $this->datos->transaccionAbiertaPorCuota((int) $objeto->metadata['nro_orden'], (int) $objeto->metadata['nro_cuota']);
                }
                if ($tx) {
                    $nroTx = $tx->nro_transaccion;
                    $sessionId = $tx->stripe_sesion;
                    $res = $this->verificarSesion($tx->stripe_sesion, null, false);
                    $resumen = "PaymentIntent {$piId} verificado vía {$tx->stripe_sesion} ({$res['estado_interno']})";
                } else {
                    $estadoWebhook = 'ignorado';
                    $resumen = "PaymentIntent {$piId} sin sesión pendiente asociada";
                }
                break;

            case 'payment_intent.payment_failed':
                $piId = $objeto->id;
                $errorMsg = $objeto->last_payment_error?->message ?? 'El pago fue rechazado por la entidad emisora.';
                $tx = $this->datos->transaccionPorPaymentIntent($piId);
                if (! $tx && isset($objeto->metadata['nro_orden'], $objeto->metadata['nro_cuota'])) {
                    $tx = $this->datos->transaccionAbiertaPorCuota((int) $objeto->metadata['nro_orden'], (int) $objeto->metadata['nro_cuota']);
                }
                if ($tx) {
                    $nroTx = $tx->nro_transaccion;
                    $sessionId = $tx->stripe_sesion;
                    if ($tx->estado_interno !== 'confirmado') {
                        $this->datos->actualizarTransaccion($tx, [
                            'stripe_pago_intent' => $piId,
                            'estado_pago' => 'unpaid',
                            'detalle_error' => $errorMsg,
                        ]);
                    }
                    $resumen = "Fallo registrado en {$piId}: {$errorMsg}";
                } else {
                    $estadoWebhook = 'ignorado';
                }
                break;

            default:
                $estadoWebhook = 'ignorado';
                $resumen = "Evento {$evento->type} no utilizado";
        }

        $this->datos->registrarEventoWebhook([
            'stripe_evento' => $evento->id,
            'tipo' => $evento->type,
            'nro_transaccion' => $nroTx,
            'stripe_sesion' => $sessionId,
            'stripe_pago_intent' => $piId,
            'livemode' => (bool) $evento->livemode,
            'estado' => $estadoWebhook,
            'resumen' => $resumen,
            'procesado_en' => now(),
        ]);

        return ['recibido' => true, 'duplicado' => false, 'evento' => $evento->id, 'estado' => $estadoWebhook];
    }

    // ---------------------------------------------------------------- conciliación idempotente

    private function confirmarPagoDesdeSesion(Session $sesion, TransaccionStripe $txInicial, ?Usuario $actor = null): array
    {
        $pi = is_object($sesion->payment_intent) ? $sesion->payment_intent : null;
        $piId = $pi?->id ?? (is_string($sesion->payment_intent) ? $sesion->payment_intent : null);
        $pm = $pi && is_object($pi->payment_method) ? $pi->payment_method : null;
        $pmId = $pm?->id ?? ($pi && is_string($pi->payment_method) ? $pi->payment_method : null);
        $card = $pm?->card;
        $marca = $card ? $this->traducirMarca((string) $card->brand) : null;
        $ultimos4 = $card?->last4;
        $vencimiento = $card ? sprintf('%02d/%02d', (int) $card->exp_month, ((int) $card->exp_year) % 100) : null;
        $titular = $pm?->billing_details?->name;
        $charge = $pi && is_object($pi->latest_charge) ? $pi->latest_charge : null;
        $receiptUrl = $charge?->receipt_url;
        $errorPi = $pi?->last_payment_error?->message;

        $moneda = strtolower((string) $sesion->currency);
        ReglaNegocioException::si($moneda !== 'bob', 'La transacción de Stripe no está expresada en bolivianos (BOB).', 422);

        if ($sesion->payment_status === 'paid' && $pi && $pi->status === 'succeeded') {
            ReglaNegocioException::si(
                (int) $sesion->amount_total !== (int) $txInicial->monto_centavos,
                'El monto confirmado por Stripe no coincide con el monto autorizado en PostgreSQL.',
                422
            );

            $faltantes = $this->datos->transaccion(function () use ($txInicial, $sesion, $piId, $pmId, $marca, $ultimos4, $vencimiento, $titular, $receiptUrl, $actor) {
                $tx = $this->datos->transaccionPorSesionBloqueada($txInicial->stripe_sesion);
                $cuota = $this->datos->cuotaBloqueada((int) $tx->nro_orden, (int) $tx->nro_cuota);
                $orden = $this->datos->ordenConDetalle((int) $tx->nro_orden);

                // Reconciliación idempotente cuando ya existe aprobación sobre esta cuota.
                if ($cuota->estado === 'Pago aprobado') {
                    if ($cuota->stripe_pago_intent === $piId || $tx->estado_interno === 'confirmado') {
                        $this->datos->actualizarTransaccion($tx, [
                            'stripe_pago_intent' => $piId,
                            'stripe_metodo' => $pmId,
                            'monto_confirmado' => $tx->monto_esperado,
                            'estado_sesion' => (string) $sesion->status,
                            'estado_pago' => (string) $sesion->payment_status,
                            'estado_interno' => 'confirmado',
                            'marca_tarjeta' => $marca,
                            'ultimos_digitos' => $ultimos4,
                            'receipt_url' => $receiptUrl,
                            'confirmado_en' => $tx->confirmado_en ?? now(),
                        ]);

                        return NConversion::faltantes($orden->interes);
                    }

                    // Segunda sesión paralela pagada sobre una cuota ya liquidada: registrar incidencia sin duplicar saldo.
                    $this->datos->actualizarTransaccion($tx, [
                        'stripe_pago_intent' => $piId,
                        'stripe_metodo' => $pmId,
                        'monto_confirmado' => $tx->monto_esperado,
                        'estado_sesion' => (string) $sesion->status,
                        'estado_pago' => (string) $sesion->payment_status,
                        'estado_interno' => 'reconciliacion_duplicada',
                        'detalle_error' => "Pago Stripe {$piId} detectado tras aprobación previa ({$cuota->stripe_pago_intent}). Requiere revisión administrativa.",
                        'marca_tarjeta' => $marca,
                        'ultimos_digitos' => $ultimos4,
                        'receipt_url' => $receiptUrl,
                    ]);
                    $this->pagos->registrarInteraccion($orden->interes, [
                        'usuario_correo' => $actor?->correo ?? $orden->vendedor_correo,
                        'tipo' => 'Nota comercial',
                        'fecha' => now(),
                        'descripcion' => "Alerta de reconciliación: cobro duplicado {$piId} sobre cuota {$tx->nro_cuota} de orden #{$tx->nro_orden} ya liquidada.",
                        'resultado' => 'Requiere reconciliación',
                    ]);

                    return [];
                }

                $nroMetodo = null;
                if ($pmId && $marca && $ultimos4 && $vencimiento) {
                    $metodo = $this->datos->registrarMetodoStripe([
                        'documento' => $orden->interes->documento,
                        'tipo' => 'Tarjeta',
                        'titular' => $titular ?: trim("{$orden->interes->prospecto->nombre} {$orden->interes->prospecto->apellido}"),
                        'marca' => $marca,
                        'ultimos_digitos' => $ultimos4,
                        'vencimiento' => $vencimiento,
                        'estado' => 'activo',
                        'proveedor' => 'stripe',
                        'stripe_cliente' => $tx->stripe_cliente,
                        'stripe_metodo' => $pmId,
                        'registrado_por' => $actor?->correo ?? $tx->usuario_correo,
                    ]);
                    $nroMetodo = $metodo->nro_metodo;
                }

                $descMetodo = $marca && $ultimos4 ? "{$marca} •••• {$ultimos4}" : 'Tarjeta Stripe';
                $observacion = "Stripe Sandbox {$piId} · {$descMetodo}";

                $this->datos->marcarCuotaPagadaStripe(
                    (int) $tx->nro_orden,
                    (int) $tx->nro_cuota,
                    [
                        'nro_metodo' => $nroMetodo,
                        'stripe_sesion' => $sesion->id,
                        'stripe_pago_intent' => $piId,
                        'stripe_metodo' => $pmId,
                        'stripe_recibo_url' => $receiptUrl,
                        'observacion' => $observacion,
                    ],
                    "Pago confirmado por Stripe Sandbox ({$piId})"
                );

                $this->datos->actualizarTransaccion($tx, [
                    'stripe_pago_intent' => $piId,
                    'stripe_metodo' => $pmId,
                    'monto_confirmado' => $tx->monto_esperado,
                    'estado_sesion' => (string) $sesion->status,
                    'estado_pago' => (string) $sesion->payment_status,
                    'estado_interno' => 'confirmado',
                    'marca_tarjeta' => $marca,
                    'ultimos_digitos' => $ultimos4,
                    'receipt_url' => $receiptUrl,
                    'detalle_error' => null,
                    'confirmado_en' => now(),
                ]);

                $interes = $this->pagos->interesBloqueado($orden->nro_tarjeta);
                $responsable = $actor ?? $orden->vendedor;
                $this->pagos->registrarInteraccion($interes, [
                    'usuario_correo' => $responsable->correo,
                    'tipo' => 'Compra validada',
                    'fecha' => now(),
                    'descripcion' => "Cuota {$tx->nro_cuota} de la orden #{$tx->nro_orden} pagada con {$descMetodo} vía Stripe Sandbox ({$piId}).",
                    'resultado' => 'Pago aprobado',
                ]);
                $this->pagos->actualizarInteres($interes, ['ultima_actividad_en' => now()]);

                if ((int) $tx->nro_cuota === 1 && $interes->estado !== 'Convertido') {
                    $faltan = NConversion::faltantes($interes);
                    if (! $faltan) {
                        NConversion::procesar($interes, $responsable);
                    }

                    return $faltan;
                }

                return [];
            });

            return $this->armarRespuestaPago($this->datos->transaccionPorSesion($sesion->id), $faltantes, 'Pago confirmado');
        }

        // Sesión no pagada todavía: expirada, rechazada con error previo, o abierta esperando confirmación/reintento.
        $estadoInterno = match (true) {
            $sesion->status === 'expired' => 'expirado',
            $errorPi !== null => 'rechazado',
            $txInicial->estado_interno === 'cancelado' => 'cancelado',
            default => 'pendiente',
        };

        $this->datos->actualizarTransaccion($txInicial, [
            'stripe_pago_intent' => $piId,
            'estado_sesion' => (string) $sesion->status,
            'estado_pago' => (string) $sesion->payment_status,
            'estado_interno' => $estadoInterno,
            'detalle_error' => $errorPi ?: $txInicial->detalle_error,
        ]);

        $titulo = match ($estadoInterno) {
            'expirado' => 'Sesión expirada',
            'rechazado' => 'Pago rechazado',
            'cancelado' => 'Pago no completado',
            default => 'Pago pendiente de confirmación',
        };

        return $this->armarRespuestaPago($this->datos->transaccionPorSesion($sesion->id), [], $titulo);
    }

    private function confirmarSetupDesdeSesion(Session $sesion, TransaccionStripe $txInicial): array
    {
        $si = is_object($sesion->setup_intent) ? $sesion->setup_intent : null;
        $siId = $si?->id ?? (is_string($sesion->setup_intent) ? $sesion->setup_intent : null);
        $pm = $si && is_object($si->payment_method) ? $si->payment_method : null;
        $pmId = $pm?->id ?? ($si && is_string($si->payment_method) ? $si->payment_method : null);

        if ($sesion->status === 'complete' && $si && $si->status === 'succeeded' && $pm && $pm->card) {
            $marca = $this->traducirMarca((string) $pm->card->brand);
            $ultimos4 = (string) $pm->card->last4;
            $vencimiento = sprintf('%02d/%02d', (int) $pm->card->exp_month, ((int) $pm->card->exp_year) % 100);
            $prospecto = $this->pagos->prospecto((string) $txInicial->documento);
            $titular = $pm->billing_details?->name ?: trim("{$prospecto->nombre} {$prospecto->apellido}");

            $this->datos->transaccion(function () use ($txInicial, $sesion, $siId, $pmId, $prospecto, $titular, $marca, $ultimos4, $vencimiento): void {
                $tx = $this->datos->transaccionPorSesionBloqueada($txInicial->stripe_sesion);
                $this->datos->registrarMetodoStripe([
                    'documento' => $prospecto->documento,
                    'tipo' => 'Tarjeta',
                    'titular' => $titular,
                    'marca' => $marca,
                    'ultimos_digitos' => $ultimos4,
                    'vencimiento' => $vencimiento,
                    'estado' => 'activo',
                    'proveedor' => 'stripe',
                    'stripe_cliente' => $tx->stripe_cliente,
                    'stripe_metodo' => $pmId,
                    'registrado_por' => $tx->usuario_correo,
                ]);
                $this->datos->actualizarTransaccion($tx, [
                    'stripe_setup_intent' => $siId,
                    'stripe_metodo' => $pmId,
                    'estado_sesion' => (string) $sesion->status,
                    'estado_pago' => 'setup_succeeded',
                    'estado_interno' => 'confirmado',
                    'marca_tarjeta' => $marca,
                    'ultimos_digitos' => $ultimos4,
                    'confirmado_en' => $tx->confirmado_en ?? now(),
                ]);
            });
        } elseif ($sesion->status === 'expired' && $txInicial->estado_interno === 'pendiente') {
            $this->datos->actualizarTransaccion($txInicial, [
                'stripe_setup_intent' => $siId,
                'estado_sesion' => 'expired',
                'estado_interno' => 'expirado',
            ]);
        }

        $actual = $this->datos->transaccionPorSesion($sesion->id);
        $prospecto = $actual->prospecto;

        return [
            'tipo' => 'setup',
            'titulo' => $actual->estado_interno === 'confirmado' ? 'Tarjeta registrada correctamente' : 'Registro de tarjeta no completado',
            'estado_interno' => $actual->estado_interno,
            'estado_sesion' => $actual->estado_sesion,
            'stripe_sesion' => $actual->stripe_sesion,
            'stripe_cliente' => $actual->stripe_cliente,
            'stripe_metodo' => $actual->stripe_metodo,
            'marca_tarjeta' => $actual->marca_tarjeta,
            'ultimos_digitos' => $actual->ultimos_digitos,
            'prospecto' => $prospecto ? trim("{$prospecto->nombre} {$prospecto->apellido}") : null,
            'nro_tarjeta' => ($sesion->metadata['nro_tarjeta'] ?? '') !== '' ? (int) $sesion->metadata['nro_tarjeta'] : null,
            'fecha_confirmacion' => $actual->confirmado_en?->toIso8601String(),
            'livemode' => $actual->livemode,
        ];
    }

    private function armarRespuestaPago(TransaccionStripe $tx, array $faltantesConversion, string $titulo): array
    {
        $orden = $tx->orden;
        $interes = $orden?->interes;
        $prospecto = $interes?->prospecto ?? $tx->prospecto;
        $cuotas = $orden?->cuotas ?? collect();
        $cuota = $cuotas->firstWhere('nro_cuota', $tx->nro_cuota);
        $saldo = $orden ? $this->datos->cuotaConSaldoOrden($orden->nro_orden) : 0.0;

        return [
            'tipo' => 'payment',
            'titulo' => $titulo,
            'estado_interno' => $tx->estado_interno,
            'estado_sesion' => $tx->estado_sesion,
            'estado_pago' => $tx->estado_pago,
            'estado_cuota' => $cuota?->estado,
            'nro_orden' => $tx->nro_orden,
            'nro_cuota' => $tx->nro_cuota,
            'total_cuotas' => $cuotas->count(),
            'nro_tarjeta' => $interes?->nro_tarjeta,
            'prospecto' => $prospecto ? trim("{$prospecto->nombre} {$prospecto->apellido}") : null,
            'programa' => $interes?->programa_nombre,
            'modulo' => $interes?->modulo_nombre,
            'monto' => (float) ($tx->monto_confirmado ?? $tx->monto_esperado ?? 0),
            'moneda' => 'BOB',
            'saldo_pendiente' => $saldo,
            'stripe_sesion' => $tx->stripe_sesion,
            'stripe_pago_intent' => $tx->stripe_pago_intent,
            'stripe_metodo' => $tx->stripe_metodo,
            'marca_tarjeta' => $tx->marca_tarjeta,
            'ultimos_digitos' => $tx->ultimos_digitos,
            'receipt_url' => $tx->receipt_url,
            'detalle_error' => $tx->detalle_error,
            'url_checkout' => $tx->estado_sesion === 'open' ? $tx->url_checkout : null,
            'fecha_confirmacion' => ($tx->confirmado_en ?? $tx->updated_at)?->toIso8601String(),
            'estado_comercial' => $interes?->estado,
            'faltantes_conversion' => $faltantesConversion,
            'livemode' => $tx->livemode,
        ];
    }

    // ---------------------------------------------------------------- utilidades Stripe

    private function cliente(): StripeClient
    {
        $secret = trim((string) config('services.stripe.secret'));
        $key = trim((string) config('services.stripe.key'));
        ReglaNegocioException::si(
            $secret === '' || str_starts_with($secret, 'sk_live_') || str_starts_with($key, 'pk_live_') || ! str_starts_with($secret, 'sk_test_'),
            'Stripe debe configurarse exclusivamente en modo Sandbox (claves de prueba sk_test_ / pk_test_).',
            500
        );
        ReglaNegocioException::si($this->moneda() !== 'bob', 'La moneda oficial de Stripe debe ser bob.', 500);

        return new StripeClient($secret);
    }

    private function moneda(): string
    {
        return strtolower((string) config('services.stripe.currency', 'bob'));
    }

    private function urlFrontend(): string
    {
        return rtrim((string) config('services.frontend.url', 'http://localhost:5173'), '/');
    }

    private function aCentavos(float|string $monto): int
    {
        $texto = number_format((float) $monto, 2, '.', '');
        [$enteros, $decimales] = explode('.', $texto);

        return ((int) $enteros * 100) + (int) $decimales;
    }

    private function validarSandbox(bool $livemode): void
    {
        ReglaNegocioException::si($livemode, 'Se rechazó una respuesta en modo producción (livemode=true); solo se permite Sandbox.', 400);
    }

    private function recuperarSesion(StripeClient $stripe, string $sessionId): Session
    {
        try {
            return $stripe->checkout->sessions->retrieve($sessionId, [
                'expand' => ['payment_intent.latest_charge', 'payment_intent.payment_method', 'setup_intent.payment_method'],
            ]);
        } catch (ApiErrorException $e) {
            throw new ReglaNegocioException('No se pudo consultar la sesión en Stripe: '.$e->getMessage(), 502);
        }
    }

    private function asegurarCustomer(StripeClient $stripe, Prospecto $prospecto): string
    {
        if ($prospecto->stripe_cliente) {
            return $prospecto->stripe_cliente;
        }

        try {
            $customer = $stripe->customers->create([
                'name' => trim("{$prospecto->nombre} {$prospecto->apellido}"),
                'email' => $prospecto->correo,
                'phone' => $prospecto->telefono,
                'metadata' => ['documento' => (string) $prospecto->documento],
            ]);
        } catch (ApiErrorException $e) {
            throw new ReglaNegocioException('No se pudo crear el cliente en Stripe: '.$e->getMessage(), 502);
        }

        $this->validarSandbox((bool) $customer->livemode);

        return $this->datos->transaccion(function () use ($prospecto, $customer): string {
            $bloqueado = $this->datos->prospectoBloqueado($prospecto->documento);
            if ($bloqueado->stripe_cliente) {
                return $bloqueado->stripe_cliente;
            }
            $this->datos->guardarClienteProspecto($bloqueado, $customer->id);

            return $customer->id;
        });
    }

    private function traducirMarca(string $brand): string
    {
        return match (strtolower($brand)) {
            'visa' => 'Visa',
            'mastercard' => 'Mastercard',
            'amex' => 'American Express',
            default => ucfirst($brand ?: 'Otra'),
        };
    }
}

<?php

namespace Datos;

use Datos\Modelos\MetodoPago;
use Datos\Modelos\OrdenPago;
use Datos\Modelos\Prospecto;
use Datos\Modelos\TransaccionStripe;
use Datos\Modelos\WebhookEventoStripe;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/** Persistencia de transacciones Stripe Sandbox, métodos Stripe, webhooks e idempotencia. */
class DStripe
{
    public function transaccion(callable $operacion): mixed
    {
        return DB::transaction($operacion);
    }

    public function ordenConDetalle(int $nroOrden): OrdenPago
    {
        return OrdenPago::query()
            ->with('interes.prospecto', 'vendedor:correo,nombre,apellido', 'items', 'cuotas', 'pago')
            ->findOrFail($nroOrden);
    }

    public function ordenBloqueada(int $nroOrden): OrdenPago
    {
        return OrdenPago::query()->lockForUpdate()->findOrFail($nroOrden);
    }

    public function cuotaBloqueada(int $nroOrden, int $nroCuota): ?object
    {
        return DB::table('cuotas')->where('nro_orden', $nroOrden)->where('nro_cuota', $nroCuota)->lockForUpdate()->first();
    }

    public function prospectoBloqueado(string $documento): Prospecto
    {
        return Prospecto::query()->lockForUpdate()->findOrFail($documento);
    }

    public function guardarClienteProspecto(Prospecto $prospecto, string $stripeCliente): void
    {
        $prospecto->update(['stripe_cliente' => $stripeCliente]);
    }

    public function transaccionPorSesion(string $sessionId): ?TransaccionStripe
    {
        return TransaccionStripe::query()
            ->with('orden.interes.prospecto', 'orden.vendedor:correo,nombre,apellido', 'orden.items', 'orden.cuotas', 'prospecto')
            ->where('stripe_sesion', $sessionId)
            ->first();
    }

    public function transaccionPorSesionBloqueada(string $sessionId): ?TransaccionStripe
    {
        return TransaccionStripe::query()->where('stripe_sesion', $sessionId)->lockForUpdate()->first();
    }

    public function transaccionPorPaymentIntent(string $paymentIntentId): ?TransaccionStripe
    {
        return TransaccionStripe::query()->where('stripe_pago_intent', $paymentIntentId)->first();
    }

    public function transaccionAbiertaPorCuota(int $nroOrden, int $nroCuota): ?TransaccionStripe
    {
        return TransaccionStripe::query()
            ->where('tipo', 'payment')
            ->where('nro_orden', $nroOrden)
            ->where('nro_cuota', $nroCuota)
            ->where('estado_interno', 'pendiente')
            ->latest('nro_transaccion')
            ->first();
    }

    public function contarIntentosCuota(int $nroOrden, int $nroCuota): int
    {
        return TransaccionStripe::query()
            ->where('tipo', 'payment')
            ->where('nro_orden', $nroOrden)
            ->where('nro_cuota', $nroCuota)
            ->count();
    }

    public function transaccionesPendientesDeOrden(int $nroOrden): Collection
    {
        return TransaccionStripe::query()
            ->where('nro_orden', $nroOrden)
            ->where('estado_interno', 'pendiente')
            ->get();
    }

    public function crearTransaccion(array $datos): TransaccionStripe
    {
        return TransaccionStripe::query()->create($datos);
    }

    public function actualizarTransaccion(TransaccionStripe $tx, array $datos): void
    {
        $tx->update($datos);
    }

    public function registrarMetodoStripe(array $datos): MetodoPago
    {
        $stripeMetodo = $datos['stripe_metodo'];
        $datosSinClave = $datos;
        unset($datosSinClave['stripe_metodo']);

        return MetodoPago::query()->firstOrCreate(
            ['stripe_metodo' => $stripeMetodo],
            $datosSinClave + ['stripe_metodo' => $stripeMetodo]
        );
    }

    public function hayTransaccionesEnEstado(int $nroOrden, string $estado): bool
    {
        return TransaccionStripe::query()->where('nro_orden', $nroOrden)->where('estado_interno', $estado)->exists();
    }

    public function eventoWebhook(string $stripeEvento): ?WebhookEventoStripe
    {
        return WebhookEventoStripe::query()->find($stripeEvento);
    }

    public function registrarEventoWebhook(array $datos): WebhookEventoStripe
    {
        $evento = $datos['stripe_evento'];
        $resto = $datos;
        unset($resto['stripe_evento']);

        return WebhookEventoStripe::query()->firstOrCreate(
            ['stripe_evento' => $evento],
            $resto + ['stripe_evento' => $evento]
        );
    }
}

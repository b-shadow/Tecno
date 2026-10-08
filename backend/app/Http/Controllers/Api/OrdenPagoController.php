<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Descuento;
use App\Models\Interes;
use App\Models\OrdenPago;
use App\Models\Pago;
use App\Models\SolicitudCompra;
use App\Services\CatalogoExternoDemo;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;

class OrdenPagoController extends Controller
{
    public function __construct(private readonly CatalogoExternoDemo $catalogo)
    {
    }

    public function descuentos(Request $request): JsonResponse
    {
        $this->authorizeVendedorOCoordinacion($request);

        return response()->json([
            'descuentos' => Descuento::query()->where('estado', 'activo')->orderBy('nombre')->get(),
        ]);
    }

    public function index(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        $ordenes = OrdenPago::query()
            ->with('interes', 'prospecto', 'vendedor', 'items.solicitudCompra', 'descuentos.descuento', 'pago.comprobantes')
            ->when($usuario->rol === 'vendedor', fn ($query) => $query->where('vendedor_id', $usuario->id))
            ->latest('fecha_generacion')
            ->get();

        return response()->json(['ordenes' => $ordenes]);
    }

    public function store(Request $request, Interes $interes): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        abort_if($usuario->rol !== 'vendedor', 403, 'Solo el vendedor puede generar ordenes de pago.');
        abort_if($interes->vendedor_id !== $usuario->id, 403, 'Debe tomar el seguimiento antes de generar una orden.');

        $data = $request->validate([
            'modulos' => ['required', 'array', 'min:1'],
            'modulos.*' => ['required', 'string'],
            'descuentos' => ['nullable', 'array'],
            'descuentos.*' => ['integer', 'exists:descuentos,id'],
        ]);

        $ofertas = collect($data['modulos'])
            ->unique()
            ->map(fn (string $moduloId) => $this->catalogo->buscarOferta(moduloId: $moduloId))
            ->filter()
            ->values();

        if ($ofertas->count() !== count(array_unique($data['modulos']))) {
            throw ValidationException::withMessages(['modulos' => 'Uno o mas modulos no estan disponibles.']);
        }

        $descuentos = Descuento::query()
            ->whereIn('id', $data['descuentos'] ?? [])
            ->where('estado', 'activo')
            ->get();

        $orden = DB::transaction(function () use ($interes, $usuario, $ofertas, $descuentos) {
            $subtotal = round($ofertas->sum(fn (array $oferta) => (float) $oferta['precio']), 2);
            $descuentoTotal = 0.0;

            $orden = OrdenPago::query()->create([
                'interes_id' => $interes->id,
                'prospecto_id' => $interes->prospecto_id,
                'vendedor_id' => $usuario->id,
                'subtotal' => $subtotal,
                'descuento_total' => 0,
                'total' => $subtotal,
                'estado' => 'Pendiente de pago',
                'fecha_generacion' => now(),
            ]);

            foreach ($descuentos as $descuento) {
                $monto = round($subtotal * ((float) $descuento->porcentaje / 100), 2);
                $descuentoTotal += $monto;
                $orden->descuentos()->create([
                    'descuento_id' => $descuento->id,
                    'porcentaje' => $descuento->porcentaje,
                    'monto' => $monto,
                ]);
            }

            $total = max(round($subtotal - $descuentoTotal, 2), 0);
            $orden->update(['descuento_total' => $descuentoTotal, 'total' => $total]);

            foreach ($ofertas as $oferta) {
                $modulo = $oferta['modulo'];
                $solicitud = SolicitudCompra::query()->create([
                    'prospecto_id' => $interes->prospecto_id,
                    'external_anuncio_id' => $oferta['external_anuncio_id'],
                    'external_modulo_id' => $oferta['external_modulo_id'],
                    'programa_nombre' => $oferta['programa']['nombre'],
                    'modulo_nombre' => $modulo['nombre'],
                    'modulo_descripcion' => $modulo['descripcion'],
                    'anuncio_titulo' => $oferta['titulo'],
                    'precio_acordado' => $oferta['precio'],
                    'estado' => 'pendiente',
                    'fecha' => now(),
                ]);

                $orden->items()->create([
                    'solicitud_compra_id' => $solicitud->id,
                    'external_modulo_id' => $oferta['external_modulo_id'],
                    'programa_nombre' => $oferta['programa']['nombre'],
                    'modulo_nombre' => $modulo['nombre'],
                    'modulo_descripcion' => $modulo['descripcion'],
                    'precio' => $oferta['precio'],
                ]);
            }

            $pago = Pago::query()->firstOrCreate([
                'orden_pago_id' => $orden->id,
            ], [
                'monto' => $total,
                'codigo_qr' => 'CRM-QR-ORD-'.$orden->id.'-'.Str::upper(Str::random(10)),
                'estado' => 'Pendiente de pago',
                'fecha_generacion' => now(),
            ]);

            $interes->interacciones()->create([
                'prospecto_id' => $interes->prospecto_id,
                'usuario_id' => $usuario->id,
                'tipo' => 'Orden de pago enviada',
                'descripcion' => 'Orden de pago generada por '.$total.' Bs para '.$ofertas->count().' modulo(s). El QR se envia por WhatsApp fuera del sistema.',
                'resultado' => 'Orden pendiente de comprobante',
                'fecha' => now(),
            ]);

            $interes->update([
                'estado' => 'Pago enviado',
                'ultima_actividad_en' => now(),
            ]);

            return $orden->setRelation('pago', $pago);
        });

        return response()->json([
            'orden' => $orden->load('interes', 'items.solicitudCompra', 'descuentos.descuento', 'pago.comprobantes', 'prospecto', 'vendedor'),
        ], 201);
    }

    private function authorizeVendedorOCoordinacion(Request $request): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_if(! in_array($usuario?->rol, ['administrador', 'coordinador', 'vendedor'], true), 403, 'No tiene permisos para esta operacion.');
    }
}

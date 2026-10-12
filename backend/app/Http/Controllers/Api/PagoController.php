<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\ComprobantePago;
use App\Models\Comision;
use App\Models\InscripcionComercial;
use App\Models\Interaccion;
use App\Models\OrdenPago;
use App\Models\Pago;
use App\Models\SolicitudCompra;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

class PagoController extends Controller
{
    public function generarPagoQR(Request $request): JsonResponse
    {
        $data = $request->validate([
            'solicitud_compra_id' => ['nullable', 'exists:solicitudes_compra,id', 'required_without:orden_pago_id'],
            'orden_pago_id' => ['nullable', 'exists:ordenes_pago,id', 'required_without:solicitud_compra_id'],
        ]);

        $solicitud = isset($data['solicitud_compra_id']) ? SolicitudCompra::query()->findOrFail($data['solicitud_compra_id']) : null;
        $orden = isset($data['orden_pago_id']) ? OrdenPago::query()->findOrFail($data['orden_pago_id']) : null;

        $pago = Pago::query()->firstOrCreate([
            'solicitud_compra_id' => $solicitud?->id,
            'orden_pago_id' => $orden?->id,
        ], [
            'monto' => $orden?->total ?? $solicitud->precio_acordado,
            'codigo_qr' => 'CRM-QR-'.($orden ? 'ORD-'.$orden->id : 'SOL-'.$solicitud->id).'-'.Str::upper(Str::random(10)),
            'estado' => 'Pendiente de pago',
            'fecha_generacion' => now(),
        ]);

        return response()->json(['pago' => $pago->load('solicitudCompra', 'ordenPago.items', 'ordenPago.descuentos.descuento', 'comprobantes')], 201);
    }

    public function show(Pago $pago): JsonResponse
    {
        return response()->json(['pago' => $pago->load('solicitudCompra.prospecto', 'ordenPago.prospecto', 'ordenPago.items', 'ordenPago.descuentos.descuento', 'comprobantes')]);
    }

    public function consultarPagos(Request $request): JsonResponse
    {
        $this->authorizeValidacion($request);

        $pagos = Pago::query()
            ->with('solicitudCompra.prospecto', 'ordenPago.prospecto', 'ordenPago.vendedor', 'ordenPago.items', 'ordenPago.descuentos.descuento', 'comprobantes')
            ->when($request->query('estado'), fn ($query, string $estado) => $query->where('estado', $estado))
            ->orderByDesc('created_at')
            ->get();

        return response()->json(['pagos' => $pagos]);
    }

    public function registrarComprobante(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        $data = $request->validate([
            'pago_id' => ['required', 'exists:pagos,id'],
            'archivo' => ['required', 'string'],
            'nombre_archivo' => ['nullable', 'string', 'max:255'],
            'mime' => ['nullable', 'string', 'max:120'],
            'remitente' => ['nullable', 'string', 'max:160'],
            'hora_pago' => ['nullable', 'date'],
            'observacion' => ['nullable', 'string'],
        ]);

        $pago = Pago::query()
            ->with('solicitudCompra.prospecto', 'ordenPago.prospecto', 'ordenPago.items', 'ordenPago.interes')
            ->findOrFail($data['pago_id']);

        abort_if($usuario?->rol === 'vendedor' && $pago->ordenPago?->vendedor_id !== $usuario->id, 403, 'No puede registrar comprobantes de otra orden.');
        abort_if(! in_array($usuario?->rol, ['administrador', 'coordinador', 'vendedor'], true), 403, 'No tiene permisos para registrar comprobantes.');

        if ($pago->estado === 'Pago aprobado') {
            return response()->json(['mensaje' => 'El pago ya fue aprobado.'], 422);
        }

        $comprobante = ComprobantePago::query()->create([
            ...$data,
            'fecha_envio' => now(),
            'estado_revision' => 'En revision',
        ]);

        $pago->update(['estado' => 'En revision']);
        $pago->ordenPago?->update(['estado' => 'En revision']);
        $pago->ordenPago?->interes?->update(['estado' => 'En revision', 'ultima_actividad_en' => now()]);
        $pago->ordenPago?->interes?->interacciones()->create([
            'prospecto_id' => $pago->ordenPago->prospecto_id,
            'usuario_id' => $usuario?->id,
            'tipo' => 'Pago informado',
            'descripcion' => 'El vendedor registro el comprobante recibido por WhatsApp para revision del coordinador.',
            'resultado' => 'Pago en revision',
            'fecha' => now(),
        ]);

        return response()->json([
            'comprobante' => $comprobante,
            'pago' => $pago->fresh()->load('solicitudCompra.prospecto', 'ordenPago.prospecto', 'ordenPago.items', 'comprobantes'),
        ], 201);
    }

    public function comprobantes(Pago $pago): JsonResponse
    {
        return response()->json(['comprobantes' => $pago->comprobantes()->latest()->get()]);
    }

    public function aprobar(Request $request, Pago $pago): JsonResponse
    {
        $this->authorizeValidacion($request);

        if (! $pago->comprobantes()->exists()) {
            return response()->json(['mensaje' => 'No se puede aprobar un pago sin comprobante.'], 422);
        }

        $data = $request->validate(['observacion' => ['nullable', 'string']]);

        $pago->update([
            'estado' => 'Pago aprobado',
            'fecha_validacion' => now(),
            'observacion_validacion' => $data['observacion'] ?? null,
        ]);

        $pago->comprobantes()->update(['estado_revision' => 'Pago aprobado']);
        $inscripciones = $this->registrarInscripcionesYComisiones($pago->fresh()->load('solicitudCompra.prospecto', 'ordenPago.items.solicitudCompra.prospecto', 'ordenPago.interes'));
        $pago->ordenPago?->update(['estado' => 'Pago aprobado']);
        $pago->ordenPago?->interes?->update(['estado' => 'Convertido', 'ultima_actividad_en' => now()]);
        $pago->ordenPago?->interes?->interacciones()->create([
            'prospecto_id' => $pago->ordenPago->prospecto_id,
            'usuario_id' => $request->attributes->get('auth_usuario')?->id,
            'tipo' => 'Compra validada',
            'descripcion' => 'Pago aprobado por coordinacion. La inscripcion comercial quedo confirmada.',
            'resultado' => 'Pago aprobado e inscripcion confirmada',
            'fecha' => now(),
        ]);

        return response()->json([
            'pago' => $pago->fresh()->load('comprobantes', 'ordenPago.items', 'ordenPago.prospecto'),
            'inscripciones' => $inscripciones,
        ]);
    }

    public function rechazar(Request $request, Pago $pago): JsonResponse
    {
        $this->authorizeValidacion($request);

        $data = $request->validate(['observacion' => ['required', 'string']]);

        $pago->update([
            'estado' => 'Pago rechazado',
            'fecha_validacion' => now(),
            'observacion_validacion' => $data['observacion'],
        ]);

        $pago->comprobantes()->update(['estado_revision' => 'Pago rechazado']);
        $pago->ordenPago?->update(['estado' => 'Pago rechazado']);
        $pago->ordenPago?->interes?->update(['estado' => 'Pago enviado', 'ultima_actividad_en' => now()]);

        return response()->json(['pago' => $pago->fresh()->load('comprobantes')]);
    }

    public function solicitudes(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        $solicitudes = SolicitudCompra::query()
            ->with('prospecto.vendedor', 'pago', 'inscripcionComercial', 'comision')
            ->when($usuario->rol === 'vendedor', fn ($query) => $query->whereHas('ordenItem.ordenPago', fn ($subquery) => $subquery->where('vendedor_id', $usuario->id)))
            ->orderByDesc('created_at')
            ->get();

        return response()->json(['solicitudes' => $solicitudes]);
    }

    private function authorizeValidacion(Request $request): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_if(! in_array($usuario?->rol, ['administrador', 'coordinador'], true), 403, 'No tiene permisos para validar pagos.');
    }

    /**
     * @return array{0: string, 1: string}
     */
    private function decodeArchivoBase64(string $archivo, ?string $mime): array
    {
        if (Str::startsWith($archivo, 'data:')) {
            [$metadata, $contenido] = explode(',', $archivo, 2);
            preg_match('/^data:(.*?);base64$/', $metadata, $matches);

            return [base64_decode($contenido) ?: '', $mime ?: ($matches[1] ?? 'application/octet-stream')];
        }

        return [base64_decode($archivo) ?: $archivo, $mime ?: 'application/octet-stream'];
    }

    private function registrarInscripcionesYComisiones(Pago $pago)
    {
        $solicitudes = $pago->ordenPago
            ? $pago->ordenPago->items->pluck('solicitudCompra')->filter()
            : collect([$pago->solicitudCompra])->filter();

        $inscripciones = collect();

        foreach ($solicitudes as $solicitud) {
            $inscripcion = InscripcionComercial::query()->firstOrCreate([
                'solicitud_compra_id' => $solicitud->id,
            ], [
                'prospecto_id' => $solicitud->prospecto_id,
                'fecha_confirmacion' => now(),
                'estado' => 'Confirmada',
            ]);

            $inscripciones->push($inscripcion->load('prospecto', 'solicitudCompra'));
            $solicitud->update(['estado' => 'confirmada']);
            $solicitud->prospecto?->update(['estado' => 'Convertido']);
            $vendedorId = $pago->ordenPago?->vendedor_id ?? $solicitud->prospecto?->vendedor_id;

            if ($vendedorId) {
                Comision::query()->firstOrCreate([
                    'venta_id' => $solicitud->id,
                ], [
                    'vendedor_id' => $vendedorId,
                    'porcentaje' => 2,
                    'monto' => round(((float) $solicitud->precio_acordado) * 0.02, 2),
                    'estado' => 'Pendiente',
                ]);
            }
        }

        return $inscripciones;
    }
}

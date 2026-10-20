<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Comision;
use App\Models\ComprobantePago;
use App\Models\InscripcionComercial;
use App\Models\OrdenPago;
use App\Models\Pago;
use App\Models\Prospecto;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;

class PagoController extends Controller
{
    public function generarPagoQR(Request $request): JsonResponse
    {
        $data = $request->validate([
            'orden_pago_id' => ['required', 'exists:ordenes_pago,id'],
        ]);

        $orden = OrdenPago::query()->findOrFail($data['orden_pago_id']);
        $this->authorizeOrden($request, $orden);

        $pago = Pago::query()->firstOrCreate([
            'orden_pago_id' => $orden->id,
        ], [
            'monto' => $orden->total,
            'codigo_qr' => 'CRM-QR-ORD-'.$orden->id.'-'.Str::upper(Str::random(10)),
            'estado' => 'Pendiente de pago',
            'fecha_generacion' => now(),
        ]);

        return response()->json(['pago' => $pago->load('ordenPago.items', 'ordenPago.descuentos.descuento', 'comprobantes')], 201);
    }

    public function show(Request $request, Pago $pago): JsonResponse
    {
        $this->authorizeOrden($request, $pago->ordenPago);

        return response()->json(['pago' => $pago->load('ordenPago.prospecto', 'ordenPago.items', 'ordenPago.descuentos.descuento', 'comprobantes')]);
    }

    public function consultarPagos(Request $request): JsonResponse
    {
        $this->authorizeValidacion($request);

        $pagos = Pago::query()
            ->with('ordenPago.prospecto', 'ordenPago.vendedor', 'ordenPago.items', 'ordenPago.descuentos.descuento', 'comprobantes')
            ->when($request->query('estado'), fn ($query, string $estado) => $query->where('estado', $estado))
            ->orderByDesc('created_at')
            ->get();

        return response()->json(['pagos' => $pagos]);
    }

    public function registrarComprobante(Request $request): JsonResponse
    {
        return DB::transaction(function () use ($request): JsonResponse {
            $usuario = $request->attributes->get('auth_usuario');

            $data = $request->validate([
                'pago_id' => ['required', 'exists:pagos,id'],
                'archivo' => ['required', 'string', 'max:8388608'],
                'nombre_archivo' => ['nullable', 'string', 'max:255'],
                'mime' => ['nullable', 'string', 'max:120'],
                'remitente' => ['nullable', 'string', 'max:160'],
                'hora_pago' => ['nullable', 'date'],
                'observacion' => ['nullable', 'string'],
            ]);

            $pago = Pago::query()
                ->lockForUpdate()
                ->with('ordenPago.prospecto', 'ordenPago.items', 'ordenPago.interes')
                ->findOrFail($data['pago_id']);

            abort_if($usuario?->rol === 'vendedor' && $pago->ordenPago?->vendedor_id !== $usuario->id, 403, 'No puede registrar comprobantes de otra orden.');
            abort_if(! in_array($usuario?->rol, ['administrador', 'coordinador', 'vendedor'], true), 403, 'No tiene permisos para registrar comprobantes.');

            if ($pago->estado === 'Pago aprobado') {
                return response()->json(['mensaje' => 'El pago ya fue aprobado.'], 422);
            }
            abort_if($pago->estado === 'En revision', 422, 'Ya existe un comprobante en revision. Espera la respuesta de coordinacion.');
            $data['mime'] = $this->validarComprobante($data['archivo']);

            $comprobante = ComprobantePago::query()->create([
                ...$data,
                'fecha_envio' => now(),
                'estado_revision' => 'En revision',
            ]);

            $pago->update(['estado' => 'En revision']);
            $pago->ordenPago?->update(['estado' => 'En revision']);
            $pago->ordenPago?->interes?->update(['estado' => 'En revision', 'ultima_actividad_en' => now()]);
            $pago->ordenPago?->interes?->interacciones()->create([
                'usuario_id' => $usuario?->id,
                'tipo' => 'Pago informado',
                'descripcion' => 'El vendedor registro el comprobante recibido por WhatsApp para revision del coordinador.',
                'resultado' => 'Pago en revision',
                'fecha' => now(),
            ]);

            return response()->json([
                'comprobante' => $comprobante,
                'pago' => $pago->fresh()->load('ordenPago.prospecto', 'ordenPago.items', 'comprobantes'),
            ], 201);
        });
    }

    public function comprobantes(Request $request, Pago $pago): JsonResponse
    {
        $this->authorizeOrden($request, $pago->ordenPago);

        return response()->json(['comprobantes' => $pago->comprobantes()->latest()->get()]);
    }

    public function aprobar(Request $request, Pago $pago): JsonResponse
    {
        $this->authorizeValidacion($request);

        return DB::transaction(function () use ($request, $pago): JsonResponse {
            $pago = Pago::query()->lockForUpdate()->findOrFail($pago->id);
            abort_if($pago->estado !== 'En revision', 422, 'Solo se puede aprobar un pago en revision.');

            if (! $pago->comprobantes()->exists()) {
                return response()->json(['mensaje' => 'No se puede aprobar un pago sin comprobante.'], 422);
            }

            $data = $request->validate(['observacion' => ['nullable', 'string']]);

            $pago->update([
                'estado' => 'Pago aprobado',
                'fecha_validacion' => now(),
                'observacion_validacion' => $data['observacion'] ?? null,
            ]);

            $pago->comprobantes()->where('estado_revision', 'En revision')->update(['estado_revision' => 'Pago aprobado']);
            $inscripciones = $this->registrarInscripcionesYComisiones($pago->fresh()->load('ordenPago.items', 'ordenPago.interes.prospecto'));
            $pago->ordenPago?->update(['estado' => 'Pago aprobado']);
            $pago->ordenPago?->interes?->update(['estado' => 'Convertido', 'ultima_actividad_en' => now()]);
            $pago->ordenPago?->interes?->interacciones()->create([
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
        });
    }

    public function rechazar(Request $request, Pago $pago): JsonResponse
    {
        $this->authorizeValidacion($request);

        return DB::transaction(function () use ($request, $pago): JsonResponse {
            $pago = Pago::query()->lockForUpdate()->findOrFail($pago->id);
            abort_if($pago->estado !== 'En revision', 422, 'Solo se puede rechazar un pago en revision.');

            $data = $request->validate(['observacion' => ['required', 'string']]);

            $pago->update([
                'estado' => 'Pago rechazado',
                'fecha_validacion' => now(),
                'observacion_validacion' => $data['observacion'],
            ]);

            $pago->comprobantes()->where('estado_revision', 'En revision')->update(['estado_revision' => 'Pago rechazado']);
            $pago->ordenPago?->update(['estado' => 'Pago rechazado']);
            $pago->ordenPago?->interes?->update(['estado' => 'Pago enviado', 'ultima_actividad_en' => now()]);

            return response()->json(['pago' => $pago->fresh()->load('comprobantes')]);
        });
    }

    private function authorizeOrden(Request $request, OrdenPago $orden): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_if(! in_array($usuario?->rol, ['administrador', 'coordinador', 'vendedor'], true), 403, 'No tiene permisos para consultar pagos.');
        abort_if($usuario->rol === 'vendedor' && $orden->vendedor_id !== $usuario->id, 403, 'No puede acceder a pagos de otra orden.');
    }

    private function authorizeValidacion(Request $request): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_if(! in_array($usuario?->rol, ['administrador', 'coordinador'], true), 403, 'No tiene permisos para validar pagos.');
    }

    private function registrarInscripcionesYComisiones(Pago $pago)
    {
        $orden = $pago->ordenPago;
        $inscripciones = collect();
        $prospectoId = $orden->interes->prospecto_id;
        Prospecto::query()->lockForUpdate()->findOrFail($prospectoId);

        foreach ($orden->items as $solicitud) {
            abort_if(InscripcionComercial::query()
                ->whereHas('solicitudCompra', fn ($query) => $query->where('external_modulo_id', $solicitud->external_modulo_id)
                    ->whereHas('ordenPago.interes', fn ($query) => $query->where('prospecto_id', $prospectoId)))
                ->exists(), 422, 'El prospecto ya tiene una inscripcion confirmada en este modulo.');
            $inscripcion = InscripcionComercial::query()->firstOrCreate([
                'solicitud_compra_id' => $solicitud->id,
            ], [
                'fecha_confirmacion' => now(),
                'estado' => 'Confirmada',
            ]);

            $inscripciones->push($inscripcion->load('solicitudCompra'));
            $solicitud->update(['estado' => 'confirmada']);
            Comision::registrar($solicitud->id, $orden->vendedor_id, (float) $solicitud->precio_acordado);
        }

        $orden->interes->prospecto->update(['estado' => 'Convertido']);

        return $inscripciones;
    }

    private function validarComprobante(string $archivo): string
    {
        $valido = preg_match('~^data:(image/(?:png|jpeg|gif|webp|svg\+xml)|application/pdf);base64,([A-Za-z0-9+/=\r\n]+)$~', $archivo, $partes);
        $contenido = $valido ? base64_decode($partes[2], true) : false;
        $mime = $contenido !== false ? (new \finfo(FILEINFO_MIME_TYPE))->buffer($contenido) : false;
        if (! $contenido || strlen($contenido) > 5 * 1024 * 1024 || $mime !== ($partes[1] ?? null)) {
            throw ValidationException::withMessages(['archivo' => 'Adjunta una imagen o PDF valido de hasta 5 MB.']);
        }

        return $mime;
    }
}

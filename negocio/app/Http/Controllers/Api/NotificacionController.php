<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Notificacion\EnviarNotificacionRequest;
use App\Services\NotificacionService;
use Illuminate\Http\JsonResponse;

/** CU7: correos enviados desde el CRM y su registro. */
class NotificacionController extends Controller
{
    public function __construct(private readonly NotificacionService $notificaciones)
    {
    }

    public function enviar(EnviarNotificacionRequest $r): JsonResponse
    {
        [$estado, $notificacion] = $this->notificaciones->enviar($r->usuario(), $r->validated());

        return response()->json([
            'mensaje' => $estado === 'enviada' ? 'Correo enviado.' : 'No se pudo enviar el correo; quedó registrado como fallido.',
            'notificacion' => $notificacion,
        ], 201);
    }

    public function index(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['notificaciones' => $this->notificaciones->listar($r->usuario())]);
    }

    public function marcarLeida(ConsultaRequest $r, int $notificacion): JsonResponse
    {
        return response()->json(['notificacion' => $this->notificaciones->marcarLeida($r->usuario(), $notificacion)]);
    }
}

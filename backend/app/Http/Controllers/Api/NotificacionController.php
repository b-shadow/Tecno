<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\NotificacionService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/** Adaptador HTTP del CU7: valida la petición y serializa la respuesta del servicio. */
class NotificacionController extends Controller
{
    public function enviar(Request $request, NotificacionService $service): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $datos = $request->validate([
            'destinatario' => ['required', 'email', 'max:160'],
            'tipo' => ['required', 'string', 'max:120'],
            'mensaje' => ['required', 'string', 'min:3', 'max:5000'],
        ], [], ['tipo' => 'asunto']);

        [$estado, $notificacion] = $service->enviar($usuario, $datos);

        return response()->json([
            'mensaje' => $estado === 'enviada' ? 'Correo enviado.' : 'No se pudo enviar el correo; quedó registrado como fallido.',
            'notificacion' => $notificacion,
        ], 201);
    }

    public function index(Request $request, NotificacionService $service): JsonResponse
    {
        return response()->json([
            'notificaciones' => $service->listar($request->attributes->get('auth_usuario')),
        ]);
    }

    public function marcarLeida(Request $request, int $notificacion, NotificacionService $service): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        return response()->json([
            'notificacion' => $service->marcarLeida($usuario, $notificacion),
        ]);
    }
}

<?php

namespace App\Negocio;

use App\Exceptions\ReglaNegocioException;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Notificacion\EnviarNotificacionRequest;
use Datos\DNotificacion;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Mail;

/** Capa de negocio — CU7: correos SMTP enviados desde el CRM y su registro. */
class NNotificacion
{
    public function __construct(private readonly DNotificacion $notificaciones)
    {
    }

    public function enviar(EnviarNotificacionRequest $r): JsonResponse
    {
        $usuario = $r->usuario();
        $datos = $r->validated();
        if ($usuario->rol === 'vendedor') {
            $esPropio = strcasecmp($datos['destinatario'], $usuario->correo) === 0;
            $esDeCartera = $this->notificaciones->prospectoAsignadoA($datos['destinatario'], $usuario->correo);

            if (! $esPropio && ! $esDeCartera) {
                throw new ReglaNegocioException('Solo puede escribir a prospectos de su cartera.', 403);
            }
        }

        $resultado = $this->enviarCorreo(
            $datos['destinatario'],
            $datos['tipo'],
            $datos['mensaje'],
            $usuario->correo,
            $datos['enlace'] ?? null,
            $datos['texto_boton'] ?? 'Completar pago',
        );

        if ($resultado['notificacion']->estado === 'fallida') {
            return response()->json([
                'mensaje' => 'No se pudo entregar el correo al servidor SMTP. Quedó registrado como fallido y puede reintentarlo.',
                'detalle_smtp' => $resultado['error'],
                'notificacion' => $resultado['notificacion'],
            ], 502);
        }

        return response()->json([
            'mensaje' => 'Correo aceptado por el servidor SMTP y registrado en el historial.',
            'notificacion' => $resultado['notificacion'],
        ], 201);
    }

    private function enviarCorreo(string $destinatario, string $asunto, string $mensajeTexto, ?string $usuarioCorreo, ?string $enlace = null, string $textoBoton = 'Completar pago'): array
    {
        $mailer = strtolower((string) config('mail.default'));
        $error = null;

        if (in_array($mailer, ['log', 'array'], true)) {
            $estado = 'fallida';
            $error = 'El envío real requiere MAIL_MAILER=smtp configurado (no modo log).';
        } else {
            try {
                if ($enlace) {
                    $html = $this->htmlConEnlace($asunto, $mensajeTexto, $enlace, $textoBoton);
                    Mail::html($html, function ($mensaje) use ($destinatario, $asunto, $mensajeTexto, $enlace): void {
                        $mensaje->to($destinatario)->subject($asunto);
                        $mensaje->getSymfonyMessage()->text($mensajeTexto . "\n\nEnlace: " . $enlace);
                    });
                } else {
                    Mail::raw($mensajeTexto, fn ($mensaje) => $mensaje->to($destinatario)->subject($asunto));
                }
                $estado = 'enviada';
            } catch (\Throwable $e) {
                $estado = 'fallida';
                $error = mb_substr($e->getMessage(), 0, 240);
            }
        }

        $notificacion = $this->notificaciones->crear([
            'destinatario' => $destinatario,
            'tipo' => mb_substr($asunto, 0, 120),
            'mensaje' => $mensajeTexto,
            'usuario_correo' => $usuarioCorreo,
            'estado' => $estado,
            'fecha_envio' => now(),
        ]);

        return ['notificacion' => $notificacion, 'error' => $error];
    }

    private function htmlConEnlace(string $asunto, string $mensajeTexto, string $enlace, string $textoBoton): string
    {
        $parrafos = nl2br(e($mensajeTexto));
        $url = e($enlace);
        $btn = e($textoBoton ?: 'Completar pago');
        $titulo = e($asunto);

        return <<<HTML
<!DOCTYPE html>
<html lang="es">
<body style="margin:0;padding:24px;background:#f4f7f9;font-family:'Segoe UI',Arial,sans-serif;color:#1d2733;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:600px;margin:0 auto;background:#ffffff;border:1px solid #cfd9e0;border-radius:8px;overflow:hidden;">
    <tr>
      <td style="background:#083456;padding:20px 24px;color:#ffffff;">
        <strong style="font-size:18px;letter-spacing:0.03em;">U<span style="color:#2ccfd5;">NEXO</span></strong>
        <div style="font-size:13px;color:#c7d6e3;margin-top:4px;">{$titulo}</div>
      </td>
    </tr>
    <tr>
      <td style="padding:24px;font-size:15px;line-height:1.55;">
        <div>{$parrafos}</div>
        <div style="margin:24px 0;">
          <a href="{$url}" target="_blank" rel="noopener noreferrer" style="display:inline-block;background:#10aeb5;color:#041d31;font-weight:700;text-decoration:none;padding:12px 22px;border-radius:6px;">{$btn}</a>
        </div>
        <p style="font-size:12px;color:#4e5d6b;word-break:break-all;">Si el botón no funciona, copia y abre este enlace:<br><a href="{$url}" style="color:#0b4268;">{$url}</a></p>
      </td>
    </tr>
  </table>
</body>
</html>
HTML;
    }

    public function index(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['notificaciones' => $this->notificaciones->listar($r->usuario())]);
    }

    public function marcarLeida(ConsultaRequest $r, int $notificacion): JsonResponse
    {
        $usuario = $r->usuario();
        $registro = $this->notificaciones->obtener($notificacion);

        ReglaNegocioException::si(
            $usuario->rol !== 'administrador' && $registro->usuario_correo !== $usuario->correo,
            'No puede modificar esta notificación.',
            403,
        );

        return response()->json(['notificacion' => $this->notificaciones->marcarLeida($registro)]);
    }
}

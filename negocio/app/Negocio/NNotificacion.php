<?php

namespace App\Negocio;

use App\Exceptions\ReglaNegocioException;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Notificacion\EnviarNotificacionRequest;
use Datos\DNotificacion;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\Mail;

/** Capa de negocio — CU7: correos SMTP enviados desde el CRM y su registro (incluye avisos de pago Stripe). */
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

    /** Envía confirmación al cliente y aviso al vendedor cuando Stripe confirma un pago (nunca revierte el cobro si SMTP falla). */
    public function notificarPagoConfirmado(array $datos): void
    {
        $monto = number_format((float) ($datos['monto'] ?? 0), 2, '.', '');
        $orden = (int) ($datos['nro_orden'] ?? 0);
        $cuota = (int) ($datos['nro_cuota'] ?? 1);
        $totalCuotas = (int) ($datos['total_cuotas'] ?? 1);
        $referencia = (string) ($datos['referencia'] ?? '');
        $programa = (string) ($datos['programa'] ?? 'Programa educativo');
        $modulo = (string) ($datos['modulo'] ?? '');
        $clienteNombre = (string) ($datos['cliente_nombre'] ?? 'Cliente');
        $clienteCorreo = trim((string) ($datos['cliente_correo'] ?? ''));
        $vendedorCorreo = trim((string) ($datos['vendedor_correo'] ?? ''));
        $fecha = Carbon::now('America/La_Paz')->format('d/m/Y H:i');

        if ($clienteCorreo !== '' && filter_var($clienteCorreo, FILTER_VALIDATE_EMAIL)) {
            $asuntoCliente = "UNEXO — Confirmación de pago (Orden #{$orden} · Cuota {$cuota})";
            if (! $this->notificaciones->existeNotificacionEnviada($clienteCorreo, $asuntoCliente, $referencia ?: "Orden #{$orden}")) {
                $cuerpoCliente = implode("\n", [
                    "Hola, {$clienteNombre}.",
                    '',
                    'Te confirmamos que tu pago fue procesado correctamente mediante Stripe Sandbox.',
                    '',
                    "Programa: {$programa}" . ($modulo ? " — {$modulo}" : ''),
                    "Orden: #{$orden}",
                    "Cuota: {$cuota} de {$totalCuotas}",
                    "Importe: Bs {$monto} (BOB)",
                    "Referencia de pago: {$referencia}",
                    "Fecha: {$fecha}",
                    '',
                    'Operación de demostración mediante Stripe Sandbox (sin cobro de dinero real).',
                    'Gracias por confiar en UNEXO.',
                ]);
                $this->enviarCorreo($clienteCorreo, $asuntoCliente, $cuerpoCliente, $vendedorCorreo ?: null);
            }
        }

        if ($vendedorCorreo !== '' && filter_var($vendedorCorreo, FILTER_VALIDATE_EMAIL)) {
            $asuntoVendedor = "UNEXO — Pago confirmado de {$clienteNombre} (Orden #{$orden} · Cuota {$cuota})";
            if (! $this->notificaciones->existeNotificacionEnviada($vendedorCorreo, $asuntoVendedor, $referencia ?: "Orden #{$orden}")) {
                $cuerpoVendedor = implode("\n", [
                    "El cliente {$clienteNombre} completó el pago mediante Stripe Sandbox.",
                    '',
                    "Programa: {$programa}" . ($modulo ? " — {$modulo}" : ''),
                    "Orden: #{$orden} · Cuota {$cuota} de {$totalCuotas}",
                    "Importe confirmado: Bs {$monto} (BOB)",
                    "Referencia Stripe: {$referencia}",
                    "Fecha: {$fecha}",
                    '',
                    'La cuota y el saldo en UNEXO ya fueron actualizados automáticamente.',
                ]);
                $this->enviarCorreo($vendedorCorreo, $asuntoVendedor, $cuerpoVendedor, $vendedorCorreo);
            }
        }
    }

    /** Método reutilizable interno para envíos programados y avisos iniciales de pago vía SMTP. */
    public function enviarCorreoSistema(string $destinatario, string $asunto, string $mensajeTexto, ?string $usuarioCorreo, ?string $enlace = null, string $textoBoton = 'Completar pago'): array
    {
        return $this->enviarCorreo($destinatario, $asunto, $mensajeTexto, $usuarioCorreo, $enlace, $textoBoton);
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

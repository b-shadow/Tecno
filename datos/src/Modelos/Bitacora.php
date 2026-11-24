<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Http\Request;

class Bitacora extends Model
{
    protected $table = 'bitacora';

    protected $primaryKey = 'nro_registro';

    public $timestamps = false;

    protected $guarded = [];

    public const EVENTOS = ['login_exitoso', 'login_fallido', 'logout', 'visita', 'acceso_denegado'];

    protected function casts(): array
    {
        return ['fecha' => 'datetime'];
    }

    public static function registrar(string $evento, Request $request, ?string $usuario = null, ?string $recurso = null, ?string $correoIntentado = null): void
    {
        self::query()->insert([
            'evento' => $evento,
            'usuario_correo' => $usuario,
            'correo_intentado' => $correoIntentado !== null ? mb_substr($correoIntentado, 0, 255) : null,
            'recurso_codigo' => $recurso,
            'ip' => (string) $request->ip(),
            'navegador' => mb_substr((string) $request->userAgent(), 0, 255) ?: null,
        ]);
    }
}

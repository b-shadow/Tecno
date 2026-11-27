<?php

namespace Datos;

use Datos\Modelos\Bitacora;

/** Escritura de la bitácora de auditoría (enunciado 4): logins, fallos, visitas y accesos denegados con su IP. */
class DBitacora
{
    public function registrar(string $evento, string $ip, ?string $navegador, ?string $usuario = null, ?string $recurso = null, ?string $correoIntentado = null): void
    {
        Bitacora::query()->insert([
            'evento' => $evento,
            'usuario_correo' => $usuario,
            'correo_intentado' => $correoIntentado !== null ? mb_substr($correoIntentado, 0, 255) : null,
            'recurso_codigo' => $recurso,
            'ip' => $ip,
            'navegador' => $navegador,
        ]);
    }
}

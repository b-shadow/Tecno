<?php

namespace App\Services;

use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;

/**
 * Fotos de usuario (CU1). Clase 40 del docente: nombre de archivo legible y ligado al dato (perez_juan.jpg),
 * guardado en la BD. Llegan como data URL (base64) desde el formulario React.
 */
class Fotos
{
    private const TIPOS = ['image/jpeg' => 'jpg', 'image/png' => 'png', 'image/webp' => 'webp'];

    public const MAX_BYTES = 2 * 1024 * 1024;

    public static function directorio(): string
    {
        return storage_path('app/fotos');
    }

    public static function guardar(string $dataUrl, string $apellido, string $nombre, ?string $anterior = null): string
    {
        if (! preg_match('/^data:([\w\/+.-]+);base64,(.+)$/s', $dataUrl, $m)) {
            throw ValidationException::withMessages(['foto' => 'La foto no tiene un formato válido.']);
        }

        $contenido = base64_decode($m[2], true);
        $mime = $contenido === false ? null : (new \finfo(FILEINFO_MIME_TYPE))->buffer($contenido);

        if (! isset(self::TIPOS[$mime])) {
            throw ValidationException::withMessages(['foto' => 'La foto debe ser una imagen JPG, PNG o WEBP.']);
        }
        if (strlen($contenido) > self::MAX_BYTES) {
            throw ValidationException::withMessages(['foto' => 'La foto no debe superar 2 MB.']);
        }

        $base = Str::slug($apellido.' '.$nombre, '_') ?: 'usuario';
        $archivo = $base.'.'.self::TIPOS[$mime];
        // Dos personas con el mismo nombre: la segunda se numera (perez_juan_2.jpg).
        for ($n = 2; file_exists(self::directorio().'/'.$archivo) && $archivo !== $anterior; $n++) {
            $archivo = "{$base}_{$n}.".self::TIPOS[$mime];
        }

        if (! is_dir(self::directorio())) {
            mkdir(self::directorio(), 0775, true);
        }
        file_put_contents(self::directorio().'/'.$archivo, $contenido);

        if ($anterior && $anterior !== $archivo) {
            @unlink(self::directorio().'/'.basename($anterior));
        }

        return $archivo;
    }

    /** Ruta absoluta de una foto guardada, o null si el nombre no es válido. */
    public static function ruta(string $archivo): ?string
    {
        $ruta = self::directorio().'/'.basename($archivo);

        return basename($archivo) === $archivo && is_file($ruta) ? $ruta : null;
    }
}

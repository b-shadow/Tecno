<?php

namespace App\Services;

use App\Exceptions\ReglaNegocioException;
use Datos\Modelos\CatalogoCache;
use Datos\Modelos\Prospecto;
use Datos\Modelos\Usuario;
use Datos\Repositorios\ProspectoRepository;
use Illuminate\Database\UniqueConstraintViolationException;
use Illuminate\Support\Collection;
use Illuminate\Support\Str;
use Illuminate\Validation\Rule;
use Illuminate\Validation\ValidationException;

/** CU2 (registro de interés desde el catálogo) y CU3 (RF2.1 alta manual o CSV, RF2.2 interés del catálogo). */
class ProspectoService
{
    /** Origen del lead (RF2.1), los mismos que acepta el P1. */
    public const ORIGENES = ['Facebook', 'Instagram', 'TikTok', 'WhatsApp', 'Referido', 'Web', 'Correo', 'Feria', 'Otro'];

    public const CAMPOS_CSV = ['documento', 'nombre', 'apellido', 'telefono', 'correo', 'origen'];

    /** Columnas opcionales del CSV: el interés con el que el prospecto entra al embudo (RF2.2). */
    public const CAMPOS_CSV_INTERES = ['modulo_codigo', 'programa_codigo'];

    public const ATRIBUTOS = [
        'documento' => 'carnet de identidad', 'telefono' => 'teléfono', 'profesion' => 'profesión', 'ubicacion' => 'ciudad',
        'modulo_codigo' => 'módulo', 'programa_codigo' => 'programa', 'origen' => 'origen del contacto',
    ];

    public function __construct(private readonly ProspectoRepository $prospectos)
    {
    }

    /** Reglas de los datos personales del prospecto: las usan los FormRequest y la validación de cada fila del CSV. */
    public static function reglasPersona(): array
    {
        return [
            'documento' => ['required', 'string', 'max:20', 'regex:/^[0-9A-Za-z-]+$/'],
            'nombre' => ['required', 'string', 'max:120', "regex:/^[\\pL\\s'.-]+$/u"],
            'apellido' => ['required', 'string', 'max:120', "regex:/^[\\pL\\s'.-]+$/u"],
            'correo' => ['required', 'email', 'max:160'],
            'telefono' => ['required', 'string', 'regex:/^\\+?[0-9 ]{7,20}$/'],
            'profesion' => ['nullable', 'string', 'max:120'],
            'ubicacion' => ['nullable', 'string', 'max:160'],
        ];
    }

    /**
     * Formulario público del catálogo: un interés por módulo, o por cada módulo si elige el programa completo.
     * Devuelve true si el prospecto es nuevo.
     */
    public function registrarInteres(array $datos): bool
    {
        $modulos = $this->modulosSolicitados($datos);

        try {
            return $this->prospectos->transaccion(function () use ($datos, $modulos) {
                $prospecto = $this->prospectos->encontrarPorDocumentoOCorreoBloqueado($datos['documento'], $datos['correo']);
                $creado = ! $prospecto;

                if ($creado) {
                    $prospecto = $this->prospectos->crear($this->soloPersona($datos) + ['origen' => 'Web', 'estado' => 'Nuevo', 'fecha_registro' => now()]);
                } elseif ($prospecto->documento !== $datos['documento'] || strcasecmp($prospecto->correo, $datos['correo']) !== 0) {
                    throw ValidationException::withMessages(['correo' => 'Ese correo o carnet ya está registrado con otros datos. Comuníquese con coordinación.']);
                }

                $this->crearIntereses($prospecto, $modulos);

                return $creado;
            });
        } catch (UniqueConstraintViolationException) {
            throw ValidationException::withMessages(['correo' => 'Su registro se está procesando. Intente nuevamente en unos segundos.']);
        }
    }

    public function listar(Usuario $usuario, string $buscar, ?string $origen): Collection
    {
        return $this->prospectos->buscar($usuario, trim($buscar), $origen);
    }

    /** RF2.1 alta manual, con su primer interés opcional. La hace quien puede repartir prospectos. */
    public function registrar(Usuario $usuario, array $datos): Prospecto
    {
        $this->autorizarAlta($usuario);

        $prospecto = $this->prospectos->transaccion(function () use ($datos) {
            $prospecto = $this->prospectos->crear($this->soloPersona($datos) + ['origen' => $datos['origen'], 'estado' => 'Nuevo', 'fecha_registro' => now()]);
            if (! empty($datos['modulo_codigo']) || ! empty($datos['programa_codigo'])) {
                $this->crearIntereses($prospecto, $this->modulosSolicitados($datos));
            }

            return $prospecto;
        });

        return $this->prospectos->conIntereses($prospecto);
    }

    public function actualizar(Usuario $usuario, Prospecto $prospecto, array $datos): Prospecto
    {
        ReglaNegocioException::si(! $this->prospectos->estaDentroDeCartera($prospecto, $usuario), 'Este prospecto no está dentro de su cartera.', 403);
        $this->prospectos->actualizar($prospecto, $datos);

        return $this->prospectos->actualizado($prospecto);
    }

    /** RF2.2: nuevo interés de un prospecto existente (módulo independiente o programa completo). */
    public function crearInteres(Usuario $usuario, Prospecto $prospecto, array $datos): Collection
    {
        ReglaNegocioException::si($usuario->rol === 'vendedor' && ! $this->prospectos->estaDentroDeCartera($prospecto, $usuario), 'Este prospecto no está dentro de su cartera.', 403);

        return $this->prospectos->transaccion(function () use ($prospecto, $datos, $usuario) {
            $vendedor = $usuario->rol === 'vendedor' ? $usuario->correo : null;

            return $this->crearIntereses($prospecto, $this->modulosSolicitados($datos), $vendedor);
        });
    }

    /**
     * RF2.1 carga masiva. Todo o nada: si una fila tiene errores no se carga ninguna.
     * Con modulo_codigo o programa_codigo la fila entra también al embudo (tarjeta Nuevo, lista para el Round-Robin).
     * Devuelve la cantidad de prospectos creados.
     */
    public function importarCSV(Usuario $usuario, string $csv): int
    {
        $this->autorizarAlta($usuario);
        $filas = $this->leerCsv($csv);
        $cabecera = array_shift($filas) ?? [];
        $faltan = array_values(array_diff(self::CAMPOS_CSV, $cabecera));

        ReglaNegocioException::si((bool) $faltan, 'Al archivo le faltan columnas obligatorias: '.implode(', ', $faltan).'.', 422, [
            'columnas_requeridas' => self::CAMPOS_CSV,
            'errores' => array_map(fn ($c) => ['columna' => $c, 'error' => 'Columna obligatoria ausente'], $faltan),
        ]);
        if (count($cabecera) !== count(array_unique($cabecera))) {
            throw ValidationException::withMessages(['csv' => 'El archivo tiene columnas repetidas.']);
        }

        $errores = [];
        $registros = [];
        foreach ($filas as $i => $valores) {
            $linea = $i + 2;
            if ($valores === [null] || $valores === ['']) {
                continue;
            }
            if (count($valores) !== count($cabecera)) {
                $errores[] = ['fila' => $linea, 'error' => 'La fila no tiene la misma cantidad de columnas que la cabecera'];

                continue;
            }
            $fila = array_combine($cabecera, array_map(fn ($v) => trim((string) $v), $valores));
            $fila['correo'] = mb_strtolower($fila['correo']);
            $fila['origen'] = collect(self::ORIGENES)->first(fn ($o) => strcasecmp($o, $fila['origen']) === 0) ?? $fila['origen'];

            $validador = validator($fila, self::reglasPersona() + ['origen' => ['required', Rule::in(self::ORIGENES)]], [], self::ATRIBUTOS);
            foreach ($validador->errors()->messages() as $columna => $mensajes) {
                $errores[] = ['fila' => $linea, 'columna' => $columna, 'error' => $mensajes[0]];
            }
            if ($this->prospectos->existeDocumentoOCorreo($fila['documento'], $fila['correo'])) {
                $errores[] = ['fila' => $linea, 'error' => 'El carnet o el correo ya están registrados'];
            }
            $fila['modulos'] = collect();
            if (! empty($fila['modulo_codigo']) || ! empty($fila['programa_codigo'])) {
                $fila['modulos'] = $this->prospectos->modulosSolicitados($fila);
                if ($fila['modulos']->isEmpty()) {
                    $errores[] = ['fila' => $linea, 'columna' => 'modulo_codigo', 'error' => 'El módulo o programa no existe o no está abierto'];
                }
            }
            $registros[] = $fila;
        }

        if (! $registros) {
            $errores[] = ['fila' => 2, 'error' => 'El archivo no contiene registros'];
        }
        foreach (['documento' => 'Carnet', 'correo' => 'Correo'] as $campo => $nombre) {
            foreach (collect($registros)->pluck($campo)->filter()->duplicates()->unique() as $repetido) {
                $errores[] = ['columna' => $campo, 'error' => "{$nombre} repetido dentro del archivo: {$repetido}"];
            }
        }

        ReglaNegocioException::si((bool) $errores, 'El archivo tiene errores; no se cargó ningún prospecto.', 422, [
            'columnas_requeridas' => self::CAMPOS_CSV, 'columnas_opcionales' => self::CAMPOS_CSV_INTERES, 'errores' => $errores,
        ]);

        $this->prospectos->transaccion(function () use ($registros) {
            foreach ($registros as $fila) {
                $prospecto = $this->prospectos->crear($this->soloPersona($fila) + ['origen' => $fila['origen'], 'estado' => 'Nuevo', 'fecha_registro' => now()]);
                $this->crearIntereses($prospecto, $fila['modulos']);
            }
        });

        return count($registros);
    }

    /** @return Collection<int, CatalogoCache> */
    private function modulosSolicitados(array $datos): Collection
    {
        $modulos = $this->prospectos->modulosSolicitados($datos);

        if ($modulos->isEmpty() || (isset($datos['modulo_codigos']) && $modulos->count() !== count($datos['modulo_codigos']))) {
            throw ValidationException::withMessages(['modulo_codigos' => 'Uno o más módulos seleccionados ya no están disponibles. Revise la selección.']);
        }
        if (isset($datos['modulo_codigos']) && $modulos->pluck('programa_codigo')->unique()->count() > 1) {
            throw ValidationException::withMessages(['modulo_codigos' => 'Seleccione módulos de un solo programa por registro.']);
        }

        return $modulos;
    }

    private function crearIntereses(Prospecto $prospecto, Collection $modulos, ?string $vendedor = null): Collection
    {
        // Todas las tarjetas de un prospecto quedan con el mismo vendedor (si ya tiene uno).
        $vendedor ??= $this->prospectos->vendedorExistente($prospecto);

        return $modulos->map(fn (CatalogoCache $m) => $this->prospectos->crearInteres($prospecto, $m, $vendedor));
    }

    private function soloPersona(array $datos): array
    {
        return collect($datos)->only(['documento', 'nombre', 'apellido', 'correo', 'telefono', 'profesion', 'ubicacion'])
            ->map(fn ($v) => is_string($v) ? trim($v) : $v)->all();
    }

    private function leerCsv(string $texto): array
    {
        $texto = preg_replace('/^\xEF\xBB\xBF/', '', $texto);
        $separador = substr_count(strtok($texto, "\n") ?: '', ';') > substr_count(strtok($texto, "\n") ?: '', ',') ? ';' : ',';
        $stream = fopen('php://temp', 'r+');
        fwrite($stream, $texto);
        rewind($stream);
        $filas = [];
        while (($valores = fgetcsv($stream, 0, $separador, '"', '')) !== false) {
            $filas[] = $valores;
        }
        fclose($stream);

        if ($filas) {
            $filas[0] = array_map(fn ($c) => match ($c = Str::ascii(Str::lower(trim((string) $c)))) {
                'nombres' => 'nombre', 'apellidos' => 'apellido', 'ci', 'carnet' => 'documento', 'celular' => 'telefono', 'email' => 'correo',
                'modulo' => 'modulo_codigo', 'programa' => 'programa_codigo',
                default => $c,
            }, $filas[0]);
        }

        return $filas;
    }

    private function autorizarAlta(Usuario $usuario): void
    {
        // Registrar o importar prospectos lo hace quien puede repartirlos (matriz: interesados, modificación).
        ReglaNegocioException::si(! AccesoService::permite($usuario, 'interesados', 'modificacion'), 'Solo coordinación registra e importa prospectos.', 403);
    }
}

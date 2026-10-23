<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\CatalogoCache;
use App\Models\Interes;
use App\Models\Prospecto;
use App\Services\Acceso;
use App\Services\Alcance;
use Illuminate\Database\UniqueConstraintViolationException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Illuminate\Validation\Rule;
use Illuminate\Validation\ValidationException;

/** CU2 (registro de interés desde el catálogo) y CU3 (RF2.1 alta manual o CSV, RF2.2 interés del catálogo). */
class ProspectoController extends Controller
{
    /** Origen del lead (RF2.1), los mismos que acepta el P1. */
    public const ORIGENES = ['Facebook', 'Instagram', 'TikTok', 'WhatsApp', 'Referido', 'Web', 'Correo', 'Feria', 'Otro'];

    private const CAMPOS_CSV = ['documento', 'nombre', 'apellido', 'telefono', 'correo', 'origen'];

    /** Formulario público del catálogo: un interés por módulo, o por cada módulo si elige el programa completo. */
    public function registrarInteres(Request $request): JsonResponse
    {
        $request->merge(['correo' => mb_strtolower(trim((string) $request->input('correo')))]);
        $data = $request->validate([
            'modulo_codigo' => ['nullable', 'string', 'required_without:programa_codigo'],
            'programa_codigo' => ['nullable', 'string'],
        ] + $this->reglasPersona(), [], $this->atributos());

        $modulos = $this->modulosSolicitados($data);

        try {
            $creado = DB::transaction(function () use ($data, $modulos) {
                $prospecto = Prospecto::query()->lockForUpdate()->find($data['documento'])
                    ?? Prospecto::query()->whereRaw('lower(correo) = ?', [$data['correo']])->lockForUpdate()->first();
                $creado = ! $prospecto;

                if ($creado) {
                    $prospecto = Prospecto::query()->create($this->soloPersona($data) + ['origen' => 'Web', 'estado' => 'Nuevo', 'fecha_registro' => now()]);
                } elseif ($prospecto->documento !== $data['documento'] || strcasecmp($prospecto->correo, $data['correo']) !== 0) {
                    throw ValidationException::withMessages(['correo' => 'Ese correo o carnet ya está registrado con otros datos. Comuníquese con coordinación.']);
                }

                $this->crearIntereses($prospecto, $modulos);

                return $creado;
            });
        } catch (UniqueConstraintViolationException) {
            throw ValidationException::withMessages(['correo' => 'Su registro se está procesando. Intente nuevamente en unos segundos.']);
        }

        return response()->json([
            'mensaje' => 'Interés registrado correctamente.',
            'detalle' => 'Un asesor se comunicará con usted por WhatsApp.',
            'nuevo_prospecto' => $creado,
        ], $creado ? 201 : 200);
    }

    public function index(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $buscar = trim((string) $request->query('buscar', ''));

        $prospectos = Alcance::prospectos(Prospecto::query(), $usuario)
            ->with(['intereses' => fn ($q) => Alcance::intereses($q, $usuario)->with('vendedor:correo,nombre,apellido')])
            ->when($buscar !== '', fn ($q) => $q->where(fn ($s) => $s
                ->where('nombre', 'ilike', "%{$buscar}%")->orWhere('apellido', 'ilike', "%{$buscar}%")
                ->orWhere('correo', 'ilike', "%{$buscar}%")->orWhere('documento', 'ilike', "%{$buscar}%")
                ->orWhere('telefono', 'ilike', "%{$buscar}%")))
            ->when($request->query('origen'), fn ($q, $origen) => $q->where('origen', $origen))
            ->orderByDesc('fecha_registro')
            ->get();

        return response()->json(['prospectos' => $prospectos, 'origenes' => self::ORIGENES]);
    }

    /** RF2.1 alta manual, con su primer interés opcional. La crea quien puede repartir prospectos. */
    public function store(Request $request): JsonResponse
    {
        $this->autorizarAlta($request);
        $request->merge(['correo' => mb_strtolower(trim((string) $request->input('correo')))]);
        $data = $request->validate($this->reglasPersona() + [
            'documento' => ['required', 'string', 'max:20', 'regex:/^[0-9A-Za-z-]+$/', 'unique:prospectos,documento'],
            'correo' => ['required', 'email', 'max:160', Rule::unique('prospectos', 'correo')],
            'origen' => ['required', Rule::in(self::ORIGENES)],
            'modulo_codigo' => ['nullable', 'string'],
            'programa_codigo' => ['nullable', 'string'],
        ], [], $this->atributos());

        $prospecto = DB::transaction(function () use ($data) {
            $prospecto = Prospecto::query()->create($this->soloPersona($data) + ['origen' => $data['origen'], 'estado' => 'Nuevo', 'fecha_registro' => now()]);
            if (! empty($data['modulo_codigo']) || ! empty($data['programa_codigo'])) {
                $this->crearIntereses($prospecto, $this->modulosSolicitados($data));
            }

            return $prospecto;
        });

        return response()->json(['mensaje' => 'Prospecto registrado correctamente.', 'prospecto' => $prospecto->load('intereses')], 201);
    }

    public function update(Request $request, Prospecto $prospecto): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_unless(Alcance::prospectos(Prospecto::query()->whereKey($prospecto->documento), $usuario)->exists(), 403, 'Este prospecto no está dentro de su cartera.');
        $request->merge(['correo' => mb_strtolower(trim((string) $request->input('correo')))]);

        $data = $request->validate([
            'correo' => ['required', 'email', 'max:160', Rule::unique('prospectos', 'correo')->ignore($prospecto->documento, 'documento')],
            'origen' => ['required', Rule::in(self::ORIGENES)],
        ] + collect($this->reglasPersona())->except(['documento', 'correo'])->all(), [], $this->atributos());

        $prospecto->update($data);

        return response()->json(['mensaje' => 'Datos del prospecto actualizados.', 'prospecto' => $prospecto->fresh()]);
    }

    /** RF2.2: nuevo interés de un prospecto existente (módulo independiente o programa completo). */
    public function crearInteres(Request $request, Prospecto $prospecto): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_unless($usuario->rol !== 'vendedor' || Alcance::prospectos(Prospecto::query()->whereKey($prospecto->documento), $usuario)->exists(), 403, 'Este prospecto no está dentro de su cartera.');
        $data = $request->validate([
            'modulo_codigo' => ['nullable', 'string', 'required_without:programa_codigo'],
            'programa_codigo' => ['nullable', 'string'],
        ], [], $this->atributos());

        $nuevos = DB::transaction(function () use ($prospecto, $data, $usuario) {
            $vendedor = $usuario->rol === 'vendedor' ? $usuario->correo : null;

            return $this->crearIntereses($prospecto, $this->modulosSolicitados($data), $vendedor);
        });

        return response()->json(['mensaje' => 'Interés registrado.', 'intereses' => $nuevos], 201);
    }

    /** RF2.1 carga masiva. Todo o nada: si una fila tiene errores no se carga ninguna. */
    public function importarCSV(Request $request): JsonResponse
    {
        $this->autorizarAlta($request);
        $data = $request->validate(['csv' => ['required', 'string', 'max:2097152']], [], ['csv' => 'archivo CSV']);

        $filas = $this->leerCsv($data['csv']);
        $cabecera = array_shift($filas) ?? [];
        $faltan = array_values(array_diff(self::CAMPOS_CSV, $cabecera));

        if ($faltan) {
            return response()->json([
                'mensaje' => 'Al archivo le faltan columnas obligatorias: '.implode(', ', $faltan).'.',
                'columnas_requeridas' => self::CAMPOS_CSV,
                'errores' => array_map(fn ($c) => ['columna' => $c, 'error' => 'Columna obligatoria ausente'], $faltan),
            ], 422);
        }
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

            $validador = validator($fila, $this->reglasPersona() + ['origen' => ['required', Rule::in(self::ORIGENES)]], [], $this->atributos());
            foreach ($validador->errors()->messages() as $columna => $mensajes) {
                $errores[] = ['fila' => $linea, 'columna' => $columna, 'error' => $mensajes[0]];
            }
            if (Prospecto::query()->whereKey($fila['documento'])->orWhereRaw('lower(correo) = ?', [$fila['correo']])->exists()) {
                $errores[] = ['fila' => $linea, 'error' => 'El carnet o el correo ya están registrados'];
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

        if ($errores) {
            return response()->json(['mensaje' => 'El archivo tiene errores; no se cargó ningún prospecto.', 'columnas_requeridas' => self::CAMPOS_CSV, 'errores' => $errores], 422);
        }

        DB::transaction(function () use ($registros) {
            foreach ($registros as $fila) {
                Prospecto::query()->create($this->soloPersona($fila) + ['origen' => $fila['origen'], 'estado' => 'Nuevo', 'fecha_registro' => now()]);
            }
        });

        return response()->json(['mensaje' => count($registros).' prospecto(s) cargados.', 'creados' => count($registros), 'errores' => []]);
    }

    /** @return Collection<int, CatalogoCache> */
    private function modulosSolicitados(array $data): Collection
    {
        $modulos = CatalogoCache::query()->where('estado', 'abierto')
            ->when(! empty($data['modulo_codigo']), fn ($q) => $q->whereKey($data['modulo_codigo']))
            ->when(empty($data['modulo_codigo']), fn ($q) => $q->where('programa_codigo', $data['programa_codigo'] ?? ''))
            ->with('programa')
            ->get();

        if ($modulos->isEmpty()) {
            throw ValidationException::withMessages(['modulo_codigo' => 'Seleccione un programa o módulo con inscripciones abiertas.']);
        }

        return $modulos;
    }

    private function crearIntereses(Prospecto $prospecto, Collection $modulos, ?string $vendedor = null): Collection
    {
        // Todas las tarjetas de un prospecto quedan con el mismo vendedor (si ya tiene uno).
        $vendedor ??= $prospecto->intereses()->whereNotNull('vendedor_correo')->value('vendedor_correo');

        return $modulos->map(fn (CatalogoCache $m) => Interes::query()->firstOrCreate(
            ['documento' => $prospecto->documento, 'modulo_codigo' => $m->codigo],
            [
                'anuncio_codigo' => $m->anuncio_codigo,
                'programa_nombre' => $m->programa->nombre,
                'modulo_nombre' => $m->nombre,
                'modulo_descripcion' => $m->descripcion,
                'precio' => $m->precio,
                'estado' => 'Nuevo',
                'fecha' => now(),
                'vendedor_correo' => $vendedor,
                'fecha_asignacion' => $vendedor ? now() : null,
            ],
        ));
    }

    private function reglasPersona(): array
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

    private function soloPersona(array $data): array
    {
        return collect($data)->only(['documento', 'nombre', 'apellido', 'correo', 'telefono', 'profesion', 'ubicacion'])
            ->map(fn ($v) => is_string($v) ? trim($v) : $v)->all();
    }

    private function atributos(): array
    {
        return ['documento' => 'carnet de identidad', 'telefono' => 'teléfono', 'profesion' => 'profesión', 'ubicacion' => 'ciudad',
            'modulo_codigo' => 'módulo', 'programa_codigo' => 'programa', 'origen' => 'origen del contacto'];
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
                default => $c,
            }, $filas[0]);
        }

        return $filas;
    }

    private function autorizarAlta(Request $request): void
    {
        // Registrar o importar prospectos lo hace quien puede repartirlos (matriz: interesados, modificación).
        abort_unless(Acceso::permite($request->attributes->get('auth_usuario'), 'interesados', 'modificacion'), 403, 'Solo coordinación registra e importa prospectos.');
    }
}

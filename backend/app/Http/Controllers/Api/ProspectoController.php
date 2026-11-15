<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Interes;
use App\Models\Prospecto;
use App\Services\CatalogoExternoDemo;
use Illuminate\Database\UniqueConstraintViolationException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Illuminate\Validation\Rule;
use Illuminate\Validation\ValidationException;

class ProspectoController extends Controller
{
    public function __construct(private readonly CatalogoExternoDemo $catalogo) {}

    public function registrarInteres(Request $request): JsonResponse
    {
        $request->merge(['correo' => mb_strtolower(trim((string) $request->input('correo')))]);
        $data = $request->validate([
            'anuncio_id' => ['nullable', 'string'],
            'modulo_id' => ['nullable', 'string'],
            'programa_id' => ['nullable', 'string', 'required_without_all:anuncio_id,modulo_id'],
            'nombre' => ['required', 'string', 'max:120'],
            'apellido' => ['required', 'string', 'max:120'],
            'documento' => ['required', 'string', 'max:60'],
            'correo' => ['required', 'email', 'max:160'],
            'telefono' => ['required', 'string', 'max:40'],
            'profesion' => ['required', 'string', 'max:120'],
            'ubicacion' => ['required', 'string', 'max:160'],
        ]);

        // Interes por programa completo: un interes por cada modulo del programa.
        $ofertas = ! empty($data['programa_id']) && empty($data['modulo_id']) && empty($data['anuncio_id'])
            ? $this->catalogo->ofertasDePrograma($data['programa_id'])
            : collect([$this->resolveOferta($data)]);

        if ($ofertas->isEmpty()) {
            throw ValidationException::withMessages(['programa_id' => 'Debe seleccionar un programa disponible.']);
        }

        try {
            [$prospecto, $interes, $created] = DB::transaction(function () use ($data, $ofertas) {
                $prospecto = Prospecto::query()
                    ->where('documento', $data['documento'])
                    ->orWhereRaw('lower(correo) = ?', [$data['correo']])
                    ->lockForUpdate()
                    ->first();

                $created = false;

                if (! $prospecto) {
                    $prospecto = Prospecto::query()->create([
                        'nombre' => $data['nombre'],
                        'apellido' => $data['apellido'],
                        'documento' => $data['documento'],
                        'correo' => $data['correo'],
                        'telefono' => $data['telefono'],
                        'profesion' => $data['profesion'],
                        'ubicacion' => $data['ubicacion'],
                        'estado' => 'Nuevo',
                        'fecha_registro' => now(),
                    ]);
                    $created = true;
                } elseif ($prospecto->documento !== $data['documento'] || strcasecmp($prospecto->correo, $data['correo']) !== 0) {
                    throw ValidationException::withMessages(['correo' => 'No se pudo registrar el interes con esos datos. Contacta a coordinacion.']);
                }

                $intereses = $ofertas->map(function (array $oferta) use ($prospecto) {
                    $modulo = $oferta['modulo'];
                    $interes = Interes::query()->firstOrCreate([
                        'prospecto_id' => $prospecto->id,
                        'external_modulo_id' => $modulo['external_modulo_id'],
                    ], [
                        'external_anuncio_id' => $oferta['external_anuncio_id'],
                        'programa_nombre' => $modulo['programa']['nombre'],
                        'modulo_nombre' => $modulo['nombre'],
                        'modulo_descripcion' => $modulo['descripcion'],
                        'precio' => $oferta['precio'],
                        'estado' => 'Nuevo',
                        'fecha' => now(),
                    ]);

                    return $interes;
                });

                return [$prospecto, $intereses->first(), $created];
            });
        } catch (UniqueConstraintViolationException) {
            throw ValidationException::withMessages(['correo' => 'El registro ya esta siendo procesado. Intenta nuevamente.']);
        }

        return response()->json([
            'mensaje' => 'Interes registrado correctamente. Un vendedor tomara seguimiento y se comunicara por WhatsApp.',
            'nuevo_prospecto' => $created,
        ], $created ? 201 : 200);
    }

    public function index(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        $query = Prospecto::query()
            ->with(['intereses' => fn ($query) => $query
                ->when($usuario->rol === 'vendedor', fn ($query) => $query->where('vendedor_id', $usuario->id))
                ->with('vendedor', 'ordenesPago.pago')])
            ->when($usuario->rol === 'vendedor', fn ($query) => $query->whereHas('intereses', fn ($subquery) => $subquery->where('vendedor_id', $usuario->id)))
            ->when($request->query('buscar'), function ($query, string $buscar) {
                $query->where(function ($subquery) use ($buscar) {
                    $subquery->where('nombre', 'ilike', "%{$buscar}%")
                        ->orWhere('apellido', 'ilike', "%{$buscar}%")
                        ->orWhere('correo', 'ilike', "%{$buscar}%")
                        ->orWhere('documento', 'ilike', "%{$buscar}%")
                        ->orWhere('telefono', 'ilike', "%{$buscar}%");
                });
            })
            ->when($request->query('estado'), fn ($query, string $estado) => $query->where('estado', $estado))
            ->orderByDesc('fecha_registro');

        return response()->json(['prospectos' => $query->get()]);
    }

    public function store(Request $request): JsonResponse
    {
        $this->authorizeComercial($request);

        $data = $this->validarProspecto($request);
        $data['fecha_registro'] = now();

        $prospecto = Prospecto::query()->create($data);

        return response()->json(['prospecto' => $prospecto->load('intereses.vendedor')], 201);
    }

    public function update(Request $request, Prospecto $prospecto): JsonResponse
    {
        $this->authorizeProspecto($request, $prospecto);

        $prospecto->update($this->validarProspecto($request, $prospecto));

        $usuario = $request->attributes->get('auth_usuario');

        return response()->json(['prospecto' => $prospecto->fresh()->load([
            'intereses' => fn ($query) => $query
                ->when($usuario->rol === 'vendedor', fn ($query) => $query->where('vendedor_id', $usuario->id))
                ->with('vendedor'),
        ])]);
    }

    public function cambiarEstado(Request $request, Prospecto $prospecto): JsonResponse
    {
        $this->authorizeProspecto($request, $prospecto);

        $data = $request->validate([
            'estado' => ['required', Rule::in(Prospecto::ESTADOS)],
        ]);

        abort_if($data['estado'] === 'Convertido' && $prospecto->estado !== 'Convertido', 422, 'La conversion se realiza al aprobar el pago.');
        $prospecto->update(['estado' => $data['estado']]);

        return response()->json(['prospecto' => $prospecto->fresh()]);
    }

    public function crearInteres(Request $request): JsonResponse
    {
        $data = $request->validate([
            'prospecto_id' => ['required', 'exists:prospectos,id'],
            'modulo_id' => ['required', 'string'],
        ]);

        $prospecto = Prospecto::query()->findOrFail($data['prospecto_id']);
        $this->authorizeProspecto($request, $prospecto);
        $oferta = $this->resolveOferta($data);
        $modulo = $oferta['modulo'];

        $interes = Interes::query()->firstOrCreate([
            'prospecto_id' => $prospecto->id,
            'external_modulo_id' => $modulo['external_modulo_id'],
        ], [
            'external_anuncio_id' => $oferta['external_anuncio_id'],
            'programa_nombre' => $modulo['programa']['nombre'],
            'modulo_nombre' => $modulo['nombre'],
            'modulo_descripcion' => $modulo['descripcion'],
            'precio' => $oferta['precio'],
            'estado' => 'Nuevo',
            'fecha' => now(),
        ]);

        return response()->json(['interes' => $interes->load('prospecto', 'vendedor')], 201);
    }

    public function intereses(Prospecto $prospecto, Request $request): JsonResponse
    {
        $this->authorizeProspecto($request, $prospecto);

        return response()->json(['intereses' => $prospecto->intereses()
            ->when($request->attributes->get('auth_usuario')->rol === 'vendedor', fn ($query) => $query->where('vendedor_id', $request->attributes->get('auth_usuario')->id))
            ->with('vendedor', 'ordenesPago.pago')->latest()->get()]);
    }

    public function importarCSV(Request $request): JsonResponse
    {
        $this->authorizeComercial($request);

        $data = $request->validate([
            'csv' => ['required', 'string', 'max:2097152'],
        ]);

        $stream = fopen('php://temp', 'r+');
        fwrite($stream, $data['csv']);
        rewind($stream);
        $rawHeader = array_map(fn ($value) => trim((string) $value), fgetcsv($stream, 0, ',', '"', '') ?: []);
        $lines = [];
        while (($values = fgetcsv($stream, 0, ',', '"', '')) !== false) {
            $lines[] = $values;
        }
        fclose($stream);
        $header = array_map(fn (string $column) => $this->normalizarColumnaCSV($column), $rawHeader);
        $required = ['nombre', 'apellido', 'documento', 'telefono', 'profesion', 'ubicacion', 'correo'];
        $errores = [];

        $missing = array_values(array_diff($required, $header));
        if (count($header) !== count(array_unique($header))) {
            throw ValidationException::withMessages(['csv' => 'El CSV contiene columnas duplicadas.']);
        }
        if ($missing) {
            return response()->json([
                'mensaje' => 'El CSV no contiene todas las columnas requeridas.',
                'columnas_requeridas' => $required,
                'columnas_faltantes' => $missing,
                'errores' => array_map(fn (string $column) => ['columna' => $column, 'error' => 'Columna requerida ausente'], $missing),
            ], 422);
        }

        $rows = [];

        foreach ($lines as $index => $line) {
            if ($line === [null]) {
                continue;
            }

            $values = array_map(fn ($value) => trim((string) $value), $line);
            $row = count($header) === count($values) ? array_combine($header, $values) : false;

            if (! $row) {
                $errores[] = ['fila' => $index + 2, 'error' => 'Formato invalido'];

                continue;
            }
            $row = array_map('trim', $row);
            $row['correo'] = mb_strtolower($row['correo']);
            foreach (['nombre' => 120, 'apellido' => 120, 'documento' => 60, 'telefono' => 40, 'profesion' => 120, 'ubicacion' => 160, 'correo' => 160] as $column => $limit) {
                if (mb_strlen($row[$column] ?? '') > $limit) {
                    $errores[] = ['fila' => $index + 2, 'columna' => $column, 'error' => "Maximo {$limit} caracteres"];
                }
            }

            foreach ($required as $column) {
                if (trim((string) ($row[$column] ?? '')) === '') {
                    $errores[] = ['fila' => $index + 2, 'columna' => $column, 'error' => 'Campo requerido vacio'];
                }
            }

            if (! filter_var($row['correo'] ?? '', FILTER_VALIDATE_EMAIL)) {
                $errores[] = ['fila' => $index + 2, 'columna' => 'correo', 'error' => 'Correo invalido'];
            }

            if (Prospecto::query()->where('documento', $row['documento'])->orWhere('correo', $row['correo'])->exists()) {
                $errores[] = ['fila' => $index + 2, 'error' => 'Documento o correo duplicado'];
            }

            $rows[] = $row;
        }

        if (! $rows) {
            $errores[] = ['fila' => 2, 'error' => 'El CSV no contiene registros'];
        }

        foreach (collect($rows)->pluck('documento')->filter()->duplicates()->values() as $documento) {
            $errores[] = ['columna' => 'documento', 'error' => "Documento duplicado en el archivo: {$documento}"];
        }

        foreach (collect($rows)->pluck('correo')->filter()->duplicates()->values() as $correo) {
            $errores[] = ['columna' => 'correo', 'error' => "Correo duplicado en el archivo: {$correo}"];
        }

        if ($errores) {
            return response()->json([
                'mensaje' => 'El CSV contiene errores. No se cargo ningun prospecto.',
                'columnas_requeridas' => $required,
                'errores' => $errores,
            ], 422);
        }

        $creados = DB::transaction(function () use ($rows): int {
            foreach ($rows as $row) {
                Prospecto::query()->create([
                    'nombre' => $row['nombre'],
                    'apellido' => $row['apellido'],
                    'documento' => $row['documento'],
                    'correo' => $row['correo'],
                    'telefono' => $row['telefono'],
                    'profesion' => $row['profesion'],
                    'ubicacion' => $row['ubicacion'],
                    'estado' => 'Nuevo',
                    'fecha_registro' => now(),
                ]);
            }

            return count($rows);
        });

        return response()->json(['creados' => $creados, 'errores' => $errores]);
    }

    private function normalizarColumnaCSV(string $column): string
    {
        $column = preg_replace('/^\xEF\xBB\xBF/', '', $column);
        $normalized = Str::ascii(Str::lower(trim($column)));

        return match ($normalized) {
            'nombres' => 'nombre',
            'apellidos' => 'apellido',
            'ci', 'documento_identidad' => 'documento',
            default => $normalized,
        };
    }

    private function resolveOferta(array $data): array
    {
        $oferta = $this->catalogo->buscarOferta(
            anuncioId: $data['anuncio_id'] ?? null,
            moduloId: $data['modulo_id'] ?? null,
        );

        if (! $oferta) {
            throw ValidationException::withMessages(['modulo_id' => 'Debe seleccionar un modulo disponible.']);
        }

        if (! empty($data['anuncio_id']) && ! empty($data['modulo_id']) && $data['modulo_id'] !== $oferta['external_modulo_id']) {
            throw ValidationException::withMessages(['modulo_id' => 'El modulo no corresponde al anuncio seleccionado.']);
        }

        return $oferta;
    }

    private function validarProspecto(Request $request, ?Prospecto $prospecto = null): array
    {
        abort_if($request->input('estado') === 'Convertido' && $prospecto?->estado !== 'Convertido', 422, 'La conversion se realiza al aprobar el pago.');
        $request->merge(['correo' => mb_strtolower(trim((string) $request->input('correo')))]);

        return $request->validate([
            'nombre' => ['required', 'string', 'max:120'],
            'apellido' => ['required', 'string', 'max:120'],
            'documento' => ['required', 'string', 'max:60', Rule::unique('prospectos', 'documento')->ignore($prospecto?->id)],
            'correo' => ['required', 'email', 'max:160', Rule::unique('prospectos', 'correo')->ignore($prospecto?->id)],
            'telefono' => ['required', 'string', 'max:40'],
            'profesion' => ['required', 'string', 'max:120'],
            'ubicacion' => ['required', 'string', 'max:160'],
            'estado' => ['required', Rule::in(Prospecto::ESTADOS)],
        ]);
    }

    private function authorizeComercial(Request $request): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_if(! in_array($usuario?->rol, ['administrador', 'coordinador'], true), 403, 'No tiene permisos comerciales.');
    }

    private function authorizeProspecto(Request $request, Prospecto $prospecto): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        $tieneInteresAsignado = $prospecto->intereses()->where('vendedor_id', $usuario?->id)->exists();

        abort_if(
            $usuario?->rol === 'vendedor' && ! $tieneInteresAsignado,
            403,
            'Prospecto no asignado.'
        );
    }
}

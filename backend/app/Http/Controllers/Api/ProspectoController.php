<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Interes;
use App\Models\Prospecto;
use App\Models\SolicitudCompra;
use App\Services\CatalogoExternoDemo;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Illuminate\Validation\Rule;
use Illuminate\Validation\ValidationException;

class ProspectoController extends Controller
{
    public function __construct(private readonly CatalogoExternoDemo $catalogo)
    {
    }

    public function registrarInteres(Request $request): JsonResponse
    {
        $data = $request->validate([
            'anuncio_id' => ['nullable', 'string'],
            'modulo_id' => ['nullable', 'string'],
            'nombre' => ['required', 'string', 'max:120'],
            'apellido' => ['required', 'string', 'max:120'],
            'documento' => ['required', 'string', 'max:60'],
            'correo' => ['required', 'email', 'max:160'],
            'telefono' => ['required', 'string', 'max:40'],
            'profesion' => ['required', 'string', 'max:120'],
            'ubicacion' => ['required', 'string', 'max:160'],
        ]);

        $oferta = $this->resolveOferta($data);
        $modulo = $oferta['modulo'];

        [$prospecto, $interes, $created] = DB::transaction(function () use ($data, $modulo, $oferta) {
            $prospecto = Prospecto::query()
                ->where('documento', $data['documento'])
                ->orWhere('correo', $data['correo'])
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
            } else {
                $prospecto->update([
                    'nombre' => $data['nombre'],
                    'apellido' => $data['apellido'],
                    'telefono' => $data['telefono'],
                    'profesion' => $data['profesion'],
                    'ubicacion' => $data['ubicacion'],
                ]);
            }

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

            if (! $interes->wasRecentlyCreated && in_array($interes->estado, ['Perdido', 'Convertido'], true)) {
                $interes->update(['estado' => 'Nuevo', 'observacion' => null]);
            }

            return [$prospecto, $interes, $created];
        });

        return response()->json([
            'mensaje' => 'Interes registrado correctamente. Un vendedor tomara seguimiento y se comunicara por WhatsApp.',
            'prospecto' => $prospecto->load('intereses.vendedor'),
            'interes' => $interes->load('prospecto', 'vendedor'),
            'nuevo_prospecto' => $created,
        ], $created ? 201 : 200);
    }

    public function index(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        $query = Prospecto::query()
            ->with(['intereses.vendedor', 'intereses.ordenesPago.pago', 'solicitudesCompra'])
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

        return response()->json(['prospecto' => $prospecto->fresh()->load('intereses.vendedor')]);
    }

    public function asignarVendedor(Request $request, Prospecto $prospecto): JsonResponse
    {
        $this->authorizeComercial($request);

        $data = $request->validate([
            'vendedor_id' => ['nullable', Rule::exists('usuarios', 'id')->where('rol', 'vendedor')],
        ]);

        $prospecto->update(['vendedor_id' => $data['vendedor_id'] ?? null]);

        return response()->json(['prospecto' => $prospecto->fresh()->load('intereses.vendedor')]);
    }

    public function cambiarEstado(Request $request, Prospecto $prospecto): JsonResponse
    {
        $this->authorizeProspecto($request, $prospecto);

        $data = $request->validate([
            'estado' => ['required', Rule::in(Prospecto::ESTADOS)],
        ]);

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

        return response()->json(['intereses' => $prospecto->intereses()->with('vendedor', 'ordenesPago.pago')->latest()->get()]);
    }

    public function crearSolicitud(Request $request): JsonResponse
    {
        $data = $request->validate([
            'prospecto_id' => ['required', 'exists:prospectos,id'],
            'modulo_id' => ['required', 'string'],
        ]);

        $prospecto = Prospecto::query()->findOrFail($data['prospecto_id']);
        $this->authorizeProspecto($request, $prospecto);
        $oferta = $this->resolveOferta($data);
        $modulo = $oferta['modulo'];

        $solicitud = SolicitudCompra::query()->create([
            'prospecto_id' => $prospecto->id,
            'external_anuncio_id' => $oferta['external_anuncio_id'],
            'external_modulo_id' => $modulo['external_modulo_id'],
            'programa_nombre' => $modulo['programa']['nombre'],
            'modulo_nombre' => $modulo['nombre'],
            'modulo_descripcion' => $modulo['descripcion'],
            'anuncio_titulo' => $oferta['titulo'],
            'precio_acordado' => $oferta['precio'],
            'estado' => 'pendiente',
            'fecha' => now(),
        ]);

        return response()->json(['solicitud' => $solicitud->load('prospecto')], 201);
    }

    public function importarCSV(Request $request): JsonResponse
    {
        $this->authorizeComercial($request);

        $data = $request->validate([
            'csv' => ['required', 'string'],
        ]);

        $lines = preg_split('/\r\n|\r|\n/', trim($data['csv']));
        $rawHeader = array_map('trim', str_getcsv(array_shift($lines)));
        $header = array_map(fn (string $column) => $this->normalizarColumnaCSV($column), $rawHeader);
        $required = ['nombre', 'apellido', 'documento', 'telefono', 'profesion', 'ubicacion', 'correo'];
        $errores = [];

        $missing = array_values(array_diff($required, $header));
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
            if (trim($line) === '') {
                continue;
            }

            $values = str_getcsv($line);
            $row = count($header) === count($values) ? array_combine($header, $values) : false;

            if (! $row) {
                $errores[] = ['fila' => $index + 2, 'error' => 'Formato invalido'];
                continue;
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
        return $request->validate([
            'nombre' => ['required', 'string', 'max:120'],
            'apellido' => ['required', 'string', 'max:120'],
            'documento' => ['required', 'string', 'max:60', Rule::unique('prospectos', 'documento')->ignore($prospecto?->id)],
            'correo' => ['required', 'email', 'max:160', Rule::unique('prospectos', 'correo')->ignore($prospecto?->id)],
            'telefono' => ['required', 'string', 'max:40'],
            'profesion' => ['required', 'string', 'max:120'],
            'ubicacion' => ['required', 'string', 'max:160'],
            'estado' => ['required', Rule::in(Prospecto::ESTADOS)],
            'vendedor_id' => ['nullable', Rule::exists('usuarios', 'id')->where('rol', 'vendedor')],
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
            $usuario?->rol === 'vendedor' && $prospecto->vendedor_id !== $usuario->id && ! $tieneInteresAsignado,
            403,
            'Prospecto no asignado.'
        );
    }
}

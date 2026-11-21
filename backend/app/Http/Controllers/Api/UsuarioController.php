<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Programa;
use App\Models\ProgramaResponsable;
use App\Models\Usuario;
use App\Services\Acceso;
use App\Services\Fotos;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rule;

/**
 * CU1: gestión de usuarios con rol, vigencia de la credencial (clase 03) y foto con nombre legible (clase 40).
 * A cada coordinador se le asignan los programas que supervisa (RF1.3).
 */
class UsuarioController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $buscar = trim((string) $request->query('buscar', ''));
        $usuarios = Usuario::query()
            ->with('programasACargo:programa_codigo,coordinador_correo')
            ->when($buscar !== '', fn ($q) => $q->where(fn ($s) => $s->where('nombre', 'ilike', "%{$buscar}%")
                ->orWhere('apellido', 'ilike', "%{$buscar}%")->orWhere('correo', 'ilike', "%{$buscar}%")))
            ->when($request->query('rol'), fn ($q, $rol) => $q->where('rol', $rol))
            ->when($request->query('estado'), fn ($q, $estado) => $q->where('estado', $estado))
            ->orderBy('rol')->orderBy('nombre')
            ->get();

        return response()->json([
            'usuarios' => $usuarios,
            'roles' => DB::table('roles')->orderBy('nombre')->get(['nombre', 'descripcion']),
            'programas' => Programa::query()->orderBy('nombre')->get(['codigo', 'nombre']),
        ]);
    }

    /** Lista corta de vendedores activos, para asignar y filtrar (la usan coordinación y reportes). */
    public function vendedores(): JsonResponse
    {
        return response()->json(['vendedores' => Usuario::query()->where('rol', 'vendedor')->where('estado', 'activo')
            ->orderBy('nombre')->get(['correo', 'nombre', 'apellido', 'foto'])]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $this->validar($request);
        $usuario = DB::transaction(function () use ($data) {
            $usuario = Usuario::query()->create(collect($data)->except(['foto', 'programas'])->all() + ['password' => Hash::make($data['password'])]);
            $this->guardarExtras($usuario, $data);

            return $usuario;
        });

        return response()->json(['mensaje' => 'Usuario creado correctamente.', 'usuario' => $usuario->fresh('programasACargo')], 201);
    }

    public function update(Request $request, Usuario $usuario): JsonResponse
    {
        $data = $this->validar($request, $usuario);

        DB::transaction(function () use ($usuario, $data, $request) {
            // Serializa cambios de acceso para no quedarse nunca sin administrador activo.
            Usuario::query()->where('rol', 'administrador')->orderBy('correo')->lockForUpdate()->get(['correo']);
            $usuario->refresh();
            $this->conservarAdministrador($usuario, $data);

            $revocar = ! empty($data['password']) || $data['estado'] !== 'activo' || $data['rol'] !== $usuario->rol;
            $campos = collect($data)->except(['foto', 'programas', 'password'])->all();
            if (! empty($data['password'])) {
                $campos['password'] = Hash::make($data['password']);
            }
            $usuario->update($campos);
            $this->guardarExtras($usuario, $data);

            if ($revocar && $usuario->correo !== $request->attributes->get('auth_usuario')->correo) {
                $usuario->tokens()->delete();
            }
        });

        return response()->json(['mensaje' => 'Usuario actualizado correctamente.', 'usuario' => $usuario->fresh('programasACargo')]);
    }

    public function cambiarEstado(Request $request, Usuario $usuario): JsonResponse
    {
        $data = $request->validate(['estado' => ['required', Rule::in(Usuario::ESTADOS)]]);

        DB::transaction(function () use ($usuario, $data) {
            Usuario::query()->where('rol', 'administrador')->orderBy('correo')->lockForUpdate()->get(['correo']);
            $usuario->refresh();
            $this->conservarAdministrador($usuario, $data + ['rol' => $usuario->rol]);
            $usuario->update($data);
            if ($data['estado'] === 'inactivo') {
                $usuario->tokens()->delete();
            }
        });

        return response()->json(['mensaje' => $data['estado'] === 'activo' ? 'Usuario activado.' : 'Usuario desactivado.', 'usuario' => $usuario->fresh()]);
    }

    public function foto(Request $request, Usuario $usuario)
    {
        // Las fotos se sirven por nombre desde /api/fotos/{archivo}; este método queda para borrar.
        abort_unless(Acceso::permite($request->attributes->get('auth_usuario'), 'usuarios', 'eliminacion'), 403);
        if ($usuario->foto && ($ruta = Fotos::ruta($usuario->foto))) {
            @unlink($ruta);
        }
        $usuario->update(['foto' => null]);

        return response()->json(['mensaje' => 'Foto eliminada.']);
    }

    private function validar(Request $request, ?Usuario $usuario = null): array
    {
        $request->merge(['correo' => mb_strtolower(trim((string) $request->input('correo')))]);

        return $request->validate([
            'nombre' => ['required', 'string', 'max:120', "regex:/^[\\pL\\s'.-]+$/u"],
            'apellido' => ['required', 'string', 'max:120', "regex:/^[\\pL\\s'.-]+$/u"],
            // El correo es la clave del usuario: no se cambia una vez creado (ON UPDATE CASCADE lo permitiría, pero rompe sesiones).
            'correo' => $usuario ? ['required', Rule::in([$usuario->correo])] : ['required', 'email', 'max:160', 'unique:usuarios,correo'],
            'telefono' => ['nullable', 'string', 'regex:/^\\+?[0-9 ]{7,20}$/'],
            'password' => [$usuario ? 'nullable' : 'required', 'string', 'min:8', 'max:120', 'regex:/(?=.*[A-Za-z])(?=.*\d)/'],
            'rol' => ['required', Rule::exists('roles', 'nombre')],
            'estado' => ['required', Rule::in(Usuario::ESTADOS)],
            'fecha_inicio' => ['required', 'date'],
            'fecha_fin' => ['required', 'date', 'after_or_equal:fecha_inicio'],
            'foto' => ['nullable', 'string'],
            'programas' => ['nullable', 'array'],
            'programas.*' => ['string', 'exists:programas,codigo'],
        ], [
            'correo.in' => 'El correo identifica al usuario y no se puede cambiar.',
            'password.regex' => 'La contraseña debe combinar letras y números.',
        ], ['fecha_inicio' => 'inicio de vigencia', 'fecha_fin' => 'fin de vigencia', 'programas' => 'programas a cargo']);
    }

    private function guardarExtras(Usuario $usuario, array $data): void
    {
        if (! empty($data['foto'])) {
            $usuario->update(['foto' => Fotos::guardar($data['foto'], $usuario->apellido, $usuario->nombre, $usuario->foto)]);
        }

        // RF1.3: programas que supervisa el coordinador (un programa tiene un solo responsable).
        if ($usuario->rol === 'coordinador' && array_key_exists('programas', $data)) {
            ProgramaResponsable::query()->where('coordinador_correo', $usuario->correo)->whereNotIn('programa_codigo', $data['programas'] ?? [])->delete();
            foreach ($data['programas'] ?? [] as $codigo) {
                ProgramaResponsable::query()->updateOrCreate(['programa_codigo' => $codigo], ['coordinador_correo' => $usuario->correo]);
            }
        } elseif ($usuario->rol !== 'coordinador') {
            ProgramaResponsable::query()->where('coordinador_correo', $usuario->correo)->delete();
        }
    }

    private function conservarAdministrador(Usuario $usuario, array $data): void
    {
        $pierdeAcceso = $data['estado'] !== 'activo' || $data['rol'] !== 'administrador';
        abort_if($usuario->rol === 'administrador' && $usuario->estado === 'activo' && $pierdeAcceso
            && ! Usuario::query()->where('rol', 'administrador')->where('estado', 'activo')->whereKeyNot($usuario->correo)->exists(),
            422, 'Debe conservar al menos un administrador activo.');
    }
}

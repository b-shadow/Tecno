<?php

namespace Database\Seeders;

use App\Models\Usuario;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        Usuario::query()->updateOrCreate([
            'correo' => 'admin@crm-educativo.local',
        ], [
            'nombre' => 'Administrador',
            'apellido' => 'General',
            'telefono' => '70000000',
            'password' => Hash::make('Admin12345'),
            'rol' => 'administrador',
            'estado' => 'activo',
        ]);

        Usuario::query()->updateOrCreate([
            'correo' => 'vendedor.demo@crm-educativo.local',
        ], [
            'nombre' => 'Vendedor',
            'apellido' => 'Demo',
            'telefono' => '71111111',
            'password' => Hash::make('Vendedor12345'),
            'rol' => 'vendedor',
            'estado' => 'activo',
        ]);
    }
}

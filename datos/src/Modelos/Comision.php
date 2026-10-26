<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Comision extends Model
{
    protected $table = 'comisiones';

    protected $primaryKey = 'nro_solicitud';

    public $incrementing = false;

    protected $guarded = [];

    public static function porcentajeVigente(): float
    {
        return (float) (Configuracion::query()->whereKey('comision_porcentaje')->value('valor') ?? 2);
    }

    public static function registrar(int $nroSolicitud, string $vendedor, float $precio): self
    {
        $porcentaje = self::porcentajeVigente();

        return self::query()->firstOrCreate(['nro_solicitud' => $nroSolicitud], [
            'vendedor_correo' => $vendedor,
            'porcentaje' => $porcentaje,
            'monto' => round($precio * $porcentaje / 100, 2),
            'estado' => 'Pendiente',
        ]);
    }

    protected function casts(): array
    {
        return ['porcentaje' => 'decimal:2', 'monto' => 'decimal:2', 'fecha_pago' => 'datetime'];
    }

    public function vendedor(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'vendedor_correo', 'correo');
    }

    public function venta(): BelongsTo
    {
        return $this->belongsTo(SolicitudCompra::class, 'nro_solicitud', 'nro_solicitud');
    }
}

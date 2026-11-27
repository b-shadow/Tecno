<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Interaccion extends Model
{
    protected $table = 'interacciones';

    protected $primaryKey = 'nro_interaccion';

    protected $guarded = [];

    public const TIPOS = ['WhatsApp', 'Llamada', 'Correo electronico', 'Reunion', 'Nota comercial', 'Orden de pago enviada', 'Pago informado', 'Compra validada', 'Orden finalizada'];

    protected function casts(): array
    {
        return ['fecha' => 'datetime'];
    }

    public function interes(): BelongsTo
    {
        return $this->belongsTo(Interes::class, 'nro_tarjeta', 'nro_tarjeta');
    }

    public function usuario(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'usuario_correo', 'correo');
    }
}

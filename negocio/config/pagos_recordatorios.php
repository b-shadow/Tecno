<?php

/**
 * Configuración centralizada del envío automático de solicitudes y recordatorios de cuotas (CU6 / CU7).
 * Modificar estos valores permite ajustar días y horarios rápidamente durante la operación o defensa.
 */
return [
    // Zona horaria comercial usada para fechas de vencimiento y programación diaria.
    'zona_horaria' => env('APP_TIMEZONE', 'America/La_Paz'),

    // Hora de ejecución automática diaria del Scheduler (formato HH:MM de 24 horas).
    'hora_envio' => env('PAGOS_HORA_ENVIO', '09:00'),

    // Enviar automáticamente el resumen del plan y enlace de 1.ª cuota al confirmar una orden.
    'enviar_al_crear_orden' => true,

    // Días antes del vencimiento para enviar recordatorio preventivo.
    'dias_antes_vencimiento' => 3,

    // Activar o desactivar el recordatorio el mismo día del vencimiento.
    'enviar_dia_vencimiento' => true,

    // Días después del vencimiento para enviar aviso de pago pendiente.
    'dias_despues_vencimiento' => 3,
];

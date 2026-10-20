<?php

return [
    'required' => 'El campo :attribute es obligatorio.',
    'required_without' => 'El campo :attribute es obligatorio cuando no se indica :values.',
    'email' => 'El campo :attribute debe ser un correo electrónico válido.',
    'string' => 'El campo :attribute debe ser texto.',
    'integer' => 'El campo :attribute debe ser un número entero.',
    'numeric' => 'El campo :attribute debe ser numérico.',
    'array' => 'El campo :attribute debe ser una lista.',
    'boolean' => 'El campo :attribute debe ser verdadero o falso.',
    'date' => 'El campo :attribute debe ser una fecha válida.',
    'after_or_equal' => 'El campo :attribute debe ser una fecha igual o posterior a :date.',
    'in' => 'El valor seleccionado para :attribute no es válido.',
    'exists' => 'El valor seleccionado para :attribute no existe o no está disponible.',
    'unique' => 'El valor de :attribute ya está registrado.',
    'confirmed' => 'La confirmación de :attribute no coincide.',
    'min' => [
        'numeric' => 'El campo :attribute debe ser al menos :min.',
        'string' => 'El campo :attribute debe tener al menos :min caracteres.',
        'array' => 'El campo :attribute debe contener al menos :min elementos.',
        'file' => 'El archivo :attribute debe tener al menos :min kilobytes.',
    ],
    'max' => [
        'numeric' => 'El campo :attribute no debe superar :max.',
        'string' => 'El campo :attribute no debe superar :max caracteres.',
        'array' => 'El campo :attribute no debe contener más de :max elementos.',
        'file' => 'El archivo :attribute no debe superar :max kilobytes.',
    ],
    'attributes' => [
        'password' => 'contraseña', 'password_actual' => 'contraseña actual',
        'vendedor_id' => 'vendedor', 'interes_id' => 'interés', 'pago_id' => 'pago',
        'orden_pago_id' => 'orden de pago', 'fecha_desde' => 'fecha inicial', 'fecha_hasta' => 'fecha final',
        'modulos' => 'módulos', 'descripcion' => 'descripción', 'profesion' => 'profesión',
    ],
];

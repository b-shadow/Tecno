<?php

namespace App\Http\Requests\Prospecto;

use App\Http\Requests\ApiRequest;

/** CU3 (RF2.1): carga masiva de prospectos en CSV (hasta 2 MB de texto). */
class ImportarCsvRequest extends ApiRequest
{
    public function rules(): array
    {
        return ['csv' => ['required', 'string', 'max:2097152']];
    }

    public function attributes(): array
    {
        return ['csv' => 'archivo CSV'];
    }
}

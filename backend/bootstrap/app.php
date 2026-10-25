<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\ValidationException;
use Symfony\Component\HttpKernel\Exception\HttpExceptionInterface;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->web(append: [
            \App\Http\Middleware\HandleInertiaRequests::class,
        ]);
        $middleware->alias([
            'auth.token' => \App\Http\Middleware\TokenAuthMiddleware::class,
            'acceso' => \App\Http\Middleware\AccesoRecurso::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->shouldRenderJsonWhen(
            fn (Request $request) => $request->is('api/*') || $request->expectsJson(),
        );

        $exceptions->render(function (ValidationException $exception, Request $request): ?JsonResponse {
            if (! $request->is('api/*')) {
                return null;
            }

            return response()->json([
                'mensaje' => 'Revise los datos marcados: hay campos con errores.',
                'errores' => $exception->errors(),
            ], 422);
        });

        $exceptions->render(function (NotFoundHttpException $exception, Request $request): ?JsonResponse {
            if (! $request->is('api/*')) {
                return null;
            }

            return response()->json(['mensaje' => 'El registro solicitado no existe.'], 404);
        });

        $exceptions->render(function (\Throwable $exception, Request $request): ?JsonResponse {
            if (! $request->is('api/*') || $exception instanceof ValidationException || $exception instanceof NotFoundHttpException) {
                return null;
            }

            if ($exception instanceof HttpExceptionInterface) {
                // Mensajes del framework en inglés (429, 405...) se reemplazan por textos en español (enunciado 6).
                $mensaje = match ($exception->getStatusCode()) {
                    429 => 'Demasiados intentos seguidos. Espere un minuto e intente de nuevo.',
                    405 => 'Operación no permitida en esta dirección.',
                    default => $exception->getMessage() ?: 'La solicitud no pudo completarse.',
                };

                return response()->json(['mensaje' => $mensaje], $exception->getStatusCode(), $exception->getHeaders());
            }

            report($exception);

            return response()->json(['mensaje' => 'Ocurrió un error interno. Intente nuevamente.'], 500);
        });
    })->create();

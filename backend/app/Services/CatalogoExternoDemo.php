<?php

namespace App\Services;

use Illuminate\Support\Collection;

class CatalogoExternoDemo
{
    /**
     * Simula la respuesta del sistema academico externo que publicara programas,
     * modulos y anuncios. El CRM solo consume estos datos.
     */
    public function ofertas(): Collection
    {
        return collect($this->programas())
            ->flatMap(fn (array $programa) => collect($programa['modulos'])->map(function (array $modulo, int $index) use ($programa): array {
                $id = $programa['codigo'].'-m'.($index + 1);

                return [
                    'id' => 'anuncio-'.$id,
                    'external_anuncio_id' => 'anuncio-'.$id,
                    'external_modulo_id' => $id,
                    'titulo' => 'Inscripción abierta: '.$modulo['nombre'],
                    'descripcion' => $modulo['descripcion'],
                    'imagen' => $modulo['imagen'],
                    'imagen_publica' => $modulo['imagen'],
                    'precio' => $modulo['precio'],
                    'fecha_limite_inscripcion' => now()->addDays(30 + $index * 3)->toDateString(),
                    'estado' => 'publicado',
                    'created_at' => now()->subDays($index)->toISOString(),
                    'programa' => [
                        'id' => $programa['codigo'],
                        'external_programa_id' => $programa['codigo'],
                        'nombre' => $programa['nombre'],
                        'descripcion' => $programa['descripcion'],
                        'area' => $programa['area'],
                        'imagen' => $programa['imagen'],
                    ],
                    'modulo' => [
                        'id' => $id,
                        'external_modulo_id' => $id,
                        'programa_id' => $programa['codigo'],
                        'nombre' => $modulo['nombre'],
                        'descripcion' => $modulo['descripcion'],
                        'duracion' => $modulo['duracion'],
                        'precio' => $modulo['precio'],
                        'imagen' => $modulo['imagen'],
                        'programa' => [
                            'id' => $programa['codigo'],
                            'nombre' => $programa['nombre'],
                            'imagen' => $programa['imagen'],
                        ],
                    ],
                ];
            }))
            ->values();
    }

    public function ofertasDePrograma(string $programaId): Collection
    {
        return $this->ofertas()->where('programa.id', $programaId)->values();
    }

    public function buscarOferta(?string $anuncioId = null, ?string $moduloId = null): ?array
    {
        return $this->ofertas()
            ->first(fn (array $oferta) => ($anuncioId && $oferta['external_anuncio_id'] === $anuncioId)
                || ($moduloId && $oferta['external_modulo_id'] === $moduloId));
    }

    private function programas(): array
    {
        return [
            [
                'codigo' => 'desarrollo-web',
                'nombre' => 'Desarrollo de Aplicaciones Web',
                'area' => 'Desarrollo de software',
                'descripcion' => 'Formación integral para construir aplicaciones web modernas.',
                'imagen' => asset('catalogo-demo/programa-desarrollo-web.jpg'),
                'modulos' => [
                    $this->modulo('Fundamentos de Desarrollo Web', 420, 'fundamentos-desarrollo-web', 'Aprende HTML, CSS, JavaScript base y arquitectura web.'),
                    $this->modulo('Desarrollo Frontend', 780, 'desarrollo-frontend', 'Construye interfaces modernas, responsivas y orientadas a componentes.'),
                    $this->modulo('Desarrollo Backend', 960, 'desarrollo-backend', 'Implementa APIs, servicios y lógica de negocio para aplicaciones web.'),
                    $this->modulo('Bases de Datos', 680, 'bases-datos-web', 'Modela, consulta y administra datos para sistemas web.'),
                    $this->modulo('Despliegue de Aplicaciones', 540, 'despliegue-aplicaciones', 'Publica aplicaciones con buenas prácticas de configuración y monitoreo.'),
                ],
            ],
            [
                'codigo' => 'ia-aplicada',
                'nombre' => 'Inteligencia Artificial Aplicada',
                'area' => 'Datos e inteligencia artificial',
                'descripcion' => 'Ruta práctica para crear soluciones con IA y datos.',
                'imagen' => asset('catalogo-demo/programa-ia-aplicada.svg'),
                'modulos' => [
                    $this->modulo('Fundamentos de Inteligencia Artificial', 600, 'fundamentos-ia', 'Comprende conceptos, casos de uso y limites de la IA.'),
                    $this->modulo('Programación con Python', 720, 'python-ia', 'Domina Python aplicado a automatización, datos e IA.'),
                    $this->modulo('Machine Learning', 1280, 'machine-learning', 'Entrena modelos predictivos y evalua su rendimiento.'),
                    $this->modulo('Redes Neuronales', 1460, 'redes-neuronales', 'Explora arquitecturas neuronales para reconocimiento y predicción.'),
                    $this->modulo('Inteligencia Artificial Generativa', 1880, 'ia-generativa', 'Crea soluciones con modelos generativos, prompts y agentes.'),
                ],
            ],
            [
                'codigo' => 'ciberseguridad',
                'nombre' => 'Ciberseguridad',
                'area' => 'Infraestructura y seguridad',
                'descripcion' => 'Protección técnica de redes, sistemas y aplicaciones.',
                'imagen' => asset('catalogo-demo/programa-ciberseguridad.svg'),
                'modulos' => [
                    $this->modulo('Fundamentos de Ciberseguridad', 500, 'fundamentos-ciberseguridad', 'Identifica amenazas, controles y principios de seguridad.'),
                    $this->modulo('Seguridad de Redes', 840, 'seguridad-redes', 'Protege comunicaciones, topologías y servicios de red.'),
                    $this->modulo('Seguridad de Sistemas Operativos', 900, 'seguridad-sistemas-operativos', 'Endurece sistemas Linux y Windows para entornos productivos.'),
                    $this->modulo('Análisis de Vulnerabilidades', 1320, 'analisis-vulnerabilidades', 'Detecta, prioriza y documenta riesgos técnicos.'),
                    $this->modulo('Seguridad de Aplicaciones Web', 1560, 'seguridad-aplicaciones-web', 'Evalua aplicaciones web con enfoque defensivo y OWASP.'),
                ],
            ],
            [
                'codigo' => 'redes-servidores',
                'nombre' => 'Redes y Administración de Servidores',
                'area' => 'Infraestructura y seguridad',
                'descripcion' => 'Operación de infraestructura, servidores y contenedores.',
                'imagen' => asset('catalogo-demo/programa-redes-servidores.svg'),
                'modulos' => [
                    $this->modulo('Fundamentos de Redes', 460, 'fundamentos-redes', 'Comprende modelos de red, direccionamiento y servicios esenciales.'),
                    $this->modulo('Configuración de Redes', 740, 'configuracion-redes', 'Configura equipos, segmentos, rutas y servicios de conectividad.'),
                    $this->modulo('Administración de Servidores Linux', 980, 'servidores-linux', 'Administra servicios, usuarios, permisos y automatización en Linux.'),
                    $this->modulo('Administración de Servidores Windows', 980, 'servidores-windows', 'Gestiona servicios Windows Server y entornos corporativos.'),
                    $this->modulo('Virtualización y Contenedores', 1180, 'virtualizacion-contenedores', 'Implementa entornos virtualizados y contenedores para despliegue.'),
                ],
            ],
            [
                'codigo' => 'datos-bi',
                'nombre' => 'Análisis de Datos y Business Intelligence',
                'area' => 'Datos e inteligencia artificial',
                'descripcion' => 'Analítica, visualización e inteligencia de negocio.',
                'imagen' => asset('catalogo-demo/programa-datos-bi.svg'),
                'modulos' => [
                    $this->modulo('Fundamentos de Bases de Datos', 520, 'fundamentos-bases-datos', 'Aprende conceptos de datos relacionales para análisis.'),
                    $this->modulo('SQL para Análisis de Datos', 700, 'sql-analisis-datos', 'Consulta, transforma y resume información con SQL.'),
                    $this->modulo('Análisis de Datos con Python', 1060, 'analisis-datos-python', 'Procesa datos y genera hallazgos con Python.'),
                    $this->modulo('Business Intelligence con Power BI', 1220, 'power-bi', 'Construye modelos, reportes y visualizaciones ejecutivas.'),
                    $this->modulo('Diseño de Dashboards', 880, 'diseno-dashboards', 'Crea tableros claros, útiles y orientados a decisiones.'),
                ],
            ],
        ];
    }

    private function modulo(string $nombre, int $precio, string $slug, string $descripcion): array
    {
        $duraciones = ['24 horas', '32 horas', '40 horas', '48 horas', '60 horas'];

        return [
            'nombre' => $nombre,
            'precio' => $precio,
            'duracion' => $duraciones[crc32($slug) % count($duraciones)],
            'imagen' => asset("catalogo-demo/modulo-{$slug}.svg"),
            'descripcion' => $descripcion,
        ];
    }
}

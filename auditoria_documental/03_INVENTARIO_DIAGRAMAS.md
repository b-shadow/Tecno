# Inventario y auditoría de diagramas

Commit auditado: `5bf47b2e863631908e37718fb343fd776003fb5b`. Fecha: 26/11/2026 (America/La_Paz). Solo lectura de originales.

47 diagramas EA actuales,49 imágenes base (añaden organigrama y mapa), sin contar EMF como diagramas nuevos. Hay22 PNG de franjas de navegación en el repositorio; el documento actual inserta19 franjas. Word contiene65 imágenes contando portada y franjas. La existencia de imagen no implica corrección.

| Tipo real | Cantidad |
| --- | --- |
| Clases | 8 |
| Actores | 1 |
| Casos de uso | 9 |
| Paquetes | 7 |
| Comunicación | 8 |
| Secuencia | 8 |
| Modelo conceptual de datos | 1 |
| Navegación | 4 |
| Despliegue | 1 |
| Organigrama | 1 |
| Mapa | 1 |

No se localizaron diagramas nativos de actividades, estados o un diagrama independiente de componentes. Los componentes están incluidos en despliegue. El modelo lógico se presenta en tablas de mapeo y el físico como DDL. No se declaran obligatorios diagramas extra sin consigna primaria. Para pagos y pérdida conviene un diagrama de estados como complemento, no como exigencia inventada.

## EA-1: CU1. Gestión de Usuarios (Propietario, Clientes)

Tipo: Clases. Página 40. Estado: PARCIALMENTE CORRECTO. Hallazgos: FMT-001.

Fuente: `generadorDocumento/diagramas/cls-cu1.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_01.png; detalles minúsculos no certificados. Elementos EA: 36.

Leer de arriba hacia abajo: P.jsx → api/*.js → N* → D* → modelo. Son dependencias de uso, no composición. Métodos PHP y firmas extraídos de EA se comparan en05. Los modelos pequeños no muestran todos sus atributos: esta figura es una vista parcial y no reemplaza el diccionario.

## EA-2: CU2. Gestión de Captar, Consumir Oferta

Tipo: Clases. Página 41. Estado: PARCIALMENTE CORRECTO. Hallazgos: FMT-001.

Fuente: `generadorDocumento/diagramas/cls-cu2.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_01.png; detalles minúsculos no certificados. Elementos EA: 16.

Leer de arriba hacia abajo: P.jsx → api/*.js → N* → D* → modelo. Son dependencias de uso, no composición. Métodos PHP y firmas extraídos de EA se comparan en05. Los modelos pequeños no muestran todos sus atributos: esta figura es una vista parcial y no reemplaza el diccionario.

## EA-3: CU3. Gestión de Asignar Prospectos (Leads)

Tipo: Clases. Página 42. Estado: PARCIALMENTE CORRECTO. Hallazgos: FMT-001.

Fuente: `generadorDocumento/diagramas/cls-cu3.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_01.png; detalles minúsculos no certificados. Elementos EA: 19.

Leer de arriba hacia abajo: P.jsx → api/*.js → N* → D* → modelo. Son dependencias de uso, no composición. Métodos PHP y firmas extraídos de EA se comparan en05. Los modelos pequeños no muestran todos sus atributos: esta figura es una vista parcial y no reemplaza el diccionario.

## EA-4: CU4. Gestión de Embudo de Ventas en Tablero Kanban

Tipo: Clases. Página 43. Estado: PARCIALMENTE CORRECTO. Hallazgos: FMT-001.

Fuente: `generadorDocumento/diagramas/cls-cu4.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_02.png; detalles minúsculos no certificados. Elementos EA: 15.

Leer de arriba hacia abajo: P.jsx → api/*.js → N* → D* → modelo. Son dependencias de uso, no composición. Métodos PHP y firmas extraídos de EA se comparan en05. Los modelos pequeños no muestran todos sus atributos: esta figura es una vista parcial y no reemplaza el diccionario.

## EA-5: CU5. Gestión de Pérdida de Prospectos y Clasificación de Motivos

Tipo: Clases. Página 44. Estado: INCORRECTO O DESACTUALIZADO. Hallazgos: CL-002.

Fuente: `generadorDocumento/diagramas/cls-cu5.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_02.png; detalles minúsculos no certificados. Elementos EA: 9.

Leer de arriba hacia abajo: P.jsx → api/*.js → N* → D* → modelo. Son dependencias de uso, no composición. Métodos PHP y firmas extraídos de EA se comparan en05. Los modelos pequeños no muestran todos sus atributos: esta figura es una vista parcial y no reemplaza el diccionario.

## EA-7: CU7. Gestión de Bitácora, Interacciones y Recordatorios

Tipo: Clases. Página 46. Estado: PARCIALMENTE CORRECTO. Hallazgos: FMT-001.

Fuente: `generadorDocumento/diagramas/cls-cu7.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_02.png; detalles minúsculos no certificados. Elementos EA: 20.

Leer de arriba hacia abajo: P.jsx → api/*.js → N* → D* → modelo. Son dependencias de uso, no composición. Métodos PHP y firmas extraídos de EA se comparan en05. Los modelos pequeños no muestran todos sus atributos: esta figura es una vista parcial y no reemplaza el diccionario.

## EA-8: CU8. Reportes y Estadísticas

Tipo: Clases. Página 47. Estado: PARCIALMENTE CORRECTO. Hallazgos: FMT-001.

Fuente: `generadorDocumento/diagramas/cls-cu8.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_03.png; detalles minúsculos no certificados. Elementos EA: 18.

Leer de arriba hacia abajo: P.jsx → api/*.js → N* → D* → modelo. Son dependencias de uso, no composición. Métodos PHP y firmas extraídos de EA se comparan en05. Los modelos pequeños no muestran todos sus atributos: esta figura es una vista parcial y no reemplaza el diccionario.

## EA-9: Actores del sistema

Tipo: Actores. Página 22. Estado: PARCIALMENTE CORRECTO. Hallazgos: CU-002.

Fuente: `generadorDocumento/diagramas/actores.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_01.png; detalles minúsculos no certificados. Elementos EA: 5.

Leer actor → objetivo; las asociaciones no otorgan todas las acciones del CU. La matriz detalla lectura/modificación/eliminación. No se localizaron include, extend o generalizaciones en estas vistas. CU6 necesita pagador público y Stripe; no se exige inventar cuenta Cliente.

## EA-10: CU1: Gestión de Usuarios (Propietario, Clientes)

Tipo: Casos de uso. Página 24. Estado: PARCIALMENTE CORRECTO. Hallazgos: CU-001; CU-002.

Fuente: `generadorDocumento/diagramas/uc-cu1.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_11.png; detalles minúsculos no certificados. Elementos EA: 4.

Leer actor → objetivo; las asociaciones no otorgan todas las acciones del CU. La matriz detalla lectura/modificación/eliminación. No se localizaron include, extend o generalizaciones en estas vistas. CU6 necesita pagador público y Stripe; no se exige inventar cuenta Cliente.

## EA-11: CU2: Gestión de Captar, Consumir Oferta

Tipo: Casos de uso. Página 25. Estado: CORRECTO EN EL ALCANCE REPRESENTADO. Hallazgos: FMT-002.

Fuente: `generadorDocumento/diagramas/uc-cu2.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_11.png; detalles minúsculos no certificados. Elementos EA: 4.

Leer actor → objetivo; las asociaciones no otorgan todas las acciones del CU. La matriz detalla lectura/modificación/eliminación. No se localizaron include, extend o generalizaciones en estas vistas. CU6 necesita pagador público y Stripe; no se exige inventar cuenta Cliente.

## EA-12: CU3: Gestión de Asignar Prospectos (Leads)

Tipo: Casos de uso. Página 26. Estado: CORRECTO EN EL ALCANCE REPRESENTADO. Hallazgos: FMT-002.

Fuente: `generadorDocumento/diagramas/uc-cu3.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_11.png; detalles minúsculos no certificados. Elementos EA: 4.

Leer actor → objetivo; las asociaciones no otorgan todas las acciones del CU. La matriz detalla lectura/modificación/eliminación. No se localizaron include, extend o generalizaciones en estas vistas. CU6 necesita pagador público y Stripe; no se exige inventar cuenta Cliente.

## EA-13: CU4: Gestión de Embudo de Ventas en Tablero Kanban

Tipo: Casos de uso. Página 27. Estado: CORRECTO EN EL ALCANCE REPRESENTADO. Hallazgos: FMT-002.

Fuente: `generadorDocumento/diagramas/uc-cu4.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_11.png; detalles minúsculos no certificados. Elementos EA: 4.

Leer actor → objetivo; las asociaciones no otorgan todas las acciones del CU. La matriz detalla lectura/modificación/eliminación. No se localizaron include, extend o generalizaciones en estas vistas. CU6 necesita pagador público y Stripe; no se exige inventar cuenta Cliente.

## EA-14: CU5: Gestión de Pérdida de Prospectos y Clasificación de Motivos

Tipo: Casos de uso. Página 28. Estado: CORRECTO EN EL ALCANCE REPRESENTADO. Hallazgos: FMT-002.

Fuente: `generadorDocumento/diagramas/uc-cu5.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_12.png; detalles minúsculos no certificados. Elementos EA: 4.

Leer actor → objetivo; las asociaciones no otorgan todas las acciones del CU. La matriz detalla lectura/modificación/eliminación. No se localizaron include, extend o generalizaciones en estas vistas. CU6 necesita pagador público y Stripe; no se exige inventar cuenta Cliente.

## EA-15: CU6: Gestión de Validar Datos y Procesar Conversión a Matrícula

Tipo: Casos de uso. Página 29. Estado: INCORRECTO O DESACTUALIZADO. Hallazgos: CU-001; CU-002.

Fuente: `generadorDocumento/diagramas/uc-cu6.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_12.png; detalles minúsculos no certificados. Elementos EA: 4.

Leer actor → objetivo; las asociaciones no otorgan todas las acciones del CU. La matriz detalla lectura/modificación/eliminación. No se localizaron include, extend o generalizaciones en estas vistas. CU6 necesita pagador público y Stripe; no se exige inventar cuenta Cliente.

## EA-16: CU7: Gestión de Bitácora, Interacciones y Recordatorios

Tipo: Casos de uso. Página 31. Estado: PARCIALMENTE CORRECTO. Hallazgos: CU-001; CU-002.

Fuente: `generadorDocumento/diagramas/uc-cu7.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_12.png; detalles minúsculos no certificados. Elementos EA: 4.

Leer actor → objetivo; las asociaciones no otorgan todas las acciones del CU. La matriz detalla lectura/modificación/eliminación. No se localizaron include, extend o generalizaciones en estas vistas. CU6 necesita pagador público y Stripe; no se exige inventar cuenta Cliente.

## EA-17: CU8: Reportes y Estadísticas

Tipo: Casos de uso. Página 32. Estado: CORRECTO EN EL ALCANCE REPRESENTADO. Hallazgos: FMT-002.

Fuente: `generadorDocumento/diagramas/uc-cu8.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_12.png; detalles minúsculos no certificados. Elementos EA: 4.

Leer actor → objetivo; las asociaciones no otorgan todas las acciones del CU. La matriz detalla lectura/modificación/eliminación. No se localizaron include, extend o generalizaciones en estas vistas. CU6 necesita pagador público y Stripe; no se exige inventar cuenta Cliente.

## EA-18: Diagrama general de casos de uso

Tipo: Casos de uso. Página 33. Estado: PARCIALMENTE CORRECTO. Hallazgos: CU-001; CU-002.

Fuente: `generadorDocumento/diagramas/uc-general.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_13.png; detalles minúsculos no certificados. Elementos EA: 13.

Leer actor → objetivo; las asociaciones no otorgan todas las acciones del CU. La matriz detalla lectura/modificación/eliminación. No se localizaron include, extend o generalizaciones en estas vistas. CU6 necesita pagador público y Stripe; no se exige inventar cuenta Cliente.

## EA-19: Paquetes del sistema

Tipo: Paquetes. Página 34. Estado: CORRECTO EN EL ALCANCE REPRESENTADO. Hallazgos: FMT-002.

Fuente: `generadorDocumento/diagramas/paquetes.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_08.png; detalles minúsculos no certificados. Elementos EA: 6.

El paquete agrupa responsabilidades funcionales; trace lo vincula al CU. Las cajas vacías son notación de paquete, no clases de dominio sin atributos. La figura general no representa interfaces entre módulos ni prueba propiedad exclusiva de tablas.

## EA-20: Seguridad y Acceso: casos de uso

Tipo: Paquetes. Página 35. Estado: CORRECTO EN EL ALCANCE REPRESENTADO. Hallazgos: FMT-002.

Fuente: `generadorDocumento/diagramas/paquete-1.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_07.png; detalles minúsculos no certificados. Elementos EA: 2.

El paquete agrupa responsabilidades funcionales; trace lo vincula al CU. Las cajas vacías son notación de paquete, no clases de dominio sin atributos. La figura general no representa interfaces entre módulos ni prueba propiedad exclusiva de tablas.

## EA-21: Oferta Académica: casos de uso

Tipo: Paquetes. Página 35. Estado: CORRECTO EN EL ALCANCE REPRESENTADO. Hallazgos: FMT-002.

Fuente: `generadorDocumento/diagramas/paquete-2.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_07.png; detalles minúsculos no certificados. Elementos EA: 2.

El paquete agrupa responsabilidades funcionales; trace lo vincula al CU. Las cajas vacías son notación de paquete, no clases de dominio sin atributos. La figura general no representa interfaces entre módulos ni prueba propiedad exclusiva de tablas.

## EA-138: CU6. Gestión de Validar Datos y Procesar Conversión a Matrícula

Tipo: Clases. Página 45. Estado: INCORRECTO O DESACTUALIZADO. Hallazgos: CL-001; FMT-001.

Fuente: `generadorDocumento/diagramas/cls-cu6.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_02.png; detalles minúsculos no certificados. Elementos EA: 35.

Leer de arriba hacia abajo: P.jsx → api/*.js → N* → D* → modelo. Son dependencias de uso, no composición. Métodos PHP y firmas extraídos de EA se comparan en05. Los modelos pequeños no muestran todos sus atributos: esta figura es una vista parcial y no reemplaza el diccionario.

## EA-22: Gestión de Prospectos: casos de uso

Tipo: Paquetes. Página 36. Estado: CORRECTO EN EL ALCANCE REPRESENTADO. Hallazgos: FMT-002.

Fuente: `generadorDocumento/diagramas/paquete-3.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_07.png; detalles minúsculos no certificados. Elementos EA: 4.

El paquete agrupa responsabilidades funcionales; trace lo vincula al CU. Las cajas vacías son notación de paquete, no clases de dominio sin atributos. La figura general no representa interfaces entre módulos ni prueba propiedad exclusiva de tablas.

## EA-23: Pagos y Matrícula: casos de uso

Tipo: Paquetes. Página 36. Estado: CORRECTO EN EL ALCANCE REPRESENTADO. Hallazgos: FMT-002.

Fuente: `generadorDocumento/diagramas/paquete-4.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_07.png; detalles minúsculos no certificados. Elementos EA: 2.

El paquete agrupa responsabilidades funcionales; trace lo vincula al CU. Las cajas vacías son notación de paquete, no clases de dominio sin atributos. La figura general no representa interfaces entre módulos ni prueba propiedad exclusiva de tablas.

## EA-24: Seguimiento Comercial: casos de uso

Tipo: Paquetes. Página 36. Estado: CORRECTO EN EL ALCANCE REPRESENTADO. Hallazgos: FMT-002.

Fuente: `generadorDocumento/diagramas/paquete-5.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_08.png; detalles minúsculos no certificados. Elementos EA: 2.

El paquete agrupa responsabilidades funcionales; trace lo vincula al CU. Las cajas vacías son notación de paquete, no clases de dominio sin atributos. La figura general no representa interfaces entre módulos ni prueba propiedad exclusiva de tablas.

## EA-25: Ventas y Reportes: casos de uso

Tipo: Paquetes. Página 37. Estado: CORRECTO EN EL ALCANCE REPRESENTADO. Hallazgos: FMT-002.

Fuente: `generadorDocumento/diagramas/paquete-6.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_08.png; detalles minúsculos no certificados. Elementos EA: 2.

El paquete agrupa responsabilidades funcionales; trace lo vincula al CU. Las cajas vacías son notación de paquete, no clases de dominio sin atributos. La figura general no representa interfaces entre módulos ni prueba propiedad exclusiva de tablas.

## EA-99: CU1. Gestión de Usuarios (Propietario, Clientes): Comunicación (recorridos principales)

Tipo: Comunicación. Página 37. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/com-cu1.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_03.png; detalles minúsculos no certificados. Elementos EA: 15.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-100: CU2. Gestión de Captar, Consumir Oferta: Comunicación (recorridos principales)

Tipo: Comunicación. Página 38. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/com-cu2.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_03.png; detalles minúsculos no certificados. Elementos EA: 10.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-101: CU3. Gestión de Asignar Prospectos (Leads): Comunicación (recorridos principales)

Tipo: Comunicación. Página 38. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/com-cu3.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_03.png; detalles minúsculos no certificados. Elementos EA: 10.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-102: CU4. Gestión de Embudo de Ventas en Tablero Kanban: Comunicación (recorridos principales)

Tipo: Comunicación. Página 38. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/com-cu4.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_04.png; detalles minúsculos no certificados. Elementos EA: 5.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-103: CU5. Gestión de Pérdida de Prospectos y Clasificación de Motivos: Comunicación (recorridos principales)

Tipo: Comunicación. Página 38. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/com-cu5.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_04.png; detalles minúsculos no certificados. Elementos EA: 10.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-124: CU1. Gestión de Usuarios (Propietario, Clientes): Secuencia (recorridos principales)

Tipo: Secuencia. Página 69. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/sd-cu1.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_08.png; detalles minúsculos no certificados. Elementos EA: 8.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-125: CU2. Gestión de Captar, Consumir Oferta: Secuencia (recorridos principales)

Tipo: Secuencia. Página 70. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/sd-cu2.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_09.png; detalles minúsculos no certificados. Elementos EA: 7.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-126: CU3. Gestión de Asignar Prospectos (Leads): Secuencia (recorridos principales)

Tipo: Secuencia. Página 71. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/sd-cu3.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_09.png; detalles minúsculos no certificados. Elementos EA: 7.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-127: CU4. Gestión de Embudo de Ventas en Tablero Kanban: Secuencia (recorridos principales)

Tipo: Secuencia. Página 72. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/sd-cu4.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_09.png; detalles minúsculos no certificados. Elementos EA: 6.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-128: CU5. Gestión de Pérdida de Prospectos y Clasificación de Motivos: Secuencia (recorridos principales)

Tipo: Secuencia. Página 73. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/sd-cu5.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_09.png; detalles minúsculos no certificados. Elementos EA: 8.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-141: CU6. Gestión de Validar Datos y Procesar Conversión a Matrícula: Comunicación (recorridos principales)

Tipo: Comunicación. Página 39. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001; SEC-002.

Fuente: `generadorDocumento/diagramas/com-cu6.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_04.png; detalles minúsculos no certificados. Elementos EA: 24.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-142: CU6. Gestión de Validar Datos y Procesar Conversión a Matrícula: Secuencia (recorridos principales)

Tipo: Secuencia. Página 74. Estado: INCORRECTO O DESACTUALIZADO. Hallazgos: SEC-001; SEC-002.

Fuente: `generadorDocumento/diagramas/sd-cu6.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_10.png; detalles minúsculos no certificados. Elementos EA: 11.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-105: CU7. Gestión de Bitácora, Interacciones y Recordatorios: Comunicación (recorridos principales)

Tipo: Comunicación. Página 39. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/com-cu7.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_04.png; detalles minúsculos no certificados. Elementos EA: 15.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-106: CU8. Reportes y Estadísticas: Comunicación (recorridos principales)

Tipo: Comunicación. Página 40. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/com-cu8.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_05.png; detalles minúsculos no certificados. Elementos EA: 10.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-130: CU7. Gestión de Bitácora, Interacciones y Recordatorios: Secuencia (recorridos principales)

Tipo: Secuencia. Página 75. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/sd-cu7.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_10.png; detalles minúsculos no certificados. Elementos EA: 8.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-131: CU8. Reportes y Estadísticas: Secuencia (recorridos principales)

Tipo: Secuencia. Página 76. Estado: PARCIALMENTE CORRECTO. Hallazgos: SEC-001.

Fuente: `generadorDocumento/diagramas/sd-cu8.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_10.png; detalles minúsculos no certificados. Elementos EA: 7.

Recorrido y evaluación mensaje por mensaje en06. El nombre del método existe, pero argumentos, validación, alternativas y postcondiciones requieren el contexto del CU. No certificar el comportamiento solo por coincidencia nominal.

## EA-133: Diseño Conceptual de Base de Datos

Tipo: Modelo conceptual de datos. Página 49. Estado: INCORRECTO O DESACTUALIZADO. Hallazgos: BD-001; MC-001; FMT-001.

Fuente: `generadorDocumento/diagramas/conceptual.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_05.png; detalles minúsculos no certificados. Elementos EA: 31.

Cada tabla es una entidad de datos. Las42 relaciones FK directas coinciden con nulabilidad/unicidad; dos asociaciones N:N con entidades asociativas representan otras cuatro FK. Omisión de columnas FK es deliberada. Faltan campos nuevos BD-001, pero no se cuenta cada FK omitida como error de atributos. La impresión es demasiado densa.

## EA-134: Diagrama de Navegacion - Administrador

Tipo: Navegación. Página 77. Estado: PARCIALMENTE CORRECTO. Hallazgos: BD-001; FMT-001.

Fuente: `generadorDocumento/diagramas/nav-administrador.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_05.png; detalles minúsculos no certificados. Elementos EA: 131.

Es una figura alta dividida en franjas. client page presenta; Formulario envía; server page representa endpoint; database tabla. submit envía y build representa respuesta conceptual; React no recibe HTML generado por Laravel. La revisión estructural no certifica todos los cruces/leyendas diminutas. Revisar pagos públicos y métodos históricos frente a HEAD.

## EA-135: Diagrama de Navegacion - Coordinador

Tipo: Navegación. Página 84. Estado: PARCIALMENTE CORRECTO. Hallazgos: BD-001; FMT-001.

Fuente: `generadorDocumento/diagramas/nav-coordinador.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_06.png; detalles minúsculos no certificados. Elementos EA: 115.

Es una figura alta dividida en franjas. client page presenta; Formulario envía; server page representa endpoint; database tabla. submit envía y build representa respuesta conceptual; React no recibe HTML generado por Laravel. La revisión estructural no certifica todos los cruces/leyendas diminutas. Revisar pagos públicos y métodos históricos frente a HEAD.

## EA-136: Diagrama de Navegacion - Vendedor

Tipo: Navegación. Página 90. Estado: PARCIALMENTE CORRECTO. Hallazgos: BD-001; FMT-001.

Fuente: `generadorDocumento/diagramas/nav-vendedor.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_06.png; detalles minúsculos no certificados. Elementos EA: 84.

Es una figura alta dividida en franjas. client page presenta; Formulario envía; server page representa endpoint; database tabla. submit envía y build representa respuesta conceptual; React no recibe HTML generado por Laravel. La revisión estructural no certifica todos los cruces/leyendas diminutas. Revisar pagos públicos y métodos históricos frente a HEAD.

## EA-137: Diagrama de Navegacion - Visitante

Tipo: Navegación. Página 94. Estado: PARCIALMENTE CORRECTO. Hallazgos: BD-001; FMT-001.

Fuente: `generadorDocumento/diagramas/nav-visitante.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_06.png; detalles minúsculos no certificados. Elementos EA: 16.

Es una figura alta dividida en franjas. client page presenta; Formulario envía; server page representa endpoint; database tabla. submit envía y build representa respuesta conceptual; React no recibe HTML generado por Laravel. La revisión estructural no certifica todos los cruces/leyendas diminutas. Revisar pagos públicos y métodos históricos frente a HEAD.

## EA-152: Diagrama de Despliegue

Tipo: Despliegue. Página 48. Estado: INCORRECTO O DESACTUALIZADO. Hallazgos: DEP-001; NOT-001.

Fuente: `generadorDocumento/diagramas/despliegue.png`. Editable: `generadorDocumento/ea/crm-p2.eapx`. Inspección: Inspeccionado globalmente en contacto_05.png; detalles minúsculos no certificados. Elementos EA: 23.

PC Administrador agrupa personal con sesión (tres roles), PC Cliente representa acceso público. Son tipos de acceso, no roles adicionales. React, negocio y paquete datos coexisten en el servidor propuesto; no son necesariamente tres máquinas. Stripe aparece, pero faltan SMTP y operación del scheduler. Versiones remotas y topología no verificadas.

## IMG-ORG: Organigrama funcional

Tipo: Organigrama. Página 19. Estado: CORRECTO EN EL ALCANCE REPRESENTADO. Hallazgos: Sin error específico demostrado en su alcance.

Fuente: `generadorDocumento/diagramas/organigrama.png`. Editable: `No se localizó diagrama en EAPX actual; revisar ea_p2.py`. Inspección: contacto_06.png. Elementos EA: No aplica.

## IMG-MAPA: Ubicación FICCT

Tipo: Mapa. Página 18. Estado: NO VERIFICABLE (ubicación externa); composición inspeccionada. Hallazgos: REQ-001.

Fuente: `generadorDocumento/diagramas/ubicacion.png`. Editable: `PNG de referencia con crédito OSM`. Inspección: contacto_10.png. Elementos EA: No aplica.

## Fuentes, duplicados y faltantes

Todos los PNG base tienen hash registrado; formatos PNG/EMF del mismo nombre son representaciones, no duplicados semánticos contabilizables por separado. Las franjas antiguas vendedor5/6 y visitante3 no pertenecen a las 19 franjas insertadas actuales y requieren depuración posterior, sin borrar nada aquí. No se verificó un editable EA del organigrama en el EAPX actual. Faltan capturas de interfaz. Faltan recorridos detallados de pagador público, webhook, confirmación/conversión y SMTP/scheduler. Se propone ampliar CU6 mediante subobjetivos, no crear un CU por endpoint.

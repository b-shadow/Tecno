# Resumen ejecutivo

Commit auditado: `5bf47b2e863631908e37718fb343fd776003fb5b`. Fecha: 26/11/2026 (America/La_Paz). Solo lectura de originales.

**No listo para impresión/defensa como versión final.** Se registraron28 hallazgos: 2 crítico, 16 alto, 9 medio, 1 bajo. No se modificaron originales ni se ejecutaron operaciones comerciales.


| Métrica | Valor |
| --- | --- |
| paginas | 108 |
| capitulos_romanos | 10 |
| secciones_finales | 3 |
| encabezados_reales | 106 |
| actores_humanos_documentados | 4 |
| roles_autenticados | 3 |
| casos_uso_macro | 8 |
| CU_con_soporte_estatico | 8 |
| CU_totalmente_no_implementados_demostrados | 0 |
| CU_nuevos_propuestos_como_subobjetivos | 2 |
| diagramas_ea | 47 |
| imagenes_base | 49 |
| imagenes_word | 65 |
| tablas_word | 43 |
| tablas_public | 31 |
| tablas_infraestructura_laravel | 1 |
| columnas_public | 292 |
| columnas_laravel | 3 |
| columnas_documentales | 284 |
| columnas_coincidentes | 284 |
| columnas_faltantes_documento | 8 |
| pk_public | 31 |
| fk_public | 46 |
| unique_public | 7 |
| check_public | 28 |
| indices_public | 55 |
| triggers_propios | 5 |
| funciones_propias | 5 |
| secuencias | 14 |
| vistas | 0 |
| clases_php_inventariadas | 111 |
| metodos_php_inventariados | 521 |
| clases_php_documentadas_distintas | 58 |
| operaciones_php_ea_apariciones | 305 |
| firmas_diferentes | 2 |
| endpoints_laravel | 79 |
| hallazgos | 28 |

## Respuestas a las38 preguntas

1. **¿Cómo está dividido?** Portada1, índice2–6, capítulosI–X7–103, conclusión104, bibliografía105–107 y anexo108.

2. **¿Cuántas páginas/capítulos?** 108 páginas,10 capítulos titulados con números romanos, más3 secciones finales numeradas11–13.

3. **¿Qué contiene cada capítulo?** I Perfil; II Teoría; III Organización; IV Requisitos; V Actores/CU; VI Análisis/paquetes/clases/comunicación; VII Diseño/BD/secuencias/navegación/interfaces; VIII Herramientas; IX Resultados esperados; X Plan de pruebas. Detalle en02.

4. **¿Cuántos actores y cuáles?** 4 humanos documentados: Administrador, Coordinador, Vendedor, Visitante.3 roles autenticados. Faltan explicitaciones del pagador público y Stripe; SMTP es servicio externo de soporte.

5. **¿Cuántos CU y cuáles?** 8. CU1: Gestión de Usuarios (Propietario, Clientes); CU2: Gestión de Captar, Consumir Oferta; CU3: Gestión de Asignar Prospectos (Leads); CU4: Gestión de Embudo de Ventas en Tablero Kanban; CU5: Gestión de Pérdida de Prospectos y Clasificación de Motivos; CU6: Gestión de Validar Datos y Procesar Conversión a Matrícula; CU7: Gestión de Bitácora, Interacciones y Recordatorios; CU8: Reportes y Estadísticas

6. **¿Qué CU faltan?** Se proponen subobjetivos CU6.1 Pagar cuota por enlace público y CU6.2 Registrar tarjeta con Setup, sin renumerar. No se afirma que deban ser CU macro nuevos.

7. **¿Cuáles sobran/desactualizados?** No se probó un CU macro sobrante. CU1 contiene Propietario/Clientes; CU7 mezcla nombres de bitácora; CU6 permite nuevos manuales que están bloqueados.

8. **¿Qué tipos de diagramas?** Casos/actores, paquetes, clases, comunicación, secuencia, conceptual de datos, navegación y despliegue; además organigrama y mapa. Lógico/físico son tablas/DDL.

9. **¿Cuántos por tipo?** 8 clases,8 comunicaciones,8 secuencias,9 CU (8 individuales+general),1 actores,7 paquetes,1 conceptual,4 navegación,1 despliegue=47 EA. Más organigrama y mapa=49 imágenes base.

10. **¿Cuáles correctos?** Paquetes y CU2/CU3/CU4/CU5/CU8 son coherentes en el alcance agrupado representado; no equivalen a certificación completa de flujos/permisos. Ver03 por figura.

11. **¿Cuáles incorrectos?** Conceptual está desactualizado por campos; clasesCU6 tiene2 firmas viejas; clasesCU5 omite pérdida; secuenciaCU6 omite conversión; despliegue no distingue observación de propuesta. Otros parciales por condiciones/legibilidad.

12. **¿Cuáles faltan?** Capturas7.6 y recorridos públicos/Setup/webhook/conversión/SMTP/scheduler. Actividades/estados solo complementarios si se decide o lo exige la fuente primaria.

13. **¿Nombres de clases coinciden?** 58 nombres PHP documentados existen en código. Hay nomenclatura Controller/Service/Repository antigua en textos auxiliares.

14. **¿Métodos coinciden?** Los nombres representados existen;303 de305 apariciones de firma coinciden en comparación de tipo/orden/retorno/visibilidad,2 firmas difieren. Defaults no certificados globalmente.

15. **¿Atributos coinciden?** Con volcado previo y abstracción deliberada FK, sí en el conceptual inventariado; frente a BD faltan8 campos nuevos. No confundir atributos Eloquent dinámicos con propiedades PHP.

16. **¿Relaciones coinciden?** 46 FK y acciones coinciden con el volcado. Relaciones de uso P/N/D no son composición. Falta detallar algunas dependencias de comportamiento.

17. **¿Multiplicidades coinciden?** 42 asociaciones directas coinciden con constraints;4 FK se representan mediante2 N:N válidas con asociativas. Detalles visuales minúsculos no certificados en papel.

18. **¿Cuántas tablas PostgreSQL?** 31 en public +1 laravel.migrations=32.

19. **¿Cuántas documentadas?** 31 de negocio/soporte en public; infraestructura Laravel separada deliberadamente.

20. **¿Todas las columnas coinciden?** No:292 reales public,284 documentadas/coincidentes y8 ausentes. Sumando migraciones hay295 columnas.

21. **¿PK/FK coinciden?** 31 PK public y46 FK coinciden con volcado y marcas de mapeo en su estructura; ver07 para restricciones y particularidad compuesta.

22. **¿Cardinalidades coinciden?** Estructuralmente las 46 FK tienen representación directa o N:N válida. La obligatoriedad de hijos en padre no se deduce solo de FK.

23. **¿Triggers coinciden?** 5 propios: intereses_clasificar, intereses_historial, pagos_crear_cuota, pagos_copiar_estado y bitacora_contar_visita. Sus5 funciones tienen cuerpo coincidente con el volcado; faltan explicaciones en el impreso.

24. **¿Arquitectura bien documentada?** Parcialmente: separación física P/N/D y HTTP es real; textos antiguos y decisiones en modelo limitan afirmación estricta de reglas solo enN.

25. **¿Stripe bien documentado?** Parcialmente: Checkout/Setup/firma/idempotencia están mencionados, pero manuales nuevos, pagador público, tokens, conciliación, matrícula y SMTP requieren actualizarse.

26. **¿Funcionalidades recientes?** No completamente: avisos-3/0/+3, enlaces públicos, vencimiento de sesiones, polling3–10s y variantes visuales tienen cobertura incompleta.

27. **¿Despliegue bien documentado?** Es una propuesta institucional con PC Administrador/PC Cliente; no hay evidencia de operación remota ni de versiones dibujadas, SMTP o cron.

28. **¿Qué información falta?** Fuente primaria del enunciado;8 campos/2 UNIQUE; flujos alternativos/públicos; diccionario semántico; restricciones/triggers explicados; capturas y resultadosQA trazados a commit.

29. **¿Qué sobra?** Nombres heredados, instrucciones Controller/Service/Repository, pendientes ya resueltos y remates/franja casi vacía; conservar historia manual etiquetada, no eliminarla por antigua.

30. **¿Qué detectaría docente?** CU6 manual bloqueado; campos de token no modelados; flujo sin matrícula; firmas unión viejas; conceptual de datos confundido con dominio; capturas pendientes y letra pequeña.

31. **¿Qué revisar manualmente?** Checklist11 por hallazgo: enunciado, política de comisión, legibilidad real, endpoints públicos y entorno institucional. No repetir cientos de comparaciones ya respaldadas sin cambios.

32. **¿Qué estudiar?** Objetivo de cada CU y actor, límites P/N/D, cardinalidad desde constraints,5 triggers, cuota1→conversión→comisión, Setup frente a payment, idempotencia, SMTP/scheduler, exportaciónCSV y despliegue previsto.

33. **¿Qué corregir primero?** Reglas/requisitos oficiales y política vigente; luego esquema/CU; después clases y secuencias; luego despliegue/interfaces/pruebas; formato al final.

34. **¿Qué conservar?** Estructura académica, ocho IDs macro, división de capas, catálogo de31 tablas,31 PK/46 FK,5 triggers y5 funciones coincidentes, paquetes y gran parte de nombres/métodos.

35. **¿Qué actualizar completamente?** La explicación/alternativas recientes deCU6 y su secuencia principal, interfaces7.6 y trazabilidad de pruebas. Actualizar selectivamente datos/clases sin rehacer figuras no afectadas.

36. **¿Listo para imprimir?** No como versión final: pendientes visibles, densidad y remates, además de contradicciones esenciales.

37. **¿Listo para defender?** Sirve como base de estudio, pero no se recomienda defender como documentación cerrada hasta corregir hallazgos críticos/altos y ensayar evidenciaQA.

38. **¿Limitaciones?** Sin enunciado primario, servidor institucional, comprobación de recepción SMTP, impresión física, prueba transaccional enHEAD, concurrencia o certificaciónWCAG; detalles densos de navegación pendientes de revisión ampliada.

## Archivos entregados

- `00_CONTROL_AVANCE.md`
- `01_INFORME_AUDITORIA_COMPLETA.md`
- `02_INVENTARIO_DOCUMENTACION.md`
- `03_INVENTARIO_DIAGRAMAS.md`
- `04_AUDITORIA_CASOS_USO.md`
- `05_AUDITORIA_CLASES_METODOS.md`
- `06_AUDITORIA_SECUENCIAS.md`
- `07_AUDITORIA_BASE_DATOS.md`
- `08_MATRIZ_TRAZABILIDAD.xlsx`
- `09_HALLAZGOS_PRIORIZADOS.xlsx`
- `10_CONSULTAS_VERIFICACION.sql`
- `11_CHECKLIST_REVISION_MANUAL.md`
- `12_PLAN_CORRECCION_DOCUMENTAL.md`
- `13_RESUMEN_EJECUTIVO.md`

Inventarios reutilizables y verificaciones: evidencias/. Registro detallado de límites y cobertura:00. No se calcula porcentaje global de calidad.

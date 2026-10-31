"""Texto y datos del documento P2, en el orden de G07. Editar aquí y correr `python documento_p2.py`.
None (o lista vacía) = todavía no escrito: el documento muestra [PENDIENTE] en rojo y lo lista al final.
Nada inventado: cada dato sale del código (crm-web), de la BD, de P2_WEB.md o de lo aprobado por el docente."""
import re
from rutas import CRM_WEB
TITULO = 'Sistema de Control de Prospectos (CRM Educativo)'   # título real del proyecto (usuario, 24/11/2026)
EMPRESA = 'UNEXO'   # organización para la que se construye el CRM (marca del sistema; logo en crm-web)

# ---------------------------------------------------------------- matriz de acceso real (menú dinámico)
_MIG = (CRM_WEB / 'datos' / 'migraciones' / '2026_11_21_000003_crear_matriz_acceso.php').read_text(encoding='utf-8')
RECURSOS = {c: dict(nombre=n, ruta=r, cu=cu, publico=p == 'true') for c, n, r, cu, p in
            re.findall(r"\['([\w-]+)', '([^']+)', '([^']+)', '\w+', \d+, '(CU\d)', (true|false)\]", _MIG)}
for _f in sorted((CRM_WEB / 'datos' / 'migraciones').glob('*.php')):   # recursos agregados después (p. ej. /error, 000007)
    for c, n, r, cu, p in re.findall(r"'codigo' => '([\w-]+)', 'nombre' => '([^']+)', 'ruta' => '([^']+)'.*?'caso_uso' => '(CU\d)', "
                                     r"'publico' => (true|false)", _f.read_text(encoding='utf-8'), re.S):
        RECURSOS.setdefault(c, dict(nombre=n, ruta=r, cu=cu, publico=p == 'true'))
PERMISOS = {rol: dict(re.findall(r"'([\w-]+)' => '(\w+)'", cuerpo))
            for rol, cuerpo in re.findall(r"'(\w+)' => \[(.*?)\]", _MIG.split('PERMISOS = [')[1].split('];')[0], re.S)}
# el administrador recibe eliminación sobre todo recurso privado salvo "Mi día" (up() de la misma migración)
PERMISOS['administrador'] = {c: 'eliminacion' for c, r in RECURSOS.items() if not r['publico'] and c != 'inicio-vendedor'}

SIN_BD = '- Sin conexión o base de datos no disponible: la operación no se guarda y la interfaz muestra el error.'

# ---------------------------------------------------------------- Capítulo I: Perfil
# Fuentes: PRODUCT.md, P2_WEB.md y el código. Antecedentes y problema necesitan la situación previa de UNEXO (cómo
# gestionaba sus prospectos antes del sistema): no está en ninguna fuente, así que quedan pendientes.
INTRODUCCION = [
    'El presente proyecto desarrolla el Sistema de Control de Prospectos (CRM Educativo) de UNEXO, una aplicación web '
    'para la venta de programas de formación de una institución educativa: programas de cinco a seis módulos y módulos '
    'independientes. El sistema capta prospectos desde un catálogo público, los asigna a los vendedores, los lleva por '
    'un embudo de ventas en un tablero Kanban, registra el seguimiento comercial y procesa el pago hasta convertir al '
    'prospecto en alumno matriculado.',
    'El sistema se construye con una arquitectura de 3 capas, como exige el enunciado del Proyecto 2 de la materia '
    'Tecnología Web (INF513): la capa de presentación es una aplicación de una sola página en React que consume, mediante '
    'Axios, una API RESTful desarrollada en Laravel (capa de lógica de negocio), y esta accede a una base de datos '
    'PostgreSQL (capa de datos) compartida con el Proyecto 1, el sistema vía correo electrónico.',
    'El acceso se controla por roles (Administrador, Coordinador y Vendedor) con una matriz de acceso guardada en la base '
    'de datos, de la que se arma el menú de cada usuario, y cada acceso queda registrado en una bitácora. El desarrollo '
    'sigue el Proceso Unificado de Desarrollo de Software (PUDS) y se modela con UML en Enterprise Architect.']
ANTECEDENTES = None          # 3 párrafos; el 3.º: justificación teórica, metodológica y práctica
PROBLEMA = None              # situación, causas, pronóstico, solución
OBJETIVO_GENERAL = ('Desarrollar un sistema web de control de prospectos para UNEXO, con arquitectura de 3 capas '
                    '(React, Laravel API RESTful y PostgreSQL), que gestione la captación, asignación, seguimiento y '
                    'conversión a matrícula de los prospectos de sus programas de formación.')
OBJETIVOS_ESPECIFICOS = [   # alineados a las fases PUDS (11. Conclusión responde una por una)
    'Identificar los requerimientos, los actores y los casos de uso del proceso comercial de UNEXO.',
    'Analizar la arquitectura del sistema mediante paquetes, diagramas de colaboración y análisis de clases por caso de uso.',
    'Diseñar la base de datos, el despliegue, las secuencias y la navegación por actor del sistema.',
    'Implementar la API RESTful en Laravel, la interfaz en React y la base de datos en PostgreSQL, con control de acceso '
    'por roles y bitácora de accesos.',
    'Verificar el sistema con pruebas de caja blanca y de caja negra, y publicarlo en el servidor de la facultad.']
METODOLOGIA = ('Para el desarrollo del sistema se utiliza el Proceso Unificado de Desarrollo de Software (PUDS), un '
               'proceso iterativo e incremental, dirigido por casos de uso y centrado en la arquitectura, con el Lenguaje '
               'Unificado de Modelado (UML) para elaborar los modelos. El proceso se organiza en cuatro fases:')
FASES = {
    'Inicio (Inception).': 'Se identifican los requerimientos del grupo y del enunciado, los actores y los ocho casos de '
                           'uso aprobados por el docente. Entregables: requerimientos funcionales, actores y casos de uso '
                           'con su priorización y detalle.',
    'Elaboración (Elaboration).': 'Se analiza la arquitectura y se diseña el sistema: paquetes, colaboración y clases por '
                                  'caso de uso, base de datos (conceptual, lógico y físico), despliegue, secuencias y '
                                  'navegación por actor. Entregables: modelos de análisis y de diseño en Enterprise Architect.',
    'Construcción (Construction).': 'Se implementan las tres capas: la base de datos con migraciones de Laravel, la API '
                                    'RESTful en Laravel con middleware de token y de matriz de acceso, y la interfaz en '
                                    'React. Entregables: código fuente en el repositorio del grupo y base de datos db_grupo05sa.',
    'Transición (Transition).': 'Se verifica el sistema con pruebas de caja blanca y de caja negra y se publica en el '
                                'servidor de la facultad. Entregables: plan de pruebas, sistema publicado y documentación técnica.'}
METODOLOGIA_CIERRE = None

# ---------------------------------------------------------------- Capítulo II: Fundamentación Teórica
PROGRAMACION_SERVIDOR = None
TEORIA = {   # solo lo que usa crm-web (verificado en composer.json, package.json, routes/, app/Http) y lo que exige el
             # enunciado: arquitectura de 3 capas, API RESTful, RBAC. G07 era MVC con Inertia y Vue: no se copia su lista.
    'Fundamentos de la programación del lado del servidor': None, 'Servicios Web': None, 'Protocolo HTTP': None,
    'Lenguaje HTML': None, 'Lenguaje PHP': None, 'Framework Laravel': None,
    'Arquitectura de 3 capas (Presentación, Lógica de Negocio y Datos)': None, 'API RESTful': None,
    'Hojas de estilo CSS': None, 'Framework Tailwind CSS': None, 'JavaScript': None, 'Biblioteca React': None, 'Enrutamiento en el cliente (React Router)': None,
    'Cliente HTTP Axios': None, 'Base de datos relacional': None, 'PostgreSQL': None,
    'Autenticación con token de acceso (Bearer)': None, 'Control de acceso basado en roles (RBAC)': None,
}
# Dónde está cada tema / herramienta en crm-web. documento_p2.py no genera el documento si un tema o herramienta no
# tiene evidencia o la evidencia ya no está. 'composer:x' / 'npm:x' = dependencia directa en composer.json / package.json;
# 'ruta[:texto]' = el archivo existe (y contiene el texto). Rutas relativas a crm-web.
EVIDENCIA = {
    'Fundamentos de la programación del lado del servidor': 'negocio/routes/api.php:Route::',
    'Servicios Web': 'negocio/app/Negocio/NMotivo.php:response()->json(', 'Protocolo HTTP': 'presentacion/src/api/cliente.js:axios.create',
    'Lenguaje HTML': 'presentacion/index.html:<html', 'Lenguaje PHP': 'composer:php', 'Framework Laravel': 'composer:laravel/framework',
    'Arquitectura de 3 capas (Presentación, Lógica de Negocio y Datos)': 'datos/composer.json:grupo05sa/datos',
    'API RESTful': 'negocio/routes/api.php:Route::patch', 'Hojas de estilo CSS': 'presentacion/src/estilos/app.css',
    'Framework Tailwind CSS': 'npm:tailwindcss', 'JavaScript': 'presentacion/src/main.jsx', 'Biblioteca React': 'npm:react',
    'Enrutamiento en el cliente (React Router)': 'npm:react-router-dom', 'Cliente HTTP Axios': 'npm:axios',
    'Base de datos relacional': 'datos/migraciones/2026_11_21_000001_crear_esquema_compartido.php:->foreign(',
    'PostgreSQL': 'negocio/.env.example:DB_CONNECTION=pgsql',
    'Autenticación con token de acceso (Bearer)': 'negocio/app/Http/Middleware/TokenAuthMiddleware.php:bearerToken()',
    'Control de acceso basado en roles (RBAC)': 'negocio/app/Http/Middleware/AccesoRecurso.php',
    # herramientas sin 'composer:'/'npm:' en su versión
    'PHP': 'composer:php',
    'Enterprise Architect': 'generadorDocumento/ea/crm-p2.eapx', 'Git': 'externa', 'GitHub': 'externa',   # herramientas de trabajo, no del código: no se exigen
}
STACK_AJENO = ('inertia', 'vue', 'jwt', 'livewire', 'blade')   # nada de esto puede estar en composer.json / package.json

# ---------------------------------------------------------------- Capítulo III: Organización (UNEXO)
# Los textos del P1 eran de la Unidad de Capacitación de la FICCT: no se reutilizan. Misión, visión, objetivo y organigrama
# son PROPUESTA DEL GRUPO a partir de ../PRODUCT.md (propósito, usuarios y criterio de éxito); confirmarlos con la clienta
# y vaciar POR_CONFIRMAR. Ubicación: dato de UNEXO que no está en ninguna fuente.
MISION = ('Formar profesionales mediante programas de formación y módulos independientes, acompañando a cada interesado '
          'desde su primer contacto hasta su matrícula.')
VISION = ('Ser una institución de formación reconocida por convertir el interés de cada persona en una matrícula, con un '
          'proceso comercial ordenado, medible y sin interesados olvidados.')
OBJETIVO_EMPRESA = ('Captar, dar seguimiento y matricular a los interesados en sus programas de formación, con la '
                    'coordinación al tanto de cada prospecto y de los motivos por los que se pierde.')
UBICACION = None
ORGANIGRAMA = 'Organigrama del área comercial de UNEXO'
# área comercial según los usuarios del sistema (../PRODUCT.md): (cargo, depende de)
ORGANIGRAMA_CARGOS = [('Administración', None), ('Coordinación', 'Administración'), ('Vendedores', 'Coordinación')]
POR_CONFIRMAR = ['Misión', 'Visión', 'Objetivo de la organización', 'Organigrama']   # propuesta del grupo, no dato de UNEXO

# ---------------------------------------------------------------- Capítulo IV: Requerimientos (P2_WEB.md §2)
REQUERIMIENTOS = [   # (título, párrafo "El sistema permitirá…"); fuente: ../P2_WEB.md §2 (RF1.1 … RF4.3, ajustes del 20/11)
    ('Acceso por roles', 'El sistema permitirá el acceso con correo y contraseña a tres roles: Administrador, Coordinador '
                         'y Vendedor, solo mientras la cuenta esté activa y dentro de su periodo de vigencia.'),
    ('Cartera del vendedor', 'El sistema permitirá que el Vendedor vea únicamente los prospectos de su cartera; los '
                             'prospectos los reparten el Coordinador o el Administrador, sin bolsa común.'),
    ('Alcance del coordinador', 'El sistema permitirá que el Coordinador vea solo las métricas y los prospectos de los '
                                'programas a su cargo.'),
    ('Registro de prospectos', 'El sistema permitirá registrar prospectos de forma manual o masiva mediante un archivo '
                               'CSV, con nombre, teléfono, correo y origen del lead.'),
    ('Interés vinculado al catálogo', 'El sistema permitirá vincular el interés de cada prospecto al catálogo activo: un '
                                      'programa de varios módulos o un módulo independiente.'),
    ('Asignación de prospectos', 'El sistema permitirá asignar prospectos a los vendedores de forma manual, por el '
                                 'Administrador o el Coordinador, o automática por reparto Round-Robin.'),
    ('Tablero Kanban', 'El sistema permitirá gestionar los prospectos como tarjetas que se mueven en un tablero Kanban.'),
    ('Estados del embudo', 'El sistema permitirá llevar cada tarjeta por los estados Nuevo, En Contacto, Seguimiento, '
                           'Promesa de Pago, Convertido y Perdido.'),
    ('Motivo de pérdida', 'El sistema permitirá marcar un prospecto como Perdido solo con un motivo clasificado por '
                          'categoría: Económico, Horario, Incompatibilidad, Contacto u Otro.'),
    ('Validación de conversión', 'El sistema permitirá pasar un prospecto a Convertido solo con sus datos completos y la '
                                 'primera cuota de su orden de pago aprobada, y entonces registrará su matrícula.'),
    ('Historial de interacciones', 'El sistema permitirá consultar el historial cronológico de las interacciones de cada tarjeta.'),
    ('Notas manuales', 'El sistema permitirá registrar notas manuales sobre cada contacto con el prospecto.'),
    ('Recordatorios de contacto', 'El sistema permitirá agendar recordatorios de contacto con fecha y hora futuras y '
                                  'marcarlos como realizados o cancelados.'),
]

# ---------------------------------------------------------------- Capítulo V: Captura de requisitos
ACTORES = [   # (actor, características). Roles reales de la tabla roles + el visitante del catálogo público (CU2)
    ('Administrador', 'Gestiona usuarios y toda la operación comercial.'),
    ('Coordinador', 'Asigna interesados, valida pagos y supervisa vendedores.'),
    ('Vendedor', 'Da seguimiento a los interesados asignados.'),
    ('Visitante', 'Consulta el catálogo público de programas y módulos y registra su interés sin iniciar sesión.'),
]
CU = {   # nombres aprobados por el docente (foro, 5/10/2026)
    'CU1': 'Gestión de Usuarios (Propietario, Clientes)', 'CU2': 'Gestión de Captar, Consumir Oferta',
    'CU3': 'Gestión de Asignar Prospectos (Leads)', 'CU4': 'Gestión de Embudo de Ventas en Tablero Kanban',
    'CU5': 'Gestión de Pérdida de Prospectos y Clasificación de Motivos',
    'CU6': 'Gestión de Validar Datos y Procesar Conversión a Matrícula',
    'CU7': 'Gestión de Bitácora, Interacciones y Recordatorios', 'CU8': 'Reportes y Estadísticas'}
PRIORIDAD = {}   # {'CU1': 'Alta', …}: decisión del grupo, no está en ninguna fuente
ALCANCE = {      # ../P2_WEB.md §1, columna "Cómo se cumple en la web"
    'CU1': 'Registro, modificación y cambio de estado de usuarios con rol, vigencia (fecha de inicio y de fin) y foto con '
           'nombre legible; inicio y cierre de sesión con token; perfil y cambio de contraseña; matriz de acceso editable '
           '(lectura, modificación y eliminación por rol y recurso) y bitácora de accesos.',
    'CU2': 'Catálogo público por programas y módulos, con búsqueda y registro de interés del visitante; sincronización de '
           'la oferta académica desde el cliente API del catálogo, simulado hasta que el Grupo 06 publique su servicio.',
    'CU3': 'Alta manual y carga masiva por CSV de prospectos con su origen; asignación manual y reparto Round-Robin por el '
           'Coordinador o el Administrador.',
    'CU4': 'Tablero Kanban con seis columnas (Nuevo, En Contacto, Seguimiento, Promesa de Pago, Convertido y Perdido), '
           'tarjetas que se arrastran y la opción "Mover a…" en el celular.',
    'CU5': 'Pasar una tarjeta a Perdido exige un motivo de la lista de motivos de pérdida, clasificados por categoría; el '
           'Administrador y el Coordinador gestionan esa lista.',
    'CU6': 'Métodos de pago del prospecto (tarjeta simulada, QR y transferencia), orden de pago al contado o en cuotas, '
           'comprobantes y su validación; la conversión exige datos completos y la primera cuota aprobada, y genera la '
           'inscripción, la comisión del vendedor y la exportación al SIS.',
    'CU7': 'Historial cronológico por tarjeta, registro de interacciones y notas, recordatorios de contacto con la agenda '
           'del día y notificaciones internas.',
    'CU8': 'Dashboard con indicadores, reportes como listados, estadísticas porcentuales del embudo y de los accesos, y '
           'ventas y comisiones por vendedor.',
}
# Detalle de CU: flujo de las pantallas reales (navegacion.py) y excepciones con el mensaje literal del código;
# documento_p2.py comprueba que cada mensaje entre comillas exista en negocio/ o datos/.
DETALLE = {
    'CU1': dict(
        gestionar='Gestionar Usuarios', iniciador='Administrador',
        proposito='Administrar las cuentas de usuario, su rol, vigencia y permisos, y controlar el acceso al sistema.',
        descripcion='El usuario inicia sesión con su correo y contraseña y el sistema arma su menú desde la matriz de '
                    'acceso. El Administrador registra, modifica y cambia el estado de los usuarios, asigna permisos en '
                    'la matriz y consulta la bitácora de accesos.',
        precondicion='El usuario tiene una cuenta activa y vigente; para gestionar usuarios, matriz y bitácora tiene '
                     'permiso sobre esos recursos.',
        proceso=['El usuario ingresa su correo y contraseña en Iniciar Sesión.',
                 'El sistema valida la credencial y su vigencia, registra el acceso en la bitácora y muestra el menú de su rol.',
                 'El Administrador abre Usuarios y registra o edita un usuario con nombre, correo, rol, vigencia y foto.',
                 'El sistema valida los datos y guarda el usuario.',
                 'El Administrador asigna permisos de lectura, modificación o eliminación en la Matriz de Acceso.',
                 'El Administrador consulta la Bitácora de Accesos filtrando por evento, usuario, IP y fechas.'],
        postcondicion='El usuario queda registrado o actualizado, sus permisos definen su menú y cada acceso queda en la bitácora.',
        excepciones=['- Credencial incorrecta: "Correo o contraseña incorrectos."',
                     '- Cuenta inactiva o vencida: "Su cuenta está inactiva o fuera de vigencia."',
                     '- Sin permiso sobre el recurso: "No tiene permiso para realizar esta acción."',
                     '- Último administrador: "Debe conservar al menos un administrador activo."',
                     '- Matriz del administrador: "El administrador debe conservar acceso total a Usuarios y Matriz de acceso."',
                     '- Foto demasiado grande: "La foto no debe superar 2 MB."', SIN_BD]),
    'CU2': dict(
        gestionar='Gestionar Captación de la Oferta', iniciador='Visitante',
        proposito='Captar prospectos desde el catálogo público de programas y módulos.',
        descripcion='El visitante consulta el catálogo por área y programa, busca módulos y registra su interés con sus '
                    'datos; el registro crea el prospecto y su interés. En el panel, el Administrador y el Coordinador '
                    'consultan la oferta académica y la sincronizan desde el catálogo del Grupo 06 (simulado).',
        precondicion='El catálogo tiene programas y módulos abiertos.',
        proceso=['El visitante abre el Catálogo de Programas.',
                 'El sistema lista los programas y módulos abiertos y cuenta la visita.',
                 'El visitante elige un programa o un módulo y presiona Me interesa.',
                 'El visitante ingresa nombre, apellido, documento, teléfono, correo, profesión y ubicación.',
                 'El sistema valida los datos y registra el prospecto y su interés.',
                 'El sistema muestra el mensaje de registro exitoso.'],
        postcondicion='El prospecto y su interés quedan registrados, listos para asignarse a un vendedor.',
        excepciones=['- Módulos de varios programas: "Seleccione módulos de un solo programa por registro."',
                     '- Módulo cerrado: "Uno o más módulos seleccionados ya no están disponibles. Revise la selección."',
                     '- Datos de otra persona: "Ese correo o carnet ya está registrado con otros datos. Comuníquese con coordinación."',
                     SIN_BD]),
    'CU3': dict(
        gestionar='Gestionar Asignación de Prospectos', iniciador='Coordinador',
        proposito='Registrar prospectos y repartirlos entre los vendedores.',
        descripcion='El Coordinador o el Administrador registran prospectos a mano o por CSV con su origen y los asignan a '
                    'un vendedor de forma manual o por reparto Round-Robin; cada vendedor ve su cartera.',
        precondicion='El usuario tiene permiso de modificación sobre Asignación de prospectos y hay vendedores activos.',
        proceso=['El Coordinador abre Prospectos y registra un prospecto o importa un archivo CSV.',
                 'El sistema valida cada fila y registra los prospectos con su interés.',
                 'El Coordinador abre Asignación de Prospectos y filtra las tarjetas sin asignar.',
                 'El Coordinador asigna una tarjeta a un vendedor o reparte las pendientes por Round-Robin.',
                 'El sistema guarda la asignación y la tarjeta aparece en la cartera del vendedor.'],
        postcondicion='Cada prospecto asignado queda en la cartera de su vendedor.',
        excepciones=['- Registro por un vendedor: "Solo coordinación registra e importa prospectos."',
                     '- CSV con errores: "El archivo tiene errores; no se cargó ningún prospecto."',
                     '- CSV con columnas repetidas: "El archivo tiene columnas repetidas."',
                     '- Usuario que no es vendedor: "El usuario seleccionado no es vendedor."',
                     '- Sin vendedores: "No hay vendedores activos para repartir."',
                     '- Nada que repartir: "No había prospectos sin asignar."', SIN_BD]),
    'CU4': dict(
        gestionar='Gestionar Embudo de Ventas', iniciador='Vendedor',
        proposito='Llevar cada prospecto por las etapas del embudo de ventas.',
        descripcion='El usuario ve las tarjetas de su alcance en un tablero Kanban de seis columnas y las mueve '
                    'arrastrándolas o con la opción Mover a…; el sistema valida cada cambio de estado.',
        precondicion='El usuario tiene permiso de modificación sobre Embudo de ventas y la tarjeta está en su alcance '
                     '(cartera del vendedor o programas del coordinador).',
        proceso=['El usuario abre Embudo de Ventas.',
                 'El sistema muestra las tarjetas por estado: Nuevo, En Contacto, Seguimiento, Promesa de Pago, Convertido y Perdido.',
                 'El usuario arrastra una tarjeta o elige Mover a… y el estado de destino.',
                 'El sistema valida la regla del estado de destino y guarda el cambio.',
                 'El tablero muestra la tarjeta en su nueva columna.'],
        postcondicion='La tarjeta queda en el nuevo estado del embudo.',
        excepciones=['- Tarjeta fuera de su cartera: "Este prospecto no está dentro de su cartera."',
                     '- Tarjeta convertida: "Una tarjeta convertida ya tiene matrícula: no se puede mover."',
                     '- Tarjeta cerrada: "La tarjeta ya está cerrada."',
                     '- Tarjeta sin vendedor: "La tarjeta no tiene vendedor asignado."', SIN_BD]),
    'CU5': dict(
        gestionar='Gestionar Pérdida y Motivos', iniciador='Vendedor',
        proposito='Registrar por qué se pierde un prospecto, con un motivo clasificado.',
        descripcion='Al pasar una tarjeta a Perdido, el usuario elige un motivo de la lista clasificada por categoría y '
                    'puede añadir una observación. El Administrador y el Coordinador registran, modifican y eliminan los motivos.',
        precondicion='Existen motivos de pérdida registrados y el usuario tiene permiso de modificación sobre Embudo de '
                     'ventas (o sobre Motivos de pérdida para gestionarlos).',
        proceso=['El usuario elige Perdido para una tarjeta del Embudo de Ventas.',
                 'El sistema muestra el formulario Marcar como Perdido con los motivos agrupados por categoría.',
                 'El usuario elige el motivo y escribe una observación.',
                 'El sistema guarda el estado Perdido con su motivo.',
                 'El Administrador o el Coordinador gestionan la lista en Motivos de Pérdida.'],
        postcondicion='La tarjeta queda en Perdido con su motivo.',
        excepciones=['- Perdido sin motivo: el sistema rechaza el cambio y pide el motivo.',
                     '- Motivo repetido: "El motivo ya está registrado."',
                     '- Motivo en uso: "No se puede eliminar: hay prospectos perdidos con este motivo."',
                     '- Motivo del sistema: "Este motivo lo usa el sistema y no se puede cambiar ni eliminar."', SIN_BD]),
    'CU6': dict(
        gestionar='Gestionar Conversión a Matrícula', iniciador='Vendedor',
        proposito='Cobrar al prospecto y convertirlo en alumno matriculado con sus datos validados.',
        descripcion='Desde la ficha del prospecto, el Vendedor registra métodos de pago, genera la orden de pago al '
                    'contado o en cuotas y sube el comprobante o cobra con la tarjeta simulada; el Coordinador o el '
                    'Administrador aprueban o rechazan la cuota. Con los datos completos y la primera cuota aprobada, la '
                    'tarjeta pasa a Convertido, se registran la inscripción y la comisión, y la matrícula se exporta al SIS.',
        precondicion='El prospecto está en la cartera del vendedor y tiene un interés abierto.',
        proceso=['El Vendedor abre la ficha del prospecto y registra un método de pago.',
                 'El Vendedor genera la orden de pago con módulos, descuentos y número de cuotas.',
                 'El Vendedor sube el comprobante de la cuota o la cobra con la tarjeta registrada, y la cuota queda en revisión.',
                 'El Coordinador revisa el comprobante en Validación de Pagos y aprueba o rechaza la cuota.',
                 'Con la primera cuota aprobada y los datos completos, el sistema pasa la tarjeta a Convertido y registra '
                 'la inscripción y la comisión.',
                 'El Coordinador exporta las matrículas pendientes al SIS en Matrículas y SIS y registra el resultado.'],
        postcondicion='El prospecto queda convertido en alumno, con su inscripción, comisión y exportación registradas.',
        excepciones=['- Orden de otro vendedor: "Solo el vendedor asignado genera la orden de pago."',
                     '- Total inválido: "El total de la orden debe ser mayor a cero."',
                     '- Tarjeta inválida: "El número de tarjeta no es válido."',
                     '- Tarjeta vencida: "La tarjeta está vencida."',
                     '- Comprobante repetido: "Ya hay un comprobante en revisión para esta cuota."',
                     '- Aprobación fuera de revisión: "Solo se aprueba una cuota en revisión."',
                     '- Conversión sin pago: "La primera cuota de una orden de pago todavía no está aprobada."',
                     '- Exportación vacía: "No hay matrículas pendientes de enviar."', SIN_BD]),
    'CU7': dict(
        gestionar='Gestionar Seguimiento del Prospecto', iniciador='Vendedor',
        proposito='Registrar el seguimiento de cada prospecto para que ningún contacto se olvide.',
        descripcion='En la ficha del prospecto el usuario ve el historial cronológico de la tarjeta, registra '
                    'interacciones y notas y agenda recordatorios; en Mi Día ve su agenda y marca los recordatorios '
                    'realizados. Las notificaciones internas avisan de las novedades.',
        precondicion='La tarjeta está en el alcance del usuario.',
        proceso=['El Vendedor abre Seguimiento y Agenda y elige una tarjeta.',
                 'El sistema muestra la ficha con el historial cronológico, los recordatorios y las órdenes de pago.',
                 'El Vendedor registra una interacción con su tipo, descripción y resultado.',
                 'El Vendedor agenda un recordatorio con fecha, hora y descripción.',
                 'En Mi Día, el Vendedor marca el recordatorio como realizado con su resultado, o lo cancela.',
                 'El usuario consulta sus notificaciones y las marca como leídas.'],
        postcondicion='La interacción y el recordatorio quedan en el historial de la tarjeta.',
        excepciones=['- Fecha pasada: "La actividad debe programarse para una fecha y hora futura."',
                     '- Actividad cerrada: "La actividad ya fue realizada o cancelada."',
                     '- Notificación a un prospecto ajeno: "Solo puede escribir a prospectos de su cartera."', SIN_BD]),
    'CU8': dict(
        gestionar='Gestionar Reportes y Estadísticas', iniciador='Coordinador',
        proposito='Medir el avance comercial y el uso del sistema.',
        descripcion='El usuario consulta el dashboard con indicadores y gráficos, los reportes como listados filtrados '
                    'por fechas, estado y vendedor, y las estadísticas porcentuales del embudo; en Ventas y Comisiones '
                    'se consultan y pagan las comisiones de los vendedores.',
        precondicion='El usuario tiene permiso de lectura sobre Dashboard, Reportes y estadísticas o Ventas y comisiones.',
        proceso=['El usuario abre el Dashboard y ve los indicadores y gráficos de su alcance.',
                 'El usuario abre Reportes y Estadísticas y filtra por fechas, estado y vendedor.',
                 'El sistema muestra el listado y las estadísticas porcentuales.',
                 'El usuario descarga el listado en CSV.',
                 'En Ventas y Comisiones, el usuario con permiso de modificación consulta el resumen y paga las comisiones; '
                 'solo el Administrador cambia el porcentaje de comisión.'],
        postcondicion='El usuario obtiene los reportes y estadísticas de su alcance; las comisiones pagadas quedan registradas.',
        excepciones=['- Porcentaje de comisión: "Solo el administrador cambia el porcentaje de comisión."',
                     '- Sin permiso: "No tiene permiso para realizar esta acción."', SIN_BD]),
}


# Actores por CU según lo que cada rol HACE en el sistema (navegacion.py usa los mismos permisos). La matriz liga cada
# página a un solo CU, pero una acción de otro CU puede vivir en esa página: p. ej. el vendedor marca "Perdido" con motivo
# (CU5) desde el Embudo (página de CU4). documento_p2.py comprueba que cada página permitida a un rol esté en sus CU.
ACTORES_CU = {
    'CU1': ['Administrador', 'Coordinador', 'Vendedor'],   # todos: sesión, perfil, contraseña; administrador: usuarios, matriz, bitácora
    'CU2': ['Administrador', 'Coordinador', 'Visitante'],   # visitante: catálogo y registro de interés; panel: oferta académica
    'CU3': ['Administrador', 'Coordinador', 'Vendedor'],    # alta/CSV/asignación: admin y coord.; vendedor: su cartera
    'CU4': ['Administrador', 'Coordinador', 'Vendedor'],    # embudo Kanban
    'CU5': ['Administrador', 'Coordinador', 'Vendedor'],    # vendedor marca Perdido con motivo; admin y coord. gestionan motivos
    'CU6': ['Administrador', 'Coordinador', 'Vendedor'],    # vendedor: orden y comprobante; coord.: validación, matrícula y SIS
    'CU7': ['Administrador', 'Coordinador', 'Vendedor'],    # interacciones, recordatorios, notificaciones
    'CU8': ['Administrador', 'Coordinador', 'Vendedor'],    # dashboard / Mi día, reportes, comisiones
}


def actores_cu(cu):
    return ACTORES_CU[cu]


# ---------------------------------------------------------------- Capítulo VI: Análisis
# Cada paquete es dueño de sus tablas (clase 03): documento_p2.py exige que juntas sean todas las tablas de la BD, sin repetir.
PAQUETES = {
    'Seguridad y Acceso': dict(cu=['CU1'], tablas=['roles', 'usuarios', 'api_tokens', 'recursos', 'permisos', 'bitacora',
                                                    'log_comandos', 'programas_responsables'],
                               descripcion='Gestiona los usuarios, sus roles y vigencia, los tokens de sesión, la matriz '
                                           'de acceso (recursos y permisos) y la bitácora de accesos.'),
    'Oferta Académica': dict(cu=['CU2'], tablas=['programas', 'catalogo_cache'],
                             descripcion='Gestiona el catálogo de programas y módulos que se ofrece al público.'),
    'Gestión de Prospectos': dict(cu=['CU3', 'CU4', 'CU5'], tablas=['prospectos', 'intereses', 'movimientos_interes', 'motivos_perdida'],
                                  descripcion='Gestiona los prospectos, sus intereses como tarjetas del embudo, sus '
                                              'movimientos y los motivos de pérdida.'),
    'Pagos y Matrícula': dict(cu=['CU6'], tablas=['metodos_pago', 'descuentos', 'ordenes_pago', 'orden_pago_descuentos',
                                                   'cuotas', 'pagos', 'comprobantes_pago', 'solicitudes_compra',
                                                   'inscripciones_comerciales', 'exportaciones'],
                              descripcion='Gestiona los métodos de pago, las órdenes de pago y sus cuotas, los '
                                          'comprobantes, la inscripción y la exportación de la matrícula al SIS.'),
    'Seguimiento Comercial': dict(cu=['CU7'], tablas=['interacciones', 'recordatorios', 'notificaciones'],
                                  descripcion='Gestiona las interacciones, los recordatorios de contacto y las notificaciones.'),
    'Ventas y Reportes': dict(cu=['CU8'], tablas=['comisiones', 'configuraciones'],
                              descripcion='Gestiona las comisiones de los vendedores, su configuración y los reportes y '
                                          'estadísticas del sistema.'),
}

# ---------------------------------------------------------------- Capítulos VIII–XIII
# Herramientas: (nombre, versión, descripción). La versión 'composer:paquete' / 'npm:paquete' se lee del lock de crm-web
# al generar; las demás son las verificadas (servidor: P2_WEB.md; BD: fuentes/esquema.sql); '' = sin versión.
# Descripción None = pendiente.
HERRAMIENTAS = {
    'Herramientas de Programación y Desarrollo': [
        ('PHP', '8.4', 'Lenguaje de la capa de negocio y de la capa de datos; el servidor de la facultad ejecuta PHP 8.4.'),
        ('Laravel', 'composer:laravel/framework', 'Framework de la capa de negocio: expone la API RESTful '
                    '(negocio/routes/api.php) con controladores, requests de validación, servicios y los middleware de '
                    'token y de matriz de acceso; sus migraciones crean la base de datos.'),
        ('React', 'npm:react', 'Biblioteca de la capa de presentación: cada página del sistema es un componente '
                               '(presentacion/src/paginas).'),
        ('React Router', 'npm:react-router-dom', 'Enrutamiento de la aplicación de una sola página: una ruta por página '
                                                 'del diagrama de navegación (presentacion/src/rutas.jsx).'),
        ('Tailwind CSS', 'npm:tailwindcss', 'Estilos de la interfaz: tokens de los tres temas, día/noche y alto contraste '
                                            'en presentacion/src/estilos, y utilidades en cada componente.'),
        ('Axios', 'npm:axios', 'Cliente HTTP único (presentacion/src/api/cliente.js) que envía el token Bearer y consume la API RESTful.'),
        ('Vite', 'npm:vite', 'Servidor de desarrollo y empaquetador de la capa de presentación; genera el build que se publica.'),
        ('Chart.js', 'npm:chart.js', 'Gráficos del Dashboard y de Reportes y Estadísticas.'),
        ('Lucide React', 'npm:lucide-react', 'Íconos de la interfaz.'),
        ('Playwright', 'npm:playwright', 'Pruebas de caja negra en los navegadores Chromium, Firefox y WebKit '
                                         '(scripts/verificar_navegadores.mjs).')],
    'Herramientas de Gestión de Bases de Datos': [('PostgreSQL', '18', 'Gestor de la base de datos db_grupo05sa (esquema '
                                                                       'public), compartida con el Proyecto 1.')],
    'Herramientas de Diseño y Modelado': [('Enterprise Architect', '15 Trial', 'Modelado UML del sistema (casos de uso, '
                                           'paquetes, clases, base de datos y navegación), automatizado por COM desde generadorDocumento/ea.')],
    'Herramientas de Control de Versiones y Colaboración': [('Git', '', 'Control de versiones del código fuente.'),
                                                            ('GitHub', '', 'Repositorio remoto del grupo (ver 13. Anexo).')],
}
def _resultado():
    """Un párrafo por actor armado con su menú real (matriz de acceso de la migración 000003), entre uno general y uno de cierre."""
    def menu(rol):
        nombres = [RECURSOS[c]['nombre'] for c in sorted(PERMISOS[rol], key=list(RECURSOS).index)]
        return ', '.join(nombres[:-1]) + ' y ' + nombres[-1]
    return [
        'Se espera un sistema web de 3 capas publicado en el servidor de la facultad en el que cada usuario vea solo el '
        'menú que le da su rol en la matriz de acceso y en el que cada acción quede validada en el servidor.',
        'El Visitante podrá consultar el catálogo de programas y módulos, buscar en él y registrar su interés sin iniciar sesión.',
        f'El Administrador podrá usar {menu("administrador")}, con permiso de eliminación sobre cada uno.',
        f'El Coordinador podrá usar {menu("coordinador")}, sobre los programas a su cargo.',
        f'El Vendedor podrá usar {menu("vendedor")}, sobre los prospectos de su cartera.',
        'Así, ningún prospecto queda sin seguimiento y la coordinación sabe en todo momento en qué etapa está cada uno y '
        'por qué se pierde.']


RESULTADO_ESPERADO = _resultado()
# (título, objetivo, criterio de éxito, caso literal en el script). documento_p2.py exige que el caso exista en el script:
# caja blanca = scripts/verificar_p2.py (API y reglas internas: bitácora, matriz, triggers); caja negra =
# scripts/verificar_navegadores.mjs (la interfaz en Chromium, Firefox y WebKit, sin mirar el código).
PRUEBAS_BLANCA = [
    ('Bitácora de accesos', 'Comprobar que el login fallido y el acceso denegado quedan registrados en la bitácora.',
     'La bitácora contiene el login fallido con su IP y el acceso denegado.', 'el login fallido queda en la bitácora con IP'),
    ('Menú dinámico por rol', 'Comprobar que el menú de cada rol se arma desde la matriz de acceso de la base de datos.',
     'El menú del vendedor no incluye usuarios ni validación de pagos e incluye el embudo.', 'menú vendedor sin usuarios ni validación'),
    ('Matriz aplicada en el servidor', 'Comprobar que la API rechaza una acción sin permiso aunque se llame directamente.',
     'El vendedor recibe 403 al listar usuarios.', 'vendedor no puede listar usuarios (403)'),
    ('Cambio de permiso sin tocar código', 'Comprobar que asignar un permiso en la matriz cambia el menú del rol.',
     'El recurso aparece en el menú del rol tras asignarlo.', 'al dar un permiso aparece en el menú del rol'),
    ('Cartera del vendedor (RF1.2)', 'Comprobar que el vendedor ve solo las tarjetas de su cartera.',
     'Todas las tarjetas devueltas tienen como vendedor al usuario que consulta.', 'RF1.2 vendedor ve solo su cartera'),
    ('Pérdida con motivo (RF3.3)', 'Comprobar que pasar una tarjeta a Perdido exige un motivo.',
     'La API responde 422 con un mensaje sobre el motivo.', 'Perdido sin motivo se rechaza'),
    ('Conversión validada (RF3.4)', 'Comprobar que una tarjeta no se convierte sin la primera cuota aprobada.',
     'La API responde 422 con la lista de lo que falta.', 'Convertido sin pago aprobado se rechaza'),
    ('Plan de cuotas', 'Comprobar que una orden en tres cuotas reparte el total.',
     'La orden tiene tres cuotas cuya suma es el total.', 'orden con plan de 3 cuotas'),
    ('Conversión al aprobar la primera cuota', 'Comprobar que con datos completos y la primera cuota aprobada la tarjeta pasa a Convertido.',
     'La tarjeta queda en Convertido.', '1.ª cuota aprobada + datos completos = Convertido'),
    ('Contador de visitas', 'Comprobar que el contador persistente (trigger) suma cada visita.',
     'Las visitas de la página suben en 1.', 'el contador de visitas sube en 1'),
    ('Importación CSV (RF2.1)', 'Comprobar el rechazo de un CSV con prospectos ya registrados.',
     'El CSV duplicado se rechaza sin cargar ningún prospecto.', 'CSV duplicado se rechaza sin cargar nada'),
    ('Estadísticas porcentuales', 'Comprobar que las estadísticas del embudo son porcentajes que suman 100 %.',
     'La suma de los porcentajes del embudo es 100 % (± 1).', 'estadísticas porcentuales'),
]
PRUEBAS_NEGRA = [
    ('Catálogo y registro público en el celular', 'Comprobar que el visitante registra su interés desde un celular (390 × 844).',
     'Aparece "Interés registrado correctamente." y el botón de envío no queda recortado.', 'catalogo y registro publico movil'),
    ('Inicio de sesión sin recordar', 'Comprobar que sin "Recordarme" la sesión dura solo mientras la pestaña está abierta.',
     'El token queda en sessionStorage y no en localStorage, y al recargar sigue en su página de inicio.', ' login sin recordar'),
    ('Páginas del menú en cuatro anchos y dos temas', 'Comprobar cada página del menú de cada rol en 320, 390, 768 y 1280 px, en modo claro y oscuro.',
     'Ninguna página desborda horizontalmente, no hay imágenes rotas ni mensajes de error visibles.', "role.id+' '+path"),
    ('Errores de ejecución y del servidor', 'Comprobar que recorrer el sistema no produce errores.',
     'No hay errores de JavaScript ni respuestas 500 del servidor.', ' errores de ejecucion y servidor'),
    ('Protección del último administrador', 'Comprobar que la interfaz no deja desactivar al único administrador.',
     'Aparece "Debe conservar al menos un administrador activo." y la cuenta sigue activa.', 'proteccion del ultimo administrador en la interfaz'),
    ('Vendedor sin acceso a páginas ajenas', 'Comprobar que el vendedor no abre Usuarios, Validación de pagos, Asignación ni Matrículas.',
     'Cada intento lo devuelve a su página de inicio.', 'vendedor no abre usuarios ni pagos'),
    ('Cierre de sesión', 'Comprobar que cerrar sesión elimina el token.',
     'Vuelve al login y no queda token guardado en el navegador.', ' cierre de sesion'),
]
CONCLUSIONES = []           # una por objetivo específico, mismo orden
BIBLIOGRAFIA = []
ANEXOS = []                 # (título, ruta de imagen); solo documentos que existan
URL_GITHUB = None   # se lee de .git/config de crm-web al generar (documento_p2.py)

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
PERMISOS = {rol: dict(re.findall(r"'([\w-]+)' => '(\w+)'", cuerpo))
            for rol, cuerpo in re.findall(r"'(\w+)' => \[(.*?)\]", _MIG.split('PERMISOS = [')[1].split('];')[0], re.S)}
# el administrador recibe eliminación sobre todo recurso privado salvo "Mi día" (up() de la misma migración)
PERMISOS['administrador'] = {c: 'eliminacion' for c, r in RECURSOS.items() if not r['publico'] and c != 'inicio-vendedor'}

# ---------------------------------------------------------------- Capítulo I: Perfil
INTRODUCCION = None          # 3 párrafos
ANTECEDENTES = None          # 3 párrafos; el 3.º: justificación teórica, metodológica y práctica
PROBLEMA = None              # situación, causas, pronóstico, solución
OBJETIVO_GENERAL = None      # una línea: "Desarrollar un …"
OBJETIVOS_ESPECIFICOS = []   # viñetas en infinitivo, alineadas a las fases PUDS (11. Conclusión responde una por una)
METODOLOGIA = None           # intro PUDS + UML; luego FASES
FASES = {'Inicio (Inception).': None, 'Elaboración (Elaboration).': None,
         'Construcción (Construction).': None, 'Transición (Transition).': None}
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

# ---------------------------------------------------------------- Capítulo III: Organización (UNEXO)
# Los textos del P1 eran de la Unidad de Capacitación de la FICCT: no se reutilizan. Faltan los datos reales de UNEXO.
MISION = None
VISION = None
OBJETIVO_EMPRESA = None
UBICACION = None
ORGANIGRAMA = 'Organigrama de UNEXO'

# ---------------------------------------------------------------- Capítulo IV: Requerimientos (P2_WEB.md §2)
REQUERIMIENTOS = [   # (título, párrafo "El sistema permitirá…"); fuente: requerimientos del grupo publicados el 14/09/2026
    ('Acceso por roles', None), ('Cartera del vendedor', None), ('Alcance del coordinador', None),
    ('Registro de prospectos', None), ('Interés vinculado al catálogo', None), ('Asignación de prospectos', None),
    ('Tablero Kanban', None), ('Estados del embudo', None), ('Motivo de pérdida', None), ('Validación de conversión', None),
    ('Historial de interacciones', None), ('Notas manuales', None), ('Recordatorios de contacto', None),
]

# ---------------------------------------------------------------- Capítulo V: Captura de requisitos
ACTORES = [   # (actor, características). Roles reales de la tabla roles + el visitante del catálogo público (CU2)
    ('Administrador', 'Gestiona usuarios y toda la operación comercial.'),
    ('Coordinador', 'Asigna interesados, valida pagos y supervisa vendedores.'),
    ('Vendedor', 'Da seguimiento a los interesados asignados.'),
    ('Visitante', None),
]
CU = {   # nombres aprobados por el docente (foro, 5/10/2026)
    'CU1': 'Gestión de Usuarios (Propietario, Clientes)', 'CU2': 'Gestión de Captar, Consumir Oferta',
    'CU3': 'Gestión de Asignar Prospectos (Leads)', 'CU4': 'Gestión de Embudo de Ventas en Tablero Kanban',
    'CU5': 'Gestión de Pérdida de Prospectos y Clasificación de Motivos',
    'CU6': 'Gestión de Validar Datos y Procesar Conversión a Matrícula',
    'CU7': 'Gestión de Bitácora, Interacciones y Recordatorios', 'CU8': 'Reportes y Estadísticas'}
PRIORIDAD = {}   # {'CU1': 'Alta', …}
ALCANCE = {}     # {'CU1': 'párrafo del alcance', …}
DETALLE = {}     # {'CU1': dict(gestionar='Gestionar Usuarios', proposito=…, descripcion=…, iniciador=…,
                 #               precondicion=…, proceso=[…], postcondicion=…, excepciones=['- …'])}


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
PAQUETES = {}    # {'Seguridad y Acceso': dict(descripcion='Gestiona …', cu=['CU1'])}

# ---------------------------------------------------------------- Capítulos VIII–XIII
# Herramientas: (nombre, versión, descripción). La versión 'composer:paquete' / 'npm:paquete' se lee del lock de crm-web
# al generar; las demás son las verificadas (servidor: P2_WEB.md; BD: fuentes/esquema.sql); '' = sin versión.
# Descripción None = pendiente.
HERRAMIENTAS = {
    'Herramientas de Programación y Desarrollo': [
        ('PHP', '8.4', None), ('Laravel', 'composer:laravel/framework', None),
        ('React', 'npm:react', None),
        ('React Router', 'npm:react-router-dom', None), ('Tailwind CSS', 'npm:tailwindcss', None), ('Axios', 'npm:axios', None), ('Vite', 'npm:vite', None),
        ('Chart.js', 'npm:chart.js', None), ('Lucide React', 'npm:lucide-react', None), ('Playwright', 'npm:playwright', None)],
    'Herramientas de Gestión de Bases de Datos': [('PostgreSQL', '18', None)],
    'Herramientas de Diseño y Modelado': [('Enterprise Architect', '15 Trial', None)],
    'Herramientas de Control de Versiones y Colaboración': [('Git', '', None), ('GitHub', '', None)],
}
RESULTADO_ESPERADO = None   # párrafo general, uno por actor, cierre
PRUEBAS_BLANCA = []         # (título, objetivo, criterio de éxito); deben existir en crm-web/scripts
PRUEBAS_NEGRA = []
CONCLUSIONES = []           # una por objetivo específico, mismo orden
BIBLIOGRAFIA = []
ANEXOS = []                 # (título, ruta de imagen); solo documentos que existan
URL_GITHUB = None

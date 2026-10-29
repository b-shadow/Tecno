# Cómo trabaja y qué exige el docente — síntesis de las clases grabadas

Fuente: lista de YouTube https://youtube.com/playlist?list=PLLaXrPKv1SoI (48 videos al 17/11/2026, ~26 h, Ing. Evans Balcázar,
INF513 2-2026). Se leyeron las 38 transcripciones automáticas de YouTube; los videos 35 y 36, que no tienen subtítulos, se
transcribieron con Whisper (`faster-whisper`, modelo small; el 36 salió con muchos errores).
Transcripciones e índice con enlaces: `referencias/clases-youtube/` (para buscar una cita: `grep -i "desafío" referencias/clases-youtube/*.txt`).
Entre corchetes va el número de video. Lo dicho en clase complementa al aula; si una fecha choca, manda el aula.

---

## 1. Cómo evalúa

### La defensa (lo que más pesa)
- **Desafío en vivo** [40, 05]: pide una modificación pequeña en el momento, p. ej. *"al lado de 'Listado amigo' ponga su nombre"*
  o *"al lado de 'Análisis de requerimientos' pongan su nombre"* en una vista. **Si no lo resuelven, la defensa vale 0** ("alguien se los
  hizo"). Dice que la mitad de los grupos falla en eso. En Laravel puede pedir *"agregue un captcha"*, *"un dato más para autenticar"*,
  *"un tercer mecanismo de autenticación"*: hay que saber qué vista y qué controlador tocar [38, 40].
- **Evaluación individual dentro del grupo** [40]: hablan los tres por igual. Si le pregunta a uno, responde ese; califica al que responde.
  El que se queda parado sin aportar baja la nota (aunque sea "cuchicheando" al compañero que está en el teclado).
- **Tiempo**: 20–25 min por grupo, todo el día de 7:00 en adelante [05, 40]. Si algo falla al principio, se va el tiempo arreglándolo.
- **Ayuda**: antes de la defensa ayuda con errores (mandar captura); el día de la defensa no [40].
- **Subir con 2 días de anticipación** [40]: la última noche el servidor de la materia colapsa (ancho de banda, librerías subidas a medias,
  la BD no responde). Probar en el servidor, no solo en local: Windows ≠ Linux (librerías, permisos, rutas).
- Pregunta conceptos al que está defendiendo: *"si no me saben explicar, no saben; y si no saben, no pasa"* [05]. Revisa proyectos
  todo el día (7 a 23 h) [05].

### Revisión del documento [06]
Lo revisa completo: objetivo general, objetivos específicos, **organigrama de la empresa**, actores, casos de uso, diagramas de secuencia
y de colaboración, diseño conceptual, lógico y físico, **pantallas**, hasta las conclusiones. Lo que más mira: **la base de datos y el
diagrama de navegación**.

### Otras reglas
- **Trabajos en grupo** (solo estos): exposición, servidor en la nube, Proyecto 1 y Proyecto 2. **Todo lo demás es individual** [26].
  En un trabajo grupal, *"si veo uno solito en la carátula, no lo reviso"* [19].
- **Tareas atrasadas**: bajan cada día hasta llegar a 0 (dio el ejemplo de −30); si se entrega tarde, anotar en el campo de texto de la
  tarea la fecha y el motivo (p. ej. inscripción especial) [01, 13].
- **Uso de la IA** [01, 40]: no la prohíbe, pero detecta el código generado (formularios con "600 parámetros" inline, nombres de archivo
  sin sentido). Lo pequeño se hace a mano: es más rápido y más barato que un prompt.
- **CSS siempre en archivo aparte**, con clases definidas y aplicadas; nada de estilos inline [40].
- **Presentación personal** en reuniones con la unidad y en la defensa: ropa limpia y planchada (camisa), peinado, higiene; nada de
  chinelas, gorra o short. *"Es la diferencia entre ser el capataz y ser el albañil"* [19, 26]. ("Puntaje de elegancia").

### Experiencia real en defensas (consejos tácticos de alumnos que ya aprobaron)
Fuente: entrevista en audio/video a estudiante que aprobó la materia (`referencias/CONSEJOS_DEFENSA_ALUMNO.md`, grabación `2026-10-28 22-59-20.mp4`).

- **Pruebas hostiles y sabotajes deliberados en vivo:** El docente evalúa agresivamente si el sistema fue hecho por el grupo o comprado. Durante la defensa o exámenes puede pedir la terminal y **eliminar dependencias, borrar archivos de configuración o cortar conexiones** para ver si el estudiante sabe recuperarse. También puede reiniciar su servidor en plena exposición (~10 min) y alegar que se acabó el tiempo.
- **Táctica de equipo en la mesa de defensa:**
  - **1 integrante al frente:** de pie, formal (camisa y zapatos), compartiendo pantalla y exponiendo con solvencia técnica.
  - **2 integrantes de soporte en la mesa:** con laptops abiertas monitoreando logs en terminal, verificando que el servidor siga arriba y vigilando que no se rompan dependencias.
  - **Cheat Sheet de comandos de rescate:** tener un Word/bloc de notas con todos los comandos de Linux exactos para clonar el repositorio, instalar dependencias y levantar el sistema de cero en <2 minutos.
  - **Cambios en vivo:** si pide modificar la interfaz, ubicarlos rápido con `Ctrl + F` en Visual Studio Code.
- **Trampa de la red / IP dinámica de la Facultad:** El router WiFi de los laboratorios/aulas cambia de IP pública al reiniciarse. Si cambia, el firewall de `tecnoweb.org.bo` bloquea las conexiones SSH, HTTP o PostgreSQL. Muchos grupos reprueban por esto creyendo que su código falló. **Regla:** apenas llegar al aula, verificar la IP asignada (`curl ifconfig.me`) y probar conectividad con comandos listos; si falla, mostrárselo de inmediato al docente en la terminal para que desbloquee la IP.
- **Arquitectura real del P1 (E-mail):** el sistema corre **100 % local** en la máquina del grupo; solo la BD PostgreSQL y el servidor de correo son remotos. El sistema local **debe imprimir logs claros en la terminal**: si el servidor SMTP o la BD no responden, el log debe decir explícitamente `[ERROR RED] Timeout en mail.tecnoweb.org.bo` para demostrarle al docente que el fallo es de su servidor. Probar con múltiples dominios de correo (Gmail, corporativo, institucional).
- **Rigor fatal: Diagrama Conceptual vs. Diagrama de Clases:**
  - *Diagrama Conceptual:* solo entidades y atributos esenciales de negocio. **Prohibido:** tipos de datos (`VARCHAR`, `INT`), llaves PK/FK y métodos/funciones. Si se titula Conceptual y tiene PK/FK o funciones, el docente te manda a sentar con nota 0.
  - *Diagrama de Clases:* clases formales con atributos tipados, visibilidad (`+`, `-`), métodos con parámetros y relaciones formales.
- **Estrategia del Visto Bueno previo:** llevar el documento impreso días antes (p. ej. un miércoles) a su clase/consulta. Si el docente valida previamente el documento o el diagrama conceptual, la defensa es mucho más tranquila.
- **Tareas regulares e investigaciones:** el docente casi nunca las revisa a fondo y suele poner 100 si están completas y bien presentadas; pero la fecha de entrega es inamovible (con retraso vale 50 % y a los 3–4 días vale 0).

---

## 2. El documento del proyecto (PUDS), según sus clases [03, 04, 28]

El mismo diseño sirve para el P1 y el P2: *"los planos sirven para construir de adobe o de ladrillo"*. Solo cambia la implementación
[16, 26]. Tres bloques de ingeniería; la implementación lleva una hoja con la nota de que el código va comprimido aparte, y al final van
las pruebas (tablas).

### Captura de requisitos
- **Lista de requerimientos** agrupada por función o área, con prioridad y ciclo en que se implementa.
- **Modelo de negocio** con diagrama de actividades (o el diagrama de CU, si alcanza para entender el negocio).
- **Modelo de dominio inicial**: solo las entidades de la primera reunión, **sin atributos**.
- **Diagrama general de casos de uso**: es el **menú por actor** y de él sale la **matriz de control de acceso**.
  - **No generalizar actores** (nada de un "Usuario" genérico): se pierde la matriz de acceso. *"Todos los semestres lo generalizan"*.
  - **No hacer explosión** de CU en esta etapa (login es login). La explosión va en Análisis.
- **Descripción de cada CU**: actores concretos, flujo principal, **subflujos aparte** (no todo en el principal) y **excepciones**
  (*"casi todos los CU tienen y se olvidan"*: BD caída, error de conexión, credencial vencida...).
  - Ejemplo del login: subflujo 1 = credenciales inválidas → mensaje; subflujo 2 = válidas → se arma el menú; excepciones = cuenta
    inactiva, **fuera de fecha inicio/fecha fin**, servidor caído.
  - **Toda credencial lleva fecha inicio, fecha fin y rol** [03]: *"Laravel lo hace automático y yo le pregunto: ¿hasta cuándo dura esta
    credencial?"*.

### Análisis
- **Paquetes o subsistemas** (un módulo por equipo de desarrollo) y sus dependencias.
- Explosión de los CU complejos (`«include»`, sub-CU).
- Por CU, un **diagrama de clases de análisis** (interfaz, control y entidad, solo estereotipos; las entidades salen del modelo de
  dominio) y un **diagrama de colaboración**; identificación de responsables.
- **Alta cohesión y bajo acoplamiento**: cada paquete es **dueño de sus tablas**; ningún otro módulo hace SELECT ni UPDATE sobre ellas;
  se comunican por **interfaces** (servicios o API). *"Hacer select a las tablas de otro módulo es de instituto"*.

### Diseño
- Interfaces entre paquetes y **diagrama de despliegue** (servidor web, servidor de BD, firewall, router, internet, usuarios internos y
  externos; el protocolo se anota cuando se usa más de uno).
- **CU a nivel de diseño**: diagrama de clases **completo** (la interfaz con sus campos y el bosquejo de pantalla; el gestor con atributos
  y métodos mínimos como `verificarDatos`, `generarMenu`; las tablas con campos y **tipos de dato**) y diagrama de secuencia. *"Es el
  plano que el programador implementa tal cual"*.
- **Modelo de dominio final** y BD en tres niveles: conceptual, lógico y físico (§4).
- **Diagramas de navegación**, por actor y por CU (§3).
- **Diseño de pantallas**: un bosquejo por cada página del diagrama de navegación (login, mensaje de error, **menú por rol**, registrar y
  su mensaje de éxito o fallo, modificar, listar...). *"Cuando me presentan los documentos no me presentan ni una pantalla"*. Además una
  **paleta de colores** y 3 temas, para que el programador no use sus propios gustos [05, 06].
- En la **aplicación por correo (P1) las pantallas son los comandos y las respuestas**: hay que maquetar la interacción con el cliente
  de correo [28].

---

## 3. Diagrama de navegación: reglas [04, 05, 06, 07]

Hay que seguir **al pie de la letra el paper de Conallen** (tema 2 del aula; dice que se imprima): *"no me puedo inventar estereotipos ni
imágenes; si me observan, digo que seguí el estándar"*.

| Relación | Estereotipo |
|---|---|
| server page → client page | `«build»` |
| client page → client page | `«link»` |
| client page → server page | link **parametrizado** (parámetros de URL, p. ej. `?opcion=2&percod=...` para ver un detalle) |
| `«form»` → server page | `«submit»` (un submit por formulario; una client page puede tener n formularios, p. ej. uno por fila de un listado) |
| frames | cada frame con nombre y `«target»` |

- **Toda clase lleva atributos y operaciones**. Hay dos excepciones: la sesión, y el `«form»`, que no tiene operaciones (sus eventos son
  JavaScript) pero **sí lleva los atributos que envía**. Una clase vacía significa *"no vino a esa clase"*.
- Los errores que más ve: clases vacías, relaciones sin estereotipo, **flechas al revés**.
- El login de ejemplo: client page con `«form»` (usuario, contraseña, enviar) → `«submit»` → server page (recibe los datos, los guarda en
  atributos, verifica) → `«build»` menú o `«build»` mensaje de error, y del error se vuelve al login.
- La pantalla de bienvenida (portada) **no** se diseña como CU; el diseño empieza en la autenticación.
- El diagrama de navegación por actor muestra el login → CU1 → CU2... en el orden en que el programador los implementa. Las clases se
  pueden dibujar como íconos (interfaz, control, entidad), pero para el programador conviene mostrarlas como clase.

---

## 4. Base de datos: lo mínimo que exige [03, 06, 24, 27]

- Diseño conceptual, normalización, diseño lógico y diseño físico; entidad fuerte y débil; relaciones 1-1, 1-N y N-N. *"Si la BD está
  mal, en la defensa le digo que está mal"*; reprobó a gente por esto.
- **Error clásico de N-N** en el conceptual: las dos entidades fuertes se unen por la relación, y de la relación sale una línea punteada
  a la tabla intermedia. Las relaciones **no** van de una entidad fuerte a la tabla intermedia.
- Consultar el diseño de la BD con él o con el profesor de BD **antes** de programar: cambiarla después rompe todo [24].
- PostgreSQL por integridad transaccional. Armar la transacción completa (todas las inserciones relacionadas, con ROLLBACK si falla) en
  vez de inserts sueltos [28].
- Una BD por sistema con su propio rol de login como dueño ("encapsular", como la carpeta de un usuario en Linux) [28].
- Modelo de la Agenda 3C [37]: `persona`, `grupo` y la relación N-N `permiso` (persona+grupo) con **contraseña, fecha_inicio, fecha_fin
  y estado**. Es la forma en que él modela usuarios, roles y vigencia.
- **Revisión de la BD en la defensa [46]** (lo dijo como aviso: *"no hay sorpresa"*). Abre la base con una herramienta que dibuja
  el modelo y mira las relaciones:
  - *"Si yo veo una tabla volando por ahí, ya no reviso ese proyecto"*: toda tabla debe estar relacionada con otra.
  - La clave es la del diseño, con su nombre: si el conceptual dice que la llave es `codigo`, **no** puede aparecer además un `id`
    (*"dos llaves"*). Lo mismo en la intermedia N-N: sin `id` extra junto a las dos FK.
  - Una intermedia N-N no puede quedar "vacía": además de las dos llaves lleva al menos un campo propio.
  - Los campos del documento deben coincidir uno a uno con la BD: *"si hay un campo de más en una tabla ya está mal"*; si no coincide,
    *"siguiente grupo"*. Dio un mes para ajustar.
- En el P2 las tablas se crean con **migraciones** de Laravel, no con SQL a mano; ahí también hay que fijar la llave primaria del
  diseño en vez del `id` por defecto [46, 47, 48].

---

## 5. Proyecto 1 (vía correo): lo que explicó en clase [10, 11, 25, 26, 28]

- *"Usted ha sido contratado como consultor"*. El comando y sus parámetros van en el **Asunto**. El programa lee el correo (POP3),
  **verifica que el comando exista y que los parámetros sean correctos** (cantidad, si faltan o sobran, tipo, formato: *"el parámetro 7 no
  es un correo"*), ejecuta el SELECT o INSERT y responde por SMTP. Si algo falla, **informa el problema concreto**: comando inexistente,
  parámetro N incorrecto, BD caída. Ejemplos: `LISTARPERSONAL["patrón"]`, `INSERTARPERSONAL[ci, nombre, ...]`.
- La tecnología es libre; se puede partir del código de sockets de la clase. Para los de Sistemas sugiere OO o incluso un analizador
  léxico; también vale la "clase cadena".
- De los requisitos publicados por cada grupo, él eligió 8 CU como **"desafío del primer proyecto"**; todos los requisitos van en el P2.
- Base técnica que mostró: el patrón de cada comando es *armar → imprimir lo que se envía → enviar → leer y analizar los 3 primeros
  caracteres de la respuesta*. Siempre con CRLF (`\r\n`), también antes y después del `.` final de DATA (el error 421 que le salió
  en clase). LIST y RETR devuelven varias líneas: leer hasta la línea `.` (función multilínea del aula). Pidió probar los casos de error,
  no solo el camino feliz: *"lo hicimos casi perfecto y no falló; si empiezan a hacer test van a ver problemas"*.
- Repositorio con nombre "elegante": `inf513-proyecto1`. Avisar en el chat del aula *"Ingeniero, grupo XX ya subió..."*.

---

## 6. Proyecto 2 (web), Laravel y prácticas U4

- **Fechas dichas en clase** [24, 26]: el P2 debe funcionar hacia el **15/11** para mostrarlo a la unidad (reunión de ~2 h; algunas
  unidades piden avances cada semana o cada 15 días). Luego hay 2 semanas de ajustes y la defensa con el docente en la última semana de
  noviembre (las clases terminan el 30/11). Recomienda hacer un cronograma y avanzar de a poco.
- **Menú dinámico desde la BD**, nunca estático; sale del diagrama general de CU (qué actor entra a qué CU) y distingue tipos de acceso
  (lectura, modificación, eliminación). Pidió investigar los modelos de control de acceso de las empresas: por módulo o rol, o con
  permisos cruzados entre áreas [40].
- **Archivos subidos con nombre legible** y relacionado con el dato (`juan_perez.jpg`), y ese nombre se guarda en la BD. Revisa la tabla
  de fotos del proyecto: nombres "en chino" = no hizo la práctica [40].
- **Plantillas**: todos los frameworks heredan de una plantilla base y se trabaja en el body; por eso la U4-1 (estructura de la página)
  es la base de todo [40].
- **Sesiones** del lado del servidor y `session_destroy()` al salir [37, 38].
- **Separar las 3 capas con librerías** [34, 35]: ADOdb separa el negocio de la BD (cambiar de motor = cambiar el driver, no el código) y
  Smarty separa el negocio de la vista (carpeta `templates/` con los `.tpl` y `templates_c/` donde se compilan; esta necesita permiso de
  escritura para Apache, en clase 777, *"igual que `storage` en Laravel"*). Lo presenta como el antecesor de los frameworks: Smarty →
  Blade (Laravel) o Twig (Symfony); ADOdb → Eloquent o Doctrine. *"Sobre esa base viene todo lo demás"* [36]. Para depurar, el modo
  debug de Smarty muestra las variables que recibe la plantilla.
- Las librerías que no están en los repositorios (JpGraph) se descargan con `wget`, se descomprimen con `tar -xzf` en
  `/usr/share/php/` y la ruta del `require` tiene que coincidir con esa carpeta [36, 37].
- La Agenda 3C [38, 39] es *"literalmente el segundo parcial"*: `env.php` con los datos de conexión, plantilla base Smarty con bloques,
  `pcXxx.php` = página cliente, `psXxx.php` = página servidor, `pslogin` guarda en sesión el nivel (grupo), el id y el nombre, y
  `pcmenu` arma el menú según el nivel. El módulo `personas.php?opcion=N` agrupa listar, nuevo, mostrar, editar, eliminar y la opción
  10, que procesa el formulario. Capturar errores como la llave duplicada y mostrar un mensaje.
- En el servidor, al clonar desde GitHub los archivos quedan con otro dueño y Apache no puede escribir (en Laravel, `storage`): hay que
  dar el grupo o dueño `apache` [29].
- **Prácticas U4** (individuales, en `practicaN/<Nombre>/` del directorio web del grupo) [34]: la U4-1 es **HTML puro sin editor**:
  CV con foto, **video y audio grabados por uno mismo**, estadística (gráfica; *"reporte es un listado, estadística es la representación
  porcentual"*) y una tabla. Se prueba en Windows y Linux con varios navegadores, y los problemas van en una **tabla con capturas** y su
  solución (si no hubo, se dice). La U4-2 es el mismo HTML con hoja de estilos.

---

## 7. Servidor en la nube: cómo lo configura él (U3) [17–33]

Principios que repite en cada servicio:
1. Instalación **mínima**, y después un servicio a la vez: así se sabe qué puerto abre cada uno.
2. Después de levantar cada servicio, **`nmap localhost` y `nmap <IP pública>`**; solo deben estar los puertos autorizados
   (22, 53, 25, 110, 5432, 80, 21, 9090). *"Cada puerta que abran es un riesgo"*.
3. **Ocultar el software y la versión** (Sendmail, Apache): el atacante busca exploits por versión.
4. Usuario administrativo además de root (root no entra a Cockpit); contraseñas de 8 o más caracteres con mayúsculas, minúsculas, dígitos
   y separadores.
5. `systemctl enable` + `start` + `status` en cada servicio.

| Servicio | Lo esencial |
|---|---|
| Fedora Server | ISO completa con test de medios; IP estática y ping antes de seguir; particiones swap, /boot (800 MB), / (10 GB), /home, /var y /opt, con **LVM** para las que crecen (/home, /var); Cockpit en `:9090` para monitorear CPU, RAM y disco (alerta al 80 %) |
| DNS (BIND) | `/var/named/<dominio>.zone` (SOA, NS, MX, A de dns/www/mail, ftp CNAME de www, TXT que exige Gmail) + zona inversa `x.y.z.in-addr.arpa`; `named.conf` con `listen-on` en la IP y `allow-query { any; }`; `named-checkconf`; probar con `nslookup <nombre> <IP>` |
| Correo | Usuarios del sistema en el grupo `mail`; `local-host-names`; `access` (RELAY/OK/REJECT) + `makemap`; `sendmail.mc` sin `Addr=127.0.0.1`, sin `accept_unresolvable_domains`, `MASQUERADE_AS`, listas negras `dnsbl`; Dovecot solo con `pop3` (sin imap ni lmtp), texto plano solo mientras se prueba |
| PostgreSQL | `--initdb`, `listen_addresses='*'`, `max_connections` razonable, `pg_hba.conf` con el admin solo desde una IP fija; un rol y una BD por grupo |
| Apache | `httpd php php-pgsql`; SELinux `httpd_can_sendmail`, `httpd_enable_homedirs`, `httpd_can_network_connect_db`; `ServerTokens Prod` + `ServerSignature Off`; `ServerAdmin` con el correo real; charset UTF-8; carpetas por `Alias` en `conf.d/` |
| FTP (vsftpd) | `ftpd_full_access`; chroot (usuario enjaulado en su carpeta); **límite de ancho de banda** (`local_max_rate`, `max_clients`, `max_per_ip`) para que no se coma a los demás servicios |
| Webmail | Roundcube con su propia BD en PostgreSQL, IMAP 143 + SMTP 25, Alias publicado |

Extras que mencionó: el dimensionamiento (gama baja, media o alta; CPU y RAM por debajo del 80 %; disco = crecimiento diario × 365 × 5
años + 20 %) y las cuotas de ~5 GB por usuario [13–16, 33]. *"La configuración de un servidor no se regala: unos 100 $us más 6 meses de
mantenimiento"* [33].

---

## 8. Teoría que suele preguntar (U1–U2)

Quién creó la web (Tim Berners-Lee, CERN) y su evolución (HTML → JS → applets → DHTML → Flash → PHP/ASP/JSP, XML → JSON) [03] ·
HTTP 1.0 frente a 1.1 [01] · TCP frente a UDP y cuándo se usa cada uno [02] · cliente-servidor y 3 capas [02] · los factores de autenticación
(algo que tengo, algo que sé, algo que soy) [02] · firewall y antivirus en cada equipo, no solo en el perímetro [02, 03] · cómo diagnosticar
una página que no carga (red → DNS → servidor) [01] · por qué el correo es asíncrono [22] · por qué Java es más seguro que un .exe
(bytecode + JVM) [03] · por qué Apache devuelve el PHP como texto (falta el intérprete) [03] · IP, máscara, gateway y DNS
(*"no se pueden olvidar"*) [03].

---

## 9. Qué implica para nuestras entregas ahora

Para el **P1** (cierra el 14/10, 15:00), lo que se puede verificar o reforzar sin rehacer nada:
- [ ] **Pantallas del P1 = comandos y respuestas**: que el documento muestre el correo que se envía y el que vuelve (éxito y error) por
      CU. Hoy `p1/doc/documento_p1.py` no tiene una sección de pantallas; las capturas de Gmail están como `[PENDIENTE]` en Resultados.
- [ ] **Organigrama** de la unidad: sigue `[PENDIENTE]` y él lo revisa (de ahí salen los actores).
- [ ] **Mensajes de error que nombren el parámetro concreto** (falta, sobra, tipo, formato) y no solo "comando inválido". Probarlo en la
      defensa.
- [ ] **Vigencia de credenciales**: `usuario` tiene `rol` y `estado`, pero no `fecha_inicio`/`fecha_fin`. Es la pregunta que dijo que
      hace (*"¿hasta cuándo dura esta credencial?"*). Si no se agrega, conviene tener la respuesta preparada.
- [ ] Los tres en la carátula; los tres saben explicar el código (cada uno debe poder hacer el desafío en el teclado).
- [ ] Ensayar un desafío en vivo: cambiar el texto de una respuesta o agregar un parámetro a un comando, a mano y en menos de 5 minutos.

Para el **P2** y la U4:
- Menú dinámico desde la BD con la matriz de acceso; archivos subidos con nombres legibles; CSS en archivos aparte; vigencia de
  credenciales en el modelo; pantalla por cada página del diagrama de navegación; mostrar el prototipo a la unidad hacia el 15/11.
- Diagrama de navegación con los estereotipos de la §3 y con atributos y operaciones en todas las clases.

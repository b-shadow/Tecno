"""Único lugar con rutas del generador. Todo es relativo a esta carpeta (crm-web/generadorDocumento)."""
import pathlib

AQUI = pathlib.Path(__file__).resolve().parent
CRM_WEB = AQUI.parent                                     # crm-web: el sistema documentado (este mismo repo)
ESQUEMA = AQUI / 'fuentes' / 'esquema.sql'                # pg_dump --schema-only de db_grupo05sa.public
LOGO = AQUI / 'recursos' / 'logo_ficct.png'
DIAGRAMAS = AQUI / 'diagramas'
DOCUMENTO = AQUI / 'documento' / 'P2-INF513-GRUPO05SA.docx'   # cada corrida reemplaza este .docx (y exportar.ps1 su .doc/.pdf)

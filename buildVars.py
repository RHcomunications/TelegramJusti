# -*- coding: UTF-8 -*-

# Build customizations
# Change this file instead of sconstruct or manifest files whenever possible.

from site_scons.site_tools.NVDATool.typings import (
	AddonInfo,
	BrailleTables,
	SymbolDictionaries,
)

from site_scons.site_tools.NVDATool.utils import _


# Add-on information
addon_info = AddonInfo(

	# Internal add-on identifier
	addon_name="TelegramJusti",

	addon_summary=_(
    "TelegramJusti complemento híbrido de accesibilidad compatible con Unigram Preview (12.10.3.0 - 12.10.4.0) y Telegram Desktop"
),

	# Add-on description
	addon_description=_(
    """TelegramJusti es un complemento híbrido de accesibilidad compatible con Telegram Desktop y Unigram Preview (12.10.3.0 y 12.10.4.0 AMD64).

Proporciona atajos de teclado, automatización accesible y navegación optimizada para usuarios de NVDA.

Incluye funciones para mensajes de voz, llamadas, videollamadas, navegación rápida entre chats, acceso a perfiles y adjuntos multimedia.

Compatible con Unigram Preview 12.10.3.0 y 12.10.4.0 AMD64.
Los gestos son personalizables desde Gestos de Entrada de NVDA."""
),

	# Version
	addon_version="1.3.1",

 # Changelog
addon_changelog=_(
    """Versión 1.3.1

  Novedades:

  * Compatibilidad con Unigram Preview 12.10.4.0 AMD64.
  * Enrutamiento híbrido automático: selección transparente entre Unigram Preview (UWP) y Telegram Desktop (Qt).
  * Corrección de importaciones y variables críticas para compatibilidad con NVDA 2026.2.
  * Reestructuración canónica de plugins globales (TelegramJusti) y tareas de instalación según los estándares de NVDA.

Versión 1.3.0

  Novedades:

  * Compatibilidad con Unigram Preview 12.10.3.0.
  * Actualización de AutomationIDs: se añadieron IDs alternativos para cada control.
  * `ComposerHeaderCancel` como fallback para cancelación de grabación.
  * `RecognizedText` como fallback para detección de mensajes de voz.
  * Búsqueda multi-IDs para todos los botones principales.
  * Se añadieron nombres alternativos para botón finalizar (End, Leave).
  * Se añadieron nombres alternativos para reproducción (Play, Pause).
  * Nuevo script de diagnóstico Ctrl+Shift+D para registrar jerarquía de elementos.
  * Mejora en la detección de perfil y navegación mediante listas de IDs compatibles.
  * Se mejoró la robustez de todas las búsquedas de UI Automation.
  * Migración progresiva a UI Automation y AutomationID.
  * Mejorada significativamente la compatibilidad multilenguaje.

  Nuevas funcionalidades (compatibilidad con Unigram Plus):

  * Editar mensaje (Retroceso), responder (Enter), reenviar (Alt+F).
  * Eliminar mensaje/chat (Alt+Delete / Shift+Delete).
  * Marcar chat como leído (Alt+Shift+R), seleccionar (Ctrl+Space), fijar.
  * Navegación rápida por chat: Alt+1 a Alt+6 (lista, último mensaje, no leídos, carpetas, perfil, hilos).
  * Velocidad de reproducción de voz (Alt+S), cerrar reproductor (Alt+E).
  * Convertir voz a texto (NVDA+Alt+R).
  * Mostrar texto en ventana emergente (Alt+C), abrir comentarios (Ctrl+Alt+C).
  * Copiar mensaje (Ctrl+C).
  * Rebobinar/reavanzar voz (Ctrl+Alt+←/→).
  * Navegación por búsqueda (Alt+I, F3, Shift+F3).
  * Controles de llamada: responder (Alt+Y), rechazar/terminar (Alt+N), micrófono (Alt+A), cámara (Alt+V).
  * Configuración persistente con diálogo de ajustes NVDA (NVDA+Alt+U).
  * Menú contextual con opciones de edición, reenvío y eliminación.
  * Soporte de 17 idiomas con localización completa.
  * Efectos de sonido para grabación y notificaciones.
  * TextWindow para mostrar texto formateado.
  * GlobalPlugin con configuración integrada.
  """
),

	# Author
	addon_author="Mauro Ocampo JustiCode <drmauroocampo271@gmail.com>",

	# Documentation URL
	addon_url="https://github.com/JustiCode/TelegramJusti",
addon_sourceURL="https://github.com/JustiCode/TelegramJusti",

	# Documentation filename
	addon_docFileName="readme.html",

	# NVDA compatibility
	addon_minimumNVDAVersion="2026.1",
	addon_lastTestedNVDAVersion="2026.2",

	# Update channel
	addon_updateChannel=None,

	# License
	addon_license="GPL v2",
	addon_licenseURL="https://www.gnu.org/licenses/gpl-2.0.html",
)

# Python source files
pythonSources = [
	"addon/appModules/telegram.py",
	"addon/appModules/unigram.py",
	"addon/appModules/cnf.py",
	"addon/appModules/data.py",
	"addon/appModules/text_window.py",
	"addon/globalPlugins/TelegramJusti/__init__.py",
	"addon/installTasks.py",
]

# Translation sources
i18nSources = pythonSources + [
	"buildVars.py",
]

# Excluded files
excludedFiles = [
	"**/__pycache__/",
	"**/*.pyc",
]

# Base language
baseLanguage = "es"

# Markdown extensions
markdownExtensions = [
	"markdown.extensions.tables",
]

# Braille tables
brailleTables: BrailleTables = {}

# Symbol dictionaries
symbolDictionaries: SymbolDictionaries = {}		

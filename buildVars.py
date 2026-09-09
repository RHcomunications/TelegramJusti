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
    "TelegramJusti_1.3.0 complemento híbrido de accesibilidad compatible con Unigram Preview 12.10.3.0 y Telegram Desktop"
),

	# Add-on description
	addon_description=_(
    """TelegramJusti es un complemento híbrido de accesibilidad compatible con Telegram Desktop y Unigram Preview 12.10.3.0.

Proporciona atajos de teclado, automatización accesible y navegación optimizada para usuarios de NVDA.

Incluye funciones para mensajes de voz, llamadas, videollamadas, navegación rápida entre chats, acceso a perfiles y adjuntos multimedia.

Compatible con Unigram Preview 12.10.3.0 AMD64.
Los gestos son personalizables desde Gestos de Entrada de NVDA."""
),

	# Version
	addon_version="1.3.0",

 # Changelog
    addon_changelog=_(
    """Versión 1.3.0

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
 * Se añadió import de controlTypes para extensibilidad futura.
 * Se mejoró la robustez de todas las búsquedas de UI Automation.
 * Migración progresiva a UI Automation y AutomationID.
 * Mejorada significativamente la compatibilidad multilenguaje.
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
addon_lastTestedNVDAVersion="2026.1.1",

	# Update channel
	addon_updateChannel=None,

	# License
	addon_license="GPL v2",
	addon_licenseURL="https://www.gnu.org/licenses/gpl-2.0.html",
)

# Python source files
pythonSources = [
	"addon/appModules/unigram.py",
]

# Translation sources
i18nSources = pythonSources + [
	"buildVars.py",
]

# Excluded files
excludedFiles = []

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

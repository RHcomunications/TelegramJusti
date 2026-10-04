# -*- coding: utf-8 -*-
"""
Telegram Justi - Módulo para Telegram Desktop
Compatible con Telegram Desktop (Qt / Win32).

Autor: Mauro Ocampo - JustiCode
"""

import time
import api
import tones
import ui
import appModuleHandler
import keyboardHandler
import logHandler
import scriptHandler
from controlTypes import Role, State
from addonHandler import initTranslation

initTranslation()
log = logHandler.log


def is_unigram_process(processID):
	"""Determina si el proceso actual corresponde a Unigram Preview."""
	try:
		import winKernel
		path = winKernel.getProcessFilename(processID)
		if path and "unigram" in path.lower():
			return True
	except Exception:
		pass

	try:
		import ctypes
		from ctypes import wintypes
		kernel32 = ctypes.windll.kernel32
		hProcess = kernel32.OpenProcess(0x1000, False, processID)
		if hProcess:
			buf = ctypes.create_unicode_buffer(1024)
			size = wintypes.DWORD(1024)
			res = kernel32.QueryFullProcessImageNameW(hProcess, 0, buf, ctypes.byref(size))
			kernel32.CloseHandle(hProcess)
			if res and "unigram" in buf.value.lower():
				return True
	except Exception:
		pass
	return False


class TelegramDesktopAppModule(appModuleHandler.AppModule):
	"""AppModule dedicado para Telegram Desktop."""

	scriptCategory = "Telegram Justi"
	lastAudioGesture = 0

	# =========================================================
	# Utilidades internas
	# =========================================================

	def sendKey(self, keyName):
		"""Envía una combinación de teclas con delay seguro."""
		try:
			gesture = keyboardHandler.KeyboardInputGesture.fromName(keyName)
			gesture.send()
			time.sleep(0.08)
		except Exception:
			log.exception("Error enviando tecla: %s", keyName)

	def findObjectByName(self, obj, target):
		"""Busca recursivamente un objeto por coincidencia de nombre."""
		if not obj:
			return None
		try:
			name = getattr(obj, "name", "") or ""
			if target.lower() in name.lower():
				return obj
		except Exception:
			pass

		try:
			child = getattr(obj, "firstChild", None)
			while child:
				result = self.findObjectByName(child, target)
				if result:
					return result
				child = getattr(child, "next", None)
		except Exception:
			pass
		return None

	def activateObject(self, obj):
		"""Activa un objeto accesible intentando doAction o espacio."""
		if not obj:
			return False
		try:
			obj.doAction()
			return True
		except Exception:
			pass
		try:
			obj.setFocus()
			time.sleep(0.1)
			self.sendKey("space")
			return True
		except Exception:
			pass
		return False

	def activateNamedControl(self, targetNames, successMessage=None, errorMessage=None, beepFrequency=1000):
		"""Busca y activa un control por una o más opciones de nombre."""
		if isinstance(targetNames, str):
			targetNames = [targetNames]

		fg = api.getForegroundObject()
		control = None
		for name in targetNames:
			control = self.findObjectByName(fg, name)
			if control:
				break

		if not control:
			if errorMessage:
				ui.message(errorMessage)
			return False

		if self.activateObject(control):
			if beepFrequency:
				tones.beep(beepFrequency, 80)
			if successMessage:
				ui.message(successMessage)
			return True
		elif errorMessage:
			ui.message(errorMessage)
		return False

	# =========================================================
	# Scripts de navegación y acciones
	# =========================================================

	@scriptHandler.script(
		description=_("Enfocar cuadro de mensaje"),
		category="Telegram Justi",
		gesture="kb:alt+e"
	)
	def script_focusMessageEdit(self, gesture):
		"""Enfoca el cuadro de edición de mensaje en Telegram Desktop."""
		fg = api.getForegroundObject()
		edit = None
		for label in ("Mensaje", "Write a message...", "Escribe un mensaje", "Message"):
			edit = self.findObjectByName(fg, label)
			if edit and getattr(edit, "role", None) in (Role.EDITABLETEXT, Role.TEXTFRAME):
				break

		if not edit:
			try:
				def findEdit(obj):
					if getattr(obj, "role", None) in (Role.EDITABLETEXT, Role.TEXTFRAME):
						return obj
					child = getattr(obj, "firstChild", None)
					while child:
						res = findEdit(child)
						if res:
							return res
						child = getattr(child, "next", None)
					return None
				edit = findEdit(fg)
			except Exception:
				edit = None

		if edit:
			try:
				edit.setFocus()
				tones.beep(900, 80)
				ui.message(_("Cuadro de mensaje"))
				return
			except Exception:
				pass

		self.sendKey("escape")
		ui.message(_("Cuadro de mensaje no encontrado"))

	@scriptHandler.script(
		description=_("Reproducir o pausar mensaje de voz"),
		category="Telegram Justi",
		gesture="kb:space"
	)
	def script_playPauseAudio(self, gesture):
		"""Reproduce o pausa notas de voz; si no es audio, envía espacio normalmente."""
		focus = api.getFocusObject()
		if focus and getattr(focus, "role", None) in (Role.EDITABLETEXT, Role.TEXTFRAME):
			gesture.send()
			return

		if focus and getattr(focus, "name", None):
			text = focus.name.lower()
			if any(k in text for k in ("mensaje de voz", "voice message", "audio", "segundos", "seconds")):
				try:
					focus.doAction()
					tones.beep(900, 50)
					return
				except Exception:
					pass

				playButton = None
				for btn_name in ("Reproducir", "Play", "Pausar", "Pause"):
					playButton = self.findObjectByName(focus, btn_name)
					if playButton:
						break

				if playButton and self.activateObject(playButton):
					tones.beep(900, 50)
					return

		gesture.send()

	@scriptHandler.script(
		description=_("Grabar o enviar mensaje de voz"),
		category="Telegram Justi",
		gesture="kb:control+r"
	)
	def script_voiceMessage(self, gesture):
		"""Graba o envía mensaje de voz."""
		currentTime = time.time()
		try:
			if currentTime - self.lastAudioGesture < 0.6:
				self.sendKey("control+enter")
				tones.beep(1200, 100)
				ui.message(_("Audio enviado"))
			else:
				gesture.send()
				tones.beep(700, 100)
				ui.message(_("Grabando mensaje de voz"))
			self.lastAudioGesture = currentTime
		except Exception:
			log.exception("Error gestionando audio en Telegram Desktop")
			gesture.send()

	@scriptHandler.script(
		description=_("Abrir perfil del chat actual"),
		category="Telegram Justi",
		gesture="kb:control+p"
	)
	def script_openProfile(self, gesture):
		self.activateNamedControl(
			["últ. vez", "last seen", "en línea", "online", "miembros", "members", "suscriptores"],
			successMessage=_("Perfil abierto"),
			errorMessage=_("Perfil no encontrado"),
			beepFrequency=900
		)

	@scriptHandler.script(
		description=_("Iniciar llamada de voz"),
		category="Telegram Justi",
		gesture="kb:control+shift+l"
	)
	def script_voiceCall(self, gesture):
		self.activateNamedControl(
			["Llamar", "Call"],
			successMessage=_("Llamando"),
			errorMessage=_("Botón llamar no encontrado"),
			beepFrequency=1000
		)

	@scriptHandler.script(
		description=_("Iniciar videollamada"),
		category="Telegram Justi",
		gesture="kb:control+shift+v"
	)
	def script_videoCall(self, gesture):
		self.activateNamedControl(
			["Videollamar", "Video call"],
			successMessage=_("Videollamada"),
			errorMessage=_("Botón videollamada no encontrado"),
			beepFrequency=1200
		)

	@scriptHandler.script(
		description=_("Finalizar llamada"),
		category="Telegram Justi",
		gesture="kb:control+shift+n"
	)
	def script_endCall(self, gesture):
		self.activateNamedControl(
			["Finalizar", "End call", "Leave", "Colgar"],
			successMessage=_("Llamada finalizada"),
			errorMessage=_("Botón finalizar no encontrado"),
			beepFrequency=500
		)

	@scriptHandler.script(
		description=_("Adjuntar multimedia"),
		category="Telegram Justi",
		gesture="kb:control+shift+a"
	)
	def script_attachMedia(self, gesture):
		self.activateNamedControl(
			["Adjuntar", "Attach", "Adjuntar archivo"],
			successMessage=_("Adjuntar multimedia"),
			errorMessage=_("Botón adjuntar no encontrado"),
			beepFrequency=700
		)

	@scriptHandler.script(
		description=_("Abrir nuevo chat"),
		category="Telegram Justi",
		gesture="kb:control+n"
	)
	def script_newChat(self, gesture):
		self.activateNamedControl(
			["Nuevo chat", "New chat", "Nuevo mensaje"],
			successMessage=_("Nuevo chat"),
			errorMessage=_("Botón nuevo chat no encontrado"),
			beepFrequency=700
		)

	# =========================================================
	# Gestos asociados
	# =========================================================

	__gestures = {
		"kb:space": "playPauseAudio",
		"kb:control+r": "voiceMessage",
		"kb:alt+e": "focusMessageEdit",
		"kb:control+p": "openProfile",
		"kb:control+shift+l": "voiceCall",
		"kb:control+shift+v": "videoCall",
		"kb:control+shift+n": "endCall",
		"kb:control+shift+a": "attachMedia",
		"kb:control+n": "newChat",
	}


class AppModule(appModuleHandler.AppModule):
	"""AppModule híbrido con selección automática entre Unigram y Telegram Desktop."""

	def __new__(cls, processID, appModuleName=None):
		if is_unigram_process(processID):
			try:
				from .unigram import AppModule as UnigramAppModule
				return UnigramAppModule(processID, appModuleName)
			except Exception:
				log.exception("Error instanciando Unigram AppModule desde telegram.py")
		return TelegramDesktopAppModule(processID, appModuleName)
# -*- coding: utf-8 -*-

"""
Telegram Justi 1.2.0
Complemento NVDA para Telegram Unigram Preview 12.10.3.0.

Autor:
Mauro Ocampo - JustiCode
"""

import time

import api
import tones
import ui
import wx
import appModuleHandler
import keyboardHandler
import logHandler
import scriptHandler
from addonHandler import initTranslation

initTranslation()

log = logHandler.log


class AppModule(appModuleHandler.AppModule):
    """AppModule principal para Telegram Unigram Preview 12.10.3.0."""

    lastAudioGesture = 0

    # =========================================================
    # AutomationIDs compatibles con Unigram Preview 12.10.3.0
    # =========================================================

    CANCEL_RECORDING_IDS = (
        "ComposerHeaderCancel",
        "ButtonCancelRecording",
        "btnVoiceMessage",
    )

    VOICE_MESSAGE_IDS = (
        "Recognize",
        "RecognizedText",
        "Subtitle",
    )

    PROFILE_IDS = (
        "Profile",
    )

    CALL_IDS = (
        "Call",
    )

    VIDEO_CALL_IDS = (
        "VideoCall",
    )

    ATTACH_IDS = (
        "ButtonAttach",
    )

    COMPOSE_IDS = (
        "ComposeButton",
    )

    TEXT_FIELD_IDS = (
        "TextField",
    )

    NAVIGATION_IDS = (
        "Photo",
    )

    BACK_IDS = (
        "BackButton",
    )

    END_CALL_NAMES = (
        "finalizar",
        "End",
        "Leave",
    )

    PLAY_NAMES = (
        "Reproducir",
        "Play",
    )

    PAUSE_NAMES = (
        "Pausar",
        "Pause",
    )

    # =========================================================
    # Utilidades internas
    # =========================================================

    def sendKey(self, keyName):
        """Envía una combinación de teclas."""

        try:
            gesture = keyboardHandler.KeyboardInputGesture.fromName(
                keyName
            )

            gesture.send()

            time.sleep(0.08)

        except Exception:
            log.exception(
                "Error enviando tecla: %s",
                keyName
            )

    def findObjectByName(self, obj, target):
        """Busca recursivamente un objeto por coincidencia parcial de nombre."""

        if not obj:
            return None

        try:
            name = obj.name or ""

            if target.lower() in name.lower():
                return obj

        except Exception:
            pass

        try:
            child = obj.firstChild

            while child:

                result = self.findObjectByName(
                    child,
                    target
                )

                if result:
                    return result

                child = child.next

        except Exception:
            pass

        return None

    def findObjectByAutomationID(self, obj, targetID):
        """Busca un objeto por AutomationID."""

        if not obj:
            return None

        try:
            automationID = getattr(
                obj,
                "UIAAutomationId",
                ""
            ) or ""

            if automationID == targetID:
                return obj

        except Exception:
            pass

        try:
            child = obj.firstChild

            while child:

                result = self.findObjectByAutomationID(
                    child,
                    targetID
                )

                if result:
                    return result

                child = child.next

        except Exception:
            pass

        return None

    def findObjectByAutomationIDs(self, obj, targetIDs):
        """Busca un objeto por cualquiera de varias AutomationIDs."""

        if not obj or not targetIDs:
            return None

        for targetID in targetIDs:
            result = self.findObjectByAutomationID(obj, targetID)
            if result:
                return result

        return None

    def findObjectByNameInList(self, obj, names):
        """Busca un objeto por cualquiera de varios nombres."""

        if not obj or not names:
            return None

        for name in names:
            result = self.findObjectByName(obj, name)
            if result:
                return result

        return None

    def activateObject(self, obj):
        """
        Activa un objeto accesible.

        Primero intenta doAction().
        Si falla, enfoca y pulsa espacio.
        """

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

    def activateNamedControl(
        self,
        targetName,
        successMessage=None,
        errorMessage=None,
        beepFrequency=1000
    ):
        """Busca y activa un control por nombre."""

        fg = api.getForegroundObject()

        try:
            control = self.findObjectByName(
                fg,
                targetName
            )

            if not control:

                if errorMessage:
                    ui.message(errorMessage)

                return False

            self.activateObject(control)

            tones.beep(beepFrequency, 100)

            if successMessage:
                ui.message(successMessage)

            return True

        except Exception:
            log.exception(
                "Error activando control: %s",
                targetName
            )

            if errorMessage:
                ui.message(errorMessage)

        return False

    def debugDumpElements(self, obj, depth=0):
        """
        Imprime en el log la jerarquía de elementos accesibles.
        Útil para descubrir nuevos AutomationIDs en actualizaciones de Unigram.
        """

        indent = "  " * depth

        try:
            automationID = getattr(obj, "UIAAutomationId", "") or ""
            name = obj.name or ""
            role = obj.role
            log.debug(
                "%s%s | AutomationID: %s | Role: %s | Name: %s",
                indent,
                type(obj).__name__,
                automationID,
                role,
                name
            )
        except Exception:
            pass

        try:
            child = obj.firstChild
            while child:
                self.debugDumpElements(child, depth + 1)
                child = child.next
        except Exception:
            pass

    # =========================================================
    # Eventos
    # =========================================================

    def event_gainFocus(self, obj, nextHandler):
        """Enfoca automáticamente la lista de chats al iniciar Unigram."""

        try:
            automationID = getattr(obj, "UIAAutomationId", "") or ""

            if automationID in self.NAVIGATION_IDS:

                def focusChats():
                    self.sendKey("tab")
                    time.sleep(0.1)

                    self.sendKey("tab")
                    time.sleep(0.1)

                    self.sendKey("tab")

                wx.CallLater(600, focusChats)

        except Exception:
            log.exception("Error enfocando lista de chats")

        nextHandler()

    # =========================================================
    # Scripts
    # =========================================================

    @scriptHandler.script(
        description=_("Grabar o enviar mensaje de voz"),
        category=_("Telegram Justi"),
        gesture="kb:control+r"
    )
    def script_voiceMessage(self, gesture):
        """Graba o envía mensajes de voz."""
        currentTime = time.time()

        try:
            if (
                currentTime - self.lastAudioGesture < 0.5
            ):
                self.sendKey("control+enter")
                tones.beep(1200, 100)
            else:
                self.sendKey("control+r")
                tones.beep(700, 100)

            self.lastAudioGesture = currentTime

        except Exception:
            log.exception("Error gestionando audio")

    @scriptHandler.script(
        description=_("Cancelar grabación de mensaje de voz"),
        category=_("Telegram Justi"),
        gesture="kb:control+shift+r"
    )
    def script_cancelVoiceMessage(self, gesture):
        """Cancela la grabación de un mensaje de voz."""

        fg = api.getForegroundObject()

        button = self.findObjectByAutomationIDs(
            fg,
            self.CANCEL_RECORDING_IDS
        )

        if not button:
            tones.beep(200, 50)
            ui.message(_("No se encontró botón de cancelación"))
            return

        try:
            button.doAction()
            tones.beep(500, 80)
            ui.message(_("Grabación cancelada"))

        except Exception:
            ui.message("No se pudo cancelar la grabación")

    @scriptHandler.script(
        description=_("Reproducir o pausar mensaje de voz"),
        category=_("Telegram Justi"),
        gesture="kb:space"
    )
    def script_playPauseAudio(self, gesture):
        """Reproduce o pausa mensajes de voz."""

        try:
            focus = api.getFocusObject()

            if not focus:
                gesture.send()
                return

            audioMessage = self.findObjectByAutomationIDs(
                focus,
                self.VOICE_MESSAGE_IDS
            )

            if audioMessage:
                try:
                    focus.doAction()
                    tones.beep(900, 50)
                    return
                except Exception:
                    pass

                playButton = self.findObjectByNameInList(
                    focus,
                    self.PLAY_NAMES
                )

                if not playButton:
                    playButton = self.findObjectByNameInList(
                        focus,
                        self.PAUSE_NAMES
                    )

                if playButton:
                    self.activateObject(playButton)
                    tones.beep(900, 50)
                    return

        except Exception:
            log.exception("Error reproduciendo audio")

        gesture.send()

    @scriptHandler.script(
        description=_("Abrir perfil del chat actual"),
        category=_("Telegram Justi"),
        gesture="kb:control+p"
    )
    def script_openProfile(self, gesture):
        """Abre el perfil del chat actual."""

        fg = api.getForegroundObject()

        button = self.findObjectByAutomationIDs(
            fg,
            self.PROFILE_IDS
        )

        if not button:
            ui.message(_("Perfil no encontrado"))
            return

        try:
            button.doAction()
            tones.beep(900, 80)

        except Exception:
            ui.message("No se pudo abrir el perfil")

    @scriptHandler.script(
        description=_("Inicia una llamada de voz"),
        category=_("Telegram Justi"),
        gesture="kb:control+shift+l"
    )
    def script_voiceCall(self, gesture):
        """Inicia una llamada de voz."""

        fg = api.getForegroundObject()

        button = self.findObjectByAutomationIDs(
            fg,
            self.CALL_IDS
        )

        if not button:
            ui.message(_("Llamar no encontrado"))
            return

        try:
            button.doAction()
            tones.beep(1000, 80)

        except Exception:
            ui.message("No se pudo iniciar la llamada")

    @scriptHandler.script(
        description=_("Iniciar videollamada"),
        category=_("Telegram Justi"),
        gesture="kb:control+shift+v"
    )
    def script_videoCall(self, gesture):
        """Inicia una videollamada."""

        fg = api.getForegroundObject()

        button = self.findObjectByAutomationIDs(
            fg,
            self.VIDEO_CALL_IDS
        )

        if not button:
            ui.message(_("Videollamada no encontrada"))
            return

        try:
            button.doAction()
            tones.beep(1200, 100)

        except Exception:
            ui.message("Error en videollamada")

    @scriptHandler.script(
        description=_("Finalizar llamada"),
        category=_("Telegram Justi"),
        gesture="kb:control+shift+n"
    )
    def script_endCall(self, gesture):
        """Finaliza una llamada."""

        fg = api.getForegroundObject()

        button = self.findObjectByNameInList(
            fg,
            self.END_CALL_NAMES
        )

        if not button:
            button = self.findObjectByAutomationIDs(
                fg,
                self.END_CALL_NAMES
            )

        if not button:
            ui.message(_("Botón finalizar no encontrado"))
            return

        try:
            button.doAction()
            tones.beep(500, 80)

        except Exception:
            ui.message("Error al finalizar llamada")

    @scriptHandler.script(
        description=_("Adjuntar multimedia"),
        category=_("Telegram Justi"),
        gesture="kb:control+shift+a"
    )
    def script_attachMedia(self, gesture):
        """Adjunta archivos multimedia."""

        fg = api.getForegroundObject()

        button = self.findObjectByAutomationIDs(
            fg,
            self.ATTACH_IDS
        )

        if not button:
            ui.message(_("Botón adjuntar no encontrado"))
            return

        try:
            button.doAction()
            tones.beep(700, 80)

        except Exception:
            ui.message("Error al adjuntar")

    @scriptHandler.script(
        description=_("Abrir nuevo chat"),
        category=_("Telegram Justi"),
        gesture="kb:control+n"
    )
    def script_newChat(self, gesture):
        """Abre la ventana nuevo chat."""

        fg = api.getForegroundObject()

        button = self.findObjectByAutomationIDs(
            fg,
            self.COMPOSE_IDS
        )

        if not button:
            ui.message(_("Botón nuevo chat no encontrado"))
            return

        try:
            button.doAction()
            tones.beep(700, 80)

        except Exception:
            ui.message("No se pudo abrir nuevo chat")

    @scriptHandler.script(
        description=_("Ir al cuadro de mensaje"),
        category=_("Telegram Justi"),
        gesture="kb:alt+e"
    )
    def script_focusMessageEdit(self, gesture):
        """Enfoca el cuadro de mensaje."""

        fg = api.getForegroundObject()

        edit = self.findObjectByAutomationIDs(
            fg,
            self.TEXT_FIELD_IDS
        )

        if not edit:
            ui.message(_("Cuadro de mensaje no encontrado"))
            return

        try:
            edit.setFocus()
            tones.beep(700, 80)

        except Exception:
            ui.message("No se pudo enfocar el cuadro de mensaje")

    @scriptHandler.script(
        description=_("Abrir menú de navegación"),
        category=_("Telegram Justi"),
        gesture="kb:control+shift+m"
    )
    def script_openNavigationMenu(self, gesture):
        """Abre el menú de navegación."""

        fg = api.getForegroundObject()

        button = self.findObjectByAutomationIDs(
            fg,
            self.NAVIGATION_IDS
        )

        if not button:
            ui.message(_("Menú no encontrado"))
            return

        try:
            button.doAction()
            tones.beep(700, 80)

        except Exception:
            ui.message("No se pudo abrir el menú")

    @scriptHandler.script(
        description=_("Volver directamente a la lista de chats"),
        category=_("Telegram Justi"),
        gesture="kb:alt+leftArrow"
    )
    def script_backToChats(self, gesture):
        """Regresa directamente a la lista de chats."""

        fg = api.getForegroundObject()

        button = self.findObjectByAutomationIDs(
            fg,
            self.BACK_IDS
        )

        if not button:
            ui.message(_("Botón volver atrás no encontrado"))
            return

        try:
            button.doAction()
            tones.beep(800, 80)

        except Exception:
            ui.message(_("No se pudo volver a la lista de chats"))

    # =========================================================
    # Utilidad de diagnóstico
    # =========================================================

    @scriptHandler.script(
        description=_("Registra la jerarquía de elementos en el log (solo desarrollo)"),
        category=_("Telegram Justi"),
        gesture="kb:control+shift+d"
    )
    def script_debugDumpElements(self, gesture):
        """Registra la jerarquía de elementos accesibles para debugging."""

        fg = api.getForegroundObject()
        log.debug("=== Jerarquía de elementos Unigram ===")
        self.debugDumpElements(fg)
        log.debug("=== Fin de la jerarquía ===")
        ui.message(_("Jerarquía registrada en el log"))

    # =========================================================
    # Gestos
    # =========================================================

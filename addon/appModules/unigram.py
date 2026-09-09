# -*- coding: utf-8 -*-
"""
Telegram Justi 1.3.0
Complemento NVDA para Telegram Unigram Preview 12.10.3.0.
Compatible con Unigram Plus features.

Autor: Mauro Ocampo - JustiCode
"""

import time
import os
import re
import queueHandler
import speech
import api
import tones
import ui
import winUser
import mouseHandler
import keyboardHandler
import logHandler
import scriptHandler
import addonHandler
import editableText
import textInfos
from addonHandler import initTranslation
from nvwave import playWaveFile
from threading import Timer
from controlTypes import Role, State
import languageHandler
from NVDAObjects.UIA import UIA, ListItem

initTranslation()

from .cnf import conf, lang
from .data import icons_from_context_menu, labels_for_buttons, labels_in_buttons, phrase_administrator_in_message, keywordsInMessages
from .text_window import TextWindow

baseDir = os.path.join(os.path.dirname(__file__), "media\\")


class Message_list_item(ListItem):
	selected_media = -1
	list_media = []
	UIAAutomationId = "Message_item"
	last_part_in_message = None
	index_last_part_in_message = 0

	@scriptHandler.script(description=_("Announce the original message"), gesture="kb:leftArrow")
	def script_voice_answer(self, gesture):
		if self.selected_media > 0:
			self.script_next_media(gesture, True)
			return
		answer = next((item for item in self.children if item.UIAAutomationId == "Reply"), None)
		if answer and answer.name == "": answer = answer.firstChild
		if scriptHandler.getLastScriptRepeatCount() == 0 and answer: ui.message(answer.name)
		elif scriptHandler.getLastScriptRepeatCount() == 1 and answer: answer.doAction()

	@scriptHandler.script(description=_("Show message text in popup"), gesture="kb:alt+c")
	def script_show_text_message(self, gesture):
		text_message = next((item.name for item in self.children if item.UIAAutomationId in ("TextBlock", "Message", "Question")), "")
		recognized_text = next((item.name for item in self.children if item.UIAAutomationId == "RecognizedText"), "")
		if not text_message and not recognized_text:
			ui.message(_("This message does not contain text")); return
		text_message = text_message.strip().replace("‍", "")
		recognized_text = recognized_text.strip().replace("‍", "")
		text = "\n\n".join([text_message, recognized_text]) if text_message and recognized_text else (text_message or recognized_text)
		TextWindow(text, _("message text"), readOnly=False)

	@scriptHandler.script(description=_("Open comments"), gesture="kb:control+alt+c")
	def script_openComentars(self, gesture):
		targetButton = next((item for item in reversed(self.children) if item.role == Role.LINK and item.UIAAutomationId == "Thread"), False)
		if targetButton: targetButton.doAction()
		else: ui.message(_("Button to open comments not found"))

	@scriptHandler.script(description=_("Edit message"), gesture="kb:backspace")
	def script_edit_message(self, gesture):
		self.activate_option_for_menu((icons_from_context_menu["edit"]), "Messages")

	@scriptHandler.script(description=_("Reply to message"), gesture="kb:enter")
	def script_reply_to_message(self, gesture):
		self.activate_option_for_menu((icons_from_context_menu["reply"]), "Messages")

	def script_next_message(self, gesture):
		if self.parent.next: gesture.send()
		else: self.script_moveFocusToTextMessage(gesture)

	def script_next_media(self, gesture, revers=False):
		self.list_media = self.list_media or [item for item in self.children if item.role == Role.LISTITEM]
		obj = None
		if revers:
			self.selected_media -= 1
			obj = self.list_media[self.selected_media]
		elif self.selected_media < len(self.list_media) - 1:
			self.selected_media += 1
			obj = self.list_media[self.selected_media]
		if not obj: return
		self.media = obj
		if obj.firstChild.UIAAutomationId == "Subtitle": name = _("Photo")
		elif obj.firstChild.UIAAutomationId == "Texture": name = _("Video")
		else: name = next((item.name for item in obj.children if item.UIAAutomationId in ("Title",)), "Media")
		ui.message(name)
		api.setNavigatorObject(obj.simpleFirstChild)

	@scriptHandler.script(description=_("Announce time and reactions"), gesture="kb:alt+w")
	def script_toggle_sounding_message_information(self, gesture):
		if scriptHandler.getLastScriptRepeatCount() == 0: ui.message(self.last_part_in_message)
		elif scriptHandler.getLastScriptRepeatCount() == 1:
			conf.set("announce_endthe_message", not conf.get("announce_endthe_message"))
			if conf.get("announce_endthe_message"): ui.message(_("Announcement of message time and reactions enabled"))
			else: ui.message(_("Announcement of message time and reactions disabled"))

	def initOverlayClass(self):
		self.states.discard(State.SELECTABLE)
		keywords = keywordsInMessages.get(conf.get("lang"), keywordsInMessages["en"])
		self.keywords = keywords
		index = self.name.find(keywords[2])
		index = index if index != -1 else self.name.find(keywords[3])
		self.index_last_part_in_message = index
		self.last_part_in_message = self.name[index:]
		if conf.get("action_when_pressing_up_arrow_in_text_field") == "to_messages":
			self.bindGesture("kb:downArrow", "next_message")

	__gestures = {
		"kb:alt+c": "show_text_message",
		"kb:rightArrow": "next_media",
		"kb:leftArrow": "voice_answer",
		"kb:backspace": "edit_message",
		"kb:enter": "reply_to_message",
	}


class Saved_items:
	_items = {}
	def get(self, key):
		focus = api.getFocusObject()
		if not focus: return False
		id = focus.windowHandle
		try: return self._items[id][key]
		except Exception: return False
	def save(self, key, obj):
		focus = api.getFocusObject()
		if not focus: return
		id = focus.windowHandle
		if id not in self._items: self._items.clear()
		self._items[id] = {}
		self._items[id][key] = obj


class AppModule(appModuleHandler.AppModule):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.saved_items = Saved_items()
		self.app_version = self.productVersion
		self.isOpenProfile = False
		self.isSkipName = 0
		self.execute_context_menu_option = False
		for i in range(10): self.bindGesture("kb:NVDA+control+%d" % i, "reviewRecentMessage")

	scriptCategory = "Telegram Justi"
	keys = {
		"upArrow": keyboardHandler.KeyboardInputGesture.fromName("upArrow"),
		"downArrow": keyboardHandler.KeyboardInputGesture.fromName("downArrow"),
		"Applications": keyboardHandler.KeyboardInputGesture.fromName("Applications"),
		"escape": keyboardHandler.KeyboardInputGesture.fromName("escape"),
		"space": keyboardHandler.KeyboardInputGesture.fromName("space"),
	}

	def getMessagesElement(self):
		obj = self.saved_items.get("messages")
		if not obj or not obj.location or not obj.location.width:
			obj = None
			item = self.get_first_item()
			while item:
				if item.UIAAutomationId == "Messages": obj = item; item = None
				else: item = item.next
			if obj: self.saved_items.save("messages", obj)
		return obj

	def get_first_item(self):
		try: return api.getForegroundObject().lastChild.previous.firstChild
		except Exception: return []

	def getElements(self):
		try: return api.getForegroundObject().lastChild.previous.children
		except Exception: return []

	def get_settings_panel(self):
		settings_panel = next((item for item in self.getElements() if item.role in (Role.PANE, Role.LIST) and item.UIAAutomationId in ("ScrollingHost", "List", "") and (item.previous.UIAAutomationId == "DetailHeaderPresenter" or item.location.width > 320)), None)
		if not settings_panel: return False
		return next((item for item in settings_panel.children if State.FOCUSABLE in item.states), settings_panel.firstChild)

	def get_profile_panel(self):
		list = self.saved_items.get("profile name")
		if not list or not list.location.width:
			list = next((item for item in self.getElements() if (item.role == Role.LIST and item.UIAAutomationId == "ScrollingHost" and item.firstChild and item.firstChild.UIAAutomationId in ("Photo", "Segments")) or (item.role == Role.LINK and item.UIAAutomationId == "Photo" and item.next.UIAAutomationId == "Title")), None)
			if not list: return False
			if list.UIAAutomationId == "Photo": return list
			self.saved_items.save("profile name", list)
			list2 = list.firstChild
			for i in range(15):
				if list2.role == Role.LIST: return next((item for item in list2.children if State.SELECTED in item.states), list2.firstChild)
				else: list2 = list2.next
			return list.firstChild

	def get_branch_list(self):
		branch_list = next((item for item in self.getElements() if item.role == Role.LIST and item.UIAAutomationId == "TopicList"), False)
		return branch_list if branch_list else False

	def is_message_object(self, obj):
		try: return obj.UIAAutomationId == "Message_item"
		except Exception: return False

	def activate_option_for_menu(self, option, list_name=False):
		if self.execute_context_menu_option: return False
		obj = api.getFocusObject()
		if list_name == "Messages" and not self.is_message_object(obj): return False
		elif list_name == "ChatsList" and obj.parent.UIAAutomationId and obj.parent.UIAAutomationId != list_name: return False
		elif not list_name and (not self.is_message_object(obj) and obj.parent.UIAAutomationId and obj.parent.UIAAutomationId != "ChatsList"): return
		self.execute_context_menu_option = option
		self.keys["Applications"].send()

	def fixedDoAction(self, obj):
		try: obj.doAction(); return
		except Exception: pass
		p = obj.location.center
		oldX, oldY = winUser.getCursorPos()
		winUser.setCursorPos(p.x, p.y)
		mouseHandler.executeMouseEvent(winUser.MOUSEEVENTF_LEFTDOWN, 0, 0)
		mouseHandler.executeMouseEvent(winUser.MOUSEEVENTF_LEFTUP, 0, 0)
		winUser.setCursorPos(oldX, oldY)

	def activateObject(self, obj):
		if not obj: return False
		try:
			obj.doAction(); return True
		except Exception: pass
		try:
			obj.setFocus(); time.sleep(0.1); self.sendKey("space"); return True
		except Exception: pass
		return False

	def sendKey(self, keyName):
		try:
			gesture = keyboardHandler.KeyboardInputGesture.fromName(keyName)
			gesture.send(); time.sleep(0.08)
		except Exception: log.exception("Error sending key: %s", keyName)

	def findObjectByName(self, obj, target):
		if not obj: return None
		try:
			name = obj.name or ""
			if target.lower() in name.lower(): return obj
		except Exception: pass
		try:
			child = obj.firstChild
			while child:
				result = self.findObjectByName(child, target)
				if result: return result
				child = child.next
		except Exception: pass
		return None

	def findObjectByAutomationID(self, obj, targetID):
		if not obj: return None
		try:
			automationID = getattr(obj, "UIAAutomationId", "") or ""
			if automationID == targetID: return obj
		except Exception: pass
		try:
			child = obj.firstChild
			while child:
				result = self.findObjectByAutomationID(child, targetID)
				if result: return result
				child = child.next
		except Exception: pass
		return None

	def findObjectByAutomationIDs(self, obj, targetIDs):
		if not obj or not targetIDs: return None
		for targetID in targetIDs:
			result = self.findObjectByAutomationID(obj, targetID)
			if result: return result
		return None

	def findObjectByNameInList(self, obj, names):
		if not obj or not names: return None
		for name in names:
			result = self.findObjectByName(obj, name)
			if result: return result
		return None

	def action_message_focus(self, obj):
		keywords = keywordsInMessages.get(conf.get("lang"), keywordsInMessages["en"])
		sender = ""
		header = False
		reactions = []
		sender_message = "received" if keywords[3] in (obj.name[-200:] if obj.name else "") else "send" if keywords[2] in (obj.name[-200:] if obj.name else "") else ""
		item = obj.firstChild
		while item:
			if item.UIAAutomationId == "Question":
				options, votes = "", ""
				for el in obj.children:
					if el.UIAAutomationId == "Votes": votes = ". " + el.name + ". "
					elif el.role == Role.TOGGLEBUTTON and el.firstChild.role == Role.PROGRESSBAR:
						if el.childCount == 3: options += self.processing_of_answer_options_in_surveys(el)
						elif el.childCount == 2: options += el.children[1].name + ", "
				if options: options = _("Answer options") + ": " + options
				obj.name = obj.name.replace(item.name + ", ", item.name + votes + options)
			elif item.UIAAutomationId == "Subtitle" and len(item.name) < 15 and " / " in item.name:
				obj.name = item.name + ", " + obj.name.replace(item.name[-5:], "")
			elif item.role == Role.LIST and item.UIAAutomationId == "Reactions": reactions = item.children
			item = item.next
		if not conf.get("announce_endthe_message") and hasattr(obj, 'index_last_part_in_message') and obj.index_last_part_in_message:
			obj.name = obj.name[:obj.index_last_part_in_message]
		obj.name = sender + obj.name
		if len(obj.name) > MAX_NAME_LENGTH: obj.name = obj.name[:MAX_NAME_LENGTH]
		if State.SELECTED in obj.states: obj.name = _("Selected") + ". " + obj.name
		if conf.get("voice_the_presence_of_a_reaction") and reactions:
			try:
				reaction_names = [r.name for r in reactions if r and r.name]
				if reaction_names: obj.name += "\n" + _("Reactions") + ": " + ", ".join(reaction_names)
			except Exception: pass
		return obj.name

	def processing_of_answer_options_in_surveys(self, obj):
		tmp_el = obj.firstChild
		processing = False
		while tmp_el.next:
			tmp_el = tmp_el.next
			if tmp_el.name == "\uf13e": processing = True
		return f'{_("Right answer")+": " if processing else ""}{obj.name}, '

	# ========== SCRIPTS ==========

	@scriptHandler.script(description=_("Move focus to chat list"), gesture="kb:alt+1")
	def script_toChatList(self, gesture):
		obj = api.getFocusObject()
		lastFocusChatElement = self.saved_items.get("last focused chat")
		if lastFocusChatElement and lastFocusChatElement.location and lastFocusChatElement.location.width:
			if obj == lastFocusChatElement: ui.message(obj.name)
			else: lastFocusChatElement.setFocus()
			return
		targetList = self.getChatsListElement()
		if targetList and targetList.firstChild:
			targetList = targetList.firstChild
			if targetList.role == Role.BUTTON and targetList.next: targetList = targetList.next
			if targetList.role == Role.LISTITEM: targetList.setFocus(); return
		ui.message(_("Chat list not found"))

	def getChatsListElement(self):
		targetList = self.saved_items.get("chats")
		if targetList and targetList.location and targetList.location.width: return targetList
		targetList = next((item for item in self.getElements() if item.role == Role.LIST and item.UIAAutomationId == "ChatsList"), False)
		if targetList: self.saved_items.save("chats", targetList)
		return targetList

	@scriptHandler.script(description=_("Move focus to last message"), gesture="kb:alt+2")
	def script_toLastMessage(self, gesture):
		focusObj = api.getFocusObject()
		if self.is_message_object(focusObj):
			if focusObj.parent.next: keyboardHandler.KeyboardInputGesture.fromName("end").send()
			else: ui.message(focusObj.name)
			return True
		obj = self.getMessagesElement()
		try:
			obj.lastChild.setFocus(); keyboardHandler.KeyboardInputGesture.fromName("end").send()
		except Exception:
			if obj and not obj.lastChild: ui.message(_("This chat is empty")); return True
			branch_list = self.get_branch_list()
			if branch_list: branch_list.firstChild.setFocus(); return
			profile_panel = self.get_profile_panel()
			if profile_panel: profile_panel.setFocus(); return
			settings_panel = self.get_settings_panel()
			if settings_panel: settings_panel.setFocus(); return
			ui.message(_("No open chat"))

	@scriptHandler.script(description=_("Move focus to unread messages"), gesture="kb:alt+3")
	def script_goToTheLastUnreadMessage(self, gesture):
		messages = self.getMessagesElement()
		try: lastObj = messages.lastChild
		except Exception: ui.message(_("No open chat")); return False
		targetButton = False
		while lastObj:
			try:
				first = lastObj.firstChild
				if first and first.role == Role.BUTTON:
					first_child = first.firstChild
					if first_child and first_child.next and first_child.next.name == "\ue0e5": targetButton = lastObj; break
			except Exception: pass
			lastObj = lastObj.previous
		if targetButton: targetButton.setFocus()
		else: ui.message(_("No unread messages"))

	@scriptHandler.script(description=_("Move focus to chat folders"), gesture="kb:alt+4")
	def script_to_tabs_folder(self, gesture):
		obj = self.saved_items.get("tabs folder")
		if obj and obj.location and obj.location.width:
			el = next((item for item in obj.children if State.SELECTED in item.states), None)
			if el: el.setFocus()
			else: ui.message(_("Chat folder list not found"))
		else: ui.message(_("Chat folder list not found"))

	@scriptHandler.script(description=_("Move focus to open profile"), gesture="kb:alt+5")
	def script_to_open_profile(self, gesture):
		profile_panel = self.get_profile_panel()
		if profile_panel: profile_panel.setFocus()
		else: ui.message(_("There is no open profile"))

	@scriptHandler.script(description=_("Move focus to group threads"), gesture="kb:alt+6")
	def script_move_focus_to_list_threads(self, gesture):
		branch_list = self.get_branch_list()
		if branch_list: branch_list.firstChild.setFocus()
		else: ui.message(_("No list with threads was found"))

	@scriptHandler.script(description=_("Move focus to edit field"), gesture="kb:alt+d")
	def script_moveFocusToTextMessage(self, gesture):
		obj = api.getFocusObject()
		lastFocusObject = self.saved_items.get("last focus object")
		if (obj.role == Role.EDITABLETEXT and obj.UIAAutomationId == "TextField") or (obj.role == Role.BUTTON and obj.UIAAutomationId == "ButtonAction"):
			if lastFocusObject and lastFocusObject.location: lastFocusObject.setFocus()
			return
		targetButton = self.saved_items.get("message box")
		if not targetButton or not targetButton.location or not targetButton.location.width:
			targetButton = False
			for item in reversed(self.getElements()):
				if item.role == Role.EDITABLETEXT and item.UIAAutomationId == "TextField":
					targetButton = item; self.saved_items.save("message box", item); break
		if targetButton: targetButton.setFocus()
		elif lastFocusObject and lastFocusObject.location: lastFocusObject.setFocus()
		else: ui.message(_("Message input field not found"))

	@scriptHandler.script(description=_("Copy message"), gesture="kb:control+c")
	def script_copyMessage(self, gesture):
		gesture.send()
		obj = api.getFocusObject()
		try:
			if obj.parent.UIAAutomationId in ("Message", "TextBlock"):
				textMessage = obj.name
				if textMessage: api.copyToClip(textMessage.strip()); ui.message(_("Link copied"))
				else: ui.message(_("This message does not contain text"))
		except Exception: pass

	@scriptHandler.script(description=_("Delete a message or chat"), gesture="kb:alt+delete")
	def script_deletion(self, gesture):
		self.deleteMessageAndChat(api.getFocusObject())

	@scriptHandler.script(description=_("Delete from both sides"), gesture="kb:shift+delete")
	def script_completeDeletion(self, gesture):
		self.deleteMessageAndChat(api.getFocusObject(), isComplete=True)

	@scriptHandler.script(description=_("Mark chat as read"), gesture="kb:alt+shift+r")
	def script_readMessage(self, gesture):
		self.activate_option_for_menu((icons_from_context_menu["read"], icons_from_context_menu["unread"]), "ChatsList")

	@scriptHandler.script(description=_("Forward message"), gesture="kb:alt+f")
	def script_forwardMessage(self, gesture):
		self.activate_option_for_menu((icons_from_context_menu["forward"]), "Messages")

	@scriptHandler.script(description=_("Select messages"), gesture="kb:control+space")
	def script_selectMessage(self, gesture):
		self.activate_option_for_menu((icons_from_context_menu["select"]), "Messages")

	@scriptHandler.script(description=_("Pin message or chat"))
	def script_attach(self, gesture):
		self.activate_option_for_menu((icons_from_context_menu["attach"], icons_from_context_menu["unpin"]))

	@scriptHandler.script(description=_("Open navigation menu"), gesture="kb:alt+m")
	def script_showMenu(self, gesture):
		targetButton = next((item for item in self.getElements() if item.UIAAutomationId == "Photo" and item.role == Role.TOGGLEBUTTON), False)
		if targetButton: targetButton.doAction()
		else: ui.message(_("Navigation menu not available"))

	@scriptHandler.script(description=_("Open profile"), gesture="kb:control+p")
	def script_openProfile(self, gesture):
		profile = self.saved_items.get("profile name")
		if not profile or profile.location.width == 0:
			profile = next((item for item in self.getElements() if item.role == Role.BUTTON and item.UIAAutomationId == "Profile"), None)
			if profile: self.saved_items.save("profile name", profile)
		if profile and profile.location.width != 0:
			self.isOpenProfile = api.getFocusObject()
			profile.doAction()
		else: ui.message(_("No open chat"))

	@scriptHandler.script(description=_("Voice message recording"), gesture="kb:control+r")
	def script_recordingVoiceMessage(self, gesture):
		lastFocus = api.getFocusObject()
		obj = False
		for item in reversed(self.getElements()):
			if item.role == Role.TOGGLEBUTTON and item.UIAAutomationId == "btnVoiceMessage": obj = item; break
			elif item.role == Role.BUTTON and item.UIAAutomationId in ("btnSendMessage", "btnEdit"):
				ui.message(_("Recording a voice message will not be available until the edit field is empty")); return
		if not obj: return
		if conf.get("isFixedToggleButton"):
			self.isSkipName = 1; gesture.send()
		else:
			obj.doAction(); lastFocus.setFocus()

	@scriptHandler.script(description=_("Cancel voice message recording"), gesture="kb:control+shift+r")
	def script_cancelVoiceMessageRecording(self, gesture):
		if scriptHandler.getLastScriptRepeatCount() == 1:
			indicator = conf.get("voiceMessageRecordingIndicator")
			if indicator == "none": conf.set("voiceMessageRecordingIndicator", "text"); ui.message(_("Voice recording notifications set to text"))
			elif indicator == "text": conf.set("voiceMessageRecordingIndicator", "audio"); ui.message(_("Voice recording notifications set to sounds"))
			elif indicator == "audio": conf.set("voiceMessageRecordingIndicator", "none"); ui.message(_("Recording voice messages has standard behavior"))
			return
		obj = next((item for item in reversed(self.getElements()) if (item.UIAAutomationId == "ElapsedLabel") or (item.role == Role.BUTTON and item.UIAAutomationId == "ComposerHeaderCancel")), False)
		lastFocus = api.getFocusObject()
		if obj and obj.UIAAutomationId == "ComposerHeaderCancel":
			obj.doAction(); lastFocus.setFocus()
			if obj.previous and obj.previous.name == "\uea4a": ui.message(_("Reply canceled"))
			elif obj.previous and obj.previous.name == "\uea4b": ui.message(_("Edit canceled"))
			else: ui.message(_("Recording canceled"))
		gesture.send(); lastFocus.setFocus()

	@scriptHandler.script(description=_("Play/pause voice message"), gesture="kb:space")
	def script_playPauseAudio(self, gesture):
		try:
			focus = api.getFocusObject()
			if not focus: gesture.send(); return
			audioMessage = self.findObjectByAutomationIDs(focus, ("Recognize", "RecognizedText", "Subtitle"))
			if audioMessage:
				try: focus.doAction(); tones.beep(900, 50); return
				except Exception: pass
				playButton = self.findObjectByNameInList(focus, ("Reproducir", "Play", "Pausar", "Pause"))
				if playButton: self.activateObject(playButton); tones.beep(900, 50); return
		except Exception: log.exception("Error playing audio")
		gesture.send()

	@scriptHandler.script(description=_("Increase/decrease playback speed"), gesture="kb:alt+s")
	def script_voiceMessageAcceleration(self, gesture):
		targetButton = next((item for item in self.getElements() if item.role == Role.BUTTON and item.UIAAutomationId == "SpeedButton"), False)
		if not targetButton and self.getElements() and self.getElements()[0].role == Role.WINDOW:
			targetButton = next((item for item in self.getElements()[0].children if item.role == Role.BUTTON and item.UIAAutomationId == "SpeedButton"), False)
		if targetButton: targetButton.doAction()
		else: ui.message(_("Nothing is playing right now"))

	@scriptHandler.script(description=_("Close audio player"), gesture="kb:alt+e")
	def script_closingVoiceMessage(self, gesture):
		try: targetButton = next((item for item in self.getElements()[1:] if item.previous.role == Role.TOGGLEBUTTON and item.previous.UIAAutomationId == "ShuffleButton"), False)
		except Exception: targetButton = False
		if targetButton:
			lastFocus = api.getFocusObject(); targetButton.doAction(); lastFocus.setFocus()
			ui.message(_("The audio player has been closed"))
		else: ui.message(_("Nothing is playing right now"))

	@scriptHandler.script(description=_("Convert voice message to text"), gesture="kb:NVDA+alt+r")
	def script_Recognize_voice_message(self, gesture):
		obj = api.getFocusObject()
		button = next((item for item in obj.children if item.UIAAutomationId == "Recognize"), None)
		if button:
			if button.next and button.next.UIAAutomationId == "RecognizedText" and button.next.name: ui.message(_("Already converted"))
			elif button.next and button.next.UIAAutomationId == "RecognizedText": ui.message(_("Converting..."))
			else: return
			button.doAction(); obj.setFocus()
			try: playWaveFile(baseDir + "RecognitionStart.wav")
			except Exception: ui.message(_("Conversion started"))
		else: ui.message(_("Button not found"))

	@scriptHandler.script(description=_("Rewind voice message"), gesture="kb:control+alt+leftArrow")
	def script_rewindVoiceMessageBack(self, gesture): self._rewind_voice_message("leftArrow")

	@scriptHandler.script(description=_("Fast forward voice message"), gesture="kb:control+alt+rightArrow")
	def script_rewindVoiceMessageForward(self, gesture): self._rewind_voice_message("rightArrow")

	def _rewind_voice_message(self, direction):
		slider = self.saved_items.get("slider")
		if not slider or slider.location.width == 0: ui.message(_("Nothing is playing right now")); return
		self.script_pauseVoiceMessage(None)
		obj = api.getFocusObject()
		slider.setFocus()
		keyboardHandler.KeyboardInputGesture.fromName(direction).send()
		self.script_pauseVoiceMessage(None)
		obj.setFocus()
		speech.cancelSpeech()

	@scriptHandler.script(description=_("Pause voice message"), gesture="kb:alt+p")
	def script_pauseVoiceMessage(self, gesture):
		targetButton = next((item for item in self.getElements() if item.role == Role.BUTTON and item.UIAAutomationId == "PlaybackButton"), False)
		if targetButton:
			lastFocus = api.getFocusObject(); targetButton.doAction(); lastFocus.setFocus()
		else: ui.message(_("Nothing is playing right now"))

	@scriptHandler.script(description=_("Open instant view"), gesture="kb:alt+q")
	def script_instantView(self, gesture):
		obj = api.getFocusObject()
		if not self.is_message_object(obj): return
		targetButton = next((item.next for item in obj.children if item.UIAAutomationId == "TextBlock" and item.next and item.next.lastChild and item.next.lastChild.UIAAutomationId == "Button"), False)
		if targetButton:
			targetButton.doAction()
			targetList = next((item for item in self.getElements() if item.role == Role.LIST and item.UIAAutomationId == "ScrollingHost"), False)
			if targetList:
				item = next((item for item in targetList.children if item.name != ""), None)
				if item: item.setFocus()
		else: ui.message(_("Button not found"))

	@scriptHandler.script(description=_("Answer call"), gesture="kb:alt+y")
	def script_answeringCall(self, gesture):
		gesture.send()
		desktop = api.getDesktopObject()
		notification = next((item.firstChild.firstChild for item in desktop.children if hasattr(item.firstChild, 'UIAAutomationId') and item.firstChild.UIAAutomationId == "ToastCenterScrollViewer"), False)
		if not notification: return
		button = next((item for item in notification.children if item.UIAAutomationId == "VerbButton"), None)
		if button: button.doAction()

	@scriptHandler.script(description=_("Decline/end call"), gesture="kb:alt+n")
	def script_callCancellation(self, gesture):
		gesture.send()
		desktop = api.getDesktopObject()
		notification = next((item.firstChild.firstChild for item in desktop.children if hasattr(item.firstChild, 'UIAAutomationId') and item.firstChild.UIAAutomationId == "ToastCenterScrollViewer"), False)
		if not notification:
			self._callCancellationAppModule(gesture); return
		button = next((item.next for item in notification.children if item.UIAAutomationId == "VerbButton"), None)
		if button: button.doAction()

	def _callCancellationAppModule(self, gesture):
		elements = self.getElements()
		targetButton = next((item for item in elements[1:] if (item.UIAAutomationId == "Accept" and item.previous.UIAAutomationId == "Audio") or (item.UIAAutomationId == "Leave" and item.firstChild and item.firstChild.name == "\ue711") or (item.previous.UIAAutomationId == "Audio" and item.firstChild and item.firstChild.name == "\ue711")), False)
		if targetButton:
			lastFocus = api.getFocusObject(); ui.message(targetButton.name); self.fixedDoAction(targetButton); lastFocus.setFocus()

	@scriptHandler.script(description=_("Mute microphone"), gesture="kb:alt+a")
	def script_microphone(self, gesture):
		obj = api.getFocusObject()
		for item in self.getElements():
			if item.UIAAutomationId == "Audio" and item.next.UIAAutomationId == "AudioInfo":
				item.doAction(); obj.setFocus()
				def spechState(): ui.message(item.next.name)
				Timer(.1, spechState).start(); return
			elif item.UIAAutomationId == "Audio" and item.previous.UIAAutomationId == "Video" and item.next.UIAAutomationId == "Accept":
				self.fixedDoAction(item); obj.setFocus()
				def spechState(): ui.message(item.name)
				Timer(.1, spechState).start(); return

	@scriptHandler.script(description=_("Enable/disable camera"), gesture="kb:alt+v")
	def script_video(self, gesture):
		obj = api.getFocusObject()
		for item in self.getElements():
			if item.UIAAutomationId == "Video" and item.next.UIAAutomationId == "VideoInfo":
				item.doAction(); obj.setFocus()
				def spechState(): ui.message(_("Camera on") if item.firstChild.name == "\ue964" else _("Camera off"))
				Timer(.1, spechState).start(); return
			elif item.UIAAutomationId == "Video" and item.next.UIAAutomationId == "Audio" and item.next.next.UIAAutomationId == "Accept":
				self.fixedDoAction(item); obj.setFocus()
				def spechState(): ui.message(item.name)
				Timer(.1, spechState).start(); return

	@scriptHandler.script(description=_("Go to end"), gesture="kb:alt+end")
	def script_to_down(self, gesture):
		button = next((item for item in self.getElements() if item.role == Role.BUTTON and item.UIAAutomationId == "MessagesButton"), None)
		if button: button.doAction()
		else: ui.message(_("Button not found"))

	@scriptHandler.script(description=_("Go to search results"), gesture="kb:alt+i")
	def script_go_to_list_search_results(self, gesture):
		obj = api.getFocusObject()
		btn = next((element.next for element in self.getElements() if element.role == Role.EDITABLETEXT and element.UIAAutomationId == "Field" and "/" in element.next.name and element.next.role == Role.BUTTON), None)
		if btn: btn.doAction()
		else: ui.message(_("Button not found"))

	@scriptHandler.script(description=_("Next search result"), gesture="kb:f3")
	def script_go_to_previous_search_result(self, gesture):
		btn = next((item for item in self.getElements() if item.UIAAutomationId == "SearchPrevious" and item.role == Role.BUTTON), None)
		if btn and State.FOCUSABLE in btn.states: btn.doAction()
		elif btn: ui.message(_("No next search result"))
		else: ui.message(_("Button not found"))

	@scriptHandler.script(description=_("Previous search result"), gesture="kb:shift+f3")
	def script_go_to_next_search_result(self, gesture):
		btn = next((item for item in self.getElements() if item.UIAAutomationId == "SearchNext" and item.role == Role.BUTTON), None)
		if btn and State.FOCUSABLE in btn.states: btn.doAction()
		elif btn: ui.message(_("No previous search result"))
		else: ui.message(_("Button not found"))

	@scriptHandler.script(description=_("Review recent message"), gesture="kb:NVDA+control+1")
	def script_reviewRecentMessage(self, gesture):
		try: index = int(gesture.mainKeyName[-1])
		except (AttributeError, ValueError): return
		if index == 0: index = 10
		obj = self.getMessagesElement()
		if not obj: ui.message(_("No open chat")); return
		target = obj.lastChild
		if not target: ui.message(_("This chat is empty")); return
		i = 0
		while target:
			child = target.firstChild
			if child.role not in (Role.BUTTON, Role.GROUPING):
				i += 1
				if i == index: ui.message(self.action_message_focus(target)); api.setNavigatorObject(target); break
			target = target.previous
		if i < index: ui.message(_("This chat is empty"))

	def deleteMessageAndChat(self, obj, isComplete=False):
		if not obj: return
		if self.is_message_object(obj):
			self.activate_option_for_menu((icons_from_context_menu["delete"],), "Messages")
		elif obj.parent.UIAAutomationId == "ChatsList":
			self.activate_option_for_menu((icons_from_context_menu["delete"],), "ChatsList")

	@scriptHandler.script(description=_("Show shortcuts list"), gesture="kb:alt+h")
	def script_help(self, gesture):
		try:
			a = next((item for item in addonHandler.getAvailableAddons() if item.name == "TelegramJusti"), None)
			a = a.getDocFilePath()[:-4] + "md"
			with open(a, "r", encoding="utf-8") as file: text = file.read()
			blocks = text.split("\n\n")
			count_rows = [len(item.split("\n")) for item in blocks]
			index = count_rows.index(max(count_rows))
			TextWindow(blocks[index].replace("* ", "").replace("## ", "").strip(), _("List of shortcuts"), readOnly=True)
		except Exception: ui.message(_("Could not open help"))

	@scriptHandler.script(description=_("Toggle live chat reading"), gesture="kb:alt+l")
	def script_toggle_live_chat(self, gesture):
		ui.message(_("Feature coming soon"))

	# ========== EVENT HANDLING ==========

	def event_gainFocus(self, obj, nextHandler):
		if obj.role == Role.LISTITEM:
			if self.is_message_object(obj):
				name = getattr(obj, 'name', "")
				if name and len(name) > MAX_NAME_LENGTH:
					obj.name = name[:MAX_NAME_LENGTH]
				self.saved_items.save("last focus object", obj)
				obj.name = self.action_message_focus(obj)
			elif obj.parent.UIAAutomationId == "ChatsList":
				self.saved_items.save("last focused chat", obj)
			elif self.isSkipName:
				speech.cancelSpeech()
				self.isSkipName -= 1
				return True
		elif self.isOpenProfile:
			self.isOpenProfile = False
			panel = next((item for item in self.getElements() if item.UIAAutomationId == "ScrollingHost"), None)
			if panel: panel.firstChild.setFocus()
		elif self.execute_context_menu_option:
			try: targetButton = next((item for item in obj.parent.children if item.firstChild.name in self.execute_context_menu_option), False)
			except Exception: targetButton = False
			self.execute_context_menu_option = False
			if targetButton: targetButton.doAction()
			else: self.keys["escape"].send()
			return
		nextHandler()

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		try:
			if obj.role == Role.LISTITEM and obj.name and obj.isFocusable:
				parent = obj.parent
				if parent and parent.UIAAutomationId == "ChatsList": pass
				elif self.is_message_object(obj): clsList.insert(0, Message_list_item)
			elif obj.role == Role.EDITABLETEXT and obj.UIAAutomationId == "TextField":
				clsList.insert(0, EditableTextOverlay)
		except Exception: pass

	# ========== GESTURES ==========

	__gestures = {
		"kb:escape": "action_escape_key",
		"kb:space": "script_playPauseAudio",
		"kb:control+d": "script_cancelVoiceMessageRecording",
	}

	def script_action_escape_key(self, gesture):
		gesture.send()
		if self.isSkipName: self.isSkipName -= 1


class EditableTextOverlay(editableText.EditableText):
	def script_caret_moveByLine(self, gesture):
		if gesture.mainKeyName != "upArrow": return super().script_caret_moveByLine(gesture)
		info = None
		try: info = self.makeTextInfo(textInfos.POSITION_ALL)
		except Exception: pass
		if info and info.text == "":
			if conf.get("action_when_pressing_up_arrow_in_text_field") == "to_messages": self.appModule.script_toLastMessage(None)
			elif conf.get("action_when_pressing_up_arrow_in_text_field") == "normal": gesture.send()
			else: ui.message("")
			return
		return super().script_caret_moveByLine(gesture)

	def script_sendMessage(self, gesture):
		gesture.send()
		info = None
		try: info = self.makeTextInfo(textInfos.POSITION_ALL)
		except Exception: pass
		if info and info.text.strip() != "": Timer(0.2, lambda: self.appModule.script_toLastMessage(None)).start()

	__gestures = {
		"kb:enter": "sendMessage",
		"kb:numpadEnter": "sendMessage",
	}

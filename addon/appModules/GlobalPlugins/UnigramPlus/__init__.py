# -*- coding: utf-8 -*-
import globalPluginHandler
import globalVars
import addonHandler
from scriptHandler import script
import api
import gui
from gui import guiHelper, nvdaControls
from gui.settingsDialogs import SettingsPanel
import wx
import threading
import os
from appModules.cnf import conf, listLanguages, lang
from appModules.unigram import AppModule
from ui import message


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = "Telegram Justi"
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(TelegramJustiSettings)

	@script(description=_("Open Telegram Justi settings window"), gesture="kb:NVDA+ALT+U")
	def script_open_settings_dialog(self, gesture, arg=False):
		wx.CallAfter(gui.mainFrame._popupSettingsDialog, gui.settingsDialogs.NVDASettingsDialog, TelegramJustiSettings)


class TelegramJustiSettings(SettingsPanel):
	title = "Telegram Justi"
	listVoiceTypeAfterChatName = {
		"beforeName": _("Before chat name"),
		"afterName": _("After chat name"),
		"don'tVoice": _("Do not speak chat type"),
	}
	listSaySenderName = {
		"none": _("Do not say at all"),
		"sent": _("Only in sent messages"),
		"received": _("Only in received messages"),
		"all": _("In all messages"),
	}
	list_actions_when_pressing_up_arrow_in_text_field = {
		"block": _("Do nothing"),
		"normal": _("Activate editing of last sent message"),
		"to_messages": _("Move focus to the last message in a chat"),
	}

	def makeSettings(self, settingsSizer):
		settingsSizerHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self.lang = settingsSizerHelper.addLabeledControl(
			_("Interface language in Unigram:"), wx.Choice,
			choices=list(listLanguages.values())
		)
		self.lang.SetStringSelection(listLanguages[conf.get("lang")])
		self.voiceTypeAfterChatName = settingsSizerHelper.addLabeledControl(
			_("Speak the type of chat in the chat list:"), wx.Choice,
			choices=[self.listVoiceTypeAfterChatName[item] for item in self.listVoiceTypeAfterChatName]
		)
		self.voiceTypeAfterChatName.SetStringSelection(self.listVoiceTypeAfterChatName[conf.get("voiceTypeAfterChatName")])
		self.saySenderName = settingsSizerHelper.addLabeledControl(
			_("Say the sender's name in:"), wx.Choice,
			choices=[self.listSaySenderName[item] for item in self.listSaySenderName]
		)
		self.saySenderName.SetStringSelection(self.listSaySenderName[conf.get("saySenderName")])
		self.action_when_pressing_up_arrow_in_text_field = settingsSizerHelper.addLabeledControl(
			_("Action when pressing the up arrow in the message edit field"), wx.Choice,
			choices=list(self.list_actions_when_pressing_up_arrow_in_text_field.values())
		)
		self.action_when_pressing_up_arrow_in_text_field.SetStringSelection(
			self.list_actions_when_pressing_up_arrow_in_text_field[conf.get("action_when_pressing_up_arrow_in_text_field")]
		)
		self.unreadBeforeMessageContent = settingsSizerHelper.addItem(
			wx.CheckBox(self, label=_("Speak \"Not Seen\" before reading contents of a message"))
		)
		self.unreadBeforeMessageContent.SetValue(conf.get("unreadBeforeMessageContent"))
		self.voice_the_presence_of_a_reaction = settingsSizerHelper.addItem(
			wx.CheckBox(self, label=_("Announce if the message contains a reaction"))
		)
		self.voice_the_presence_of_a_reaction.SetValue(conf.get("voice_the_presence_of_a_reaction"))
		self.notify_administrators_in_messages = settingsSizerHelper.addItem(
			wx.CheckBox(self, label=_('Announce the phrases "Administrator" and "Owner" on messages in communities'))
		)
		self.notify_administrators_in_messages.SetValue(conf.get("notify_administrators_in_messages"))
		self.voiceFolderNames = settingsSizerHelper.addItem(
			wx.CheckBox(self, label=_("Speak folder names when switching between them"))
		)
		self.voiceFolderNames.SetValue(conf.get("voiceFolderNames"))
		self.voiceMessageRecordingIndicator = settingsSizerHelper.addLabeledControl(
			_("Set voice message recording notification method as:"), wx.Choice,
			choices=[_("Revert to standard"), _("Text notification"), _("Sound notification")]
		)
		self.voiceMessageRecordingIndicator.SetStringSelection(conf.get("voiceMessageRecordingIndicator"))
		self.actionDescriptionForLinks = settingsSizerHelper.addItem(
			wx.CheckBox(self, label=_("Read description of URLs attached to messages"))
		)
		self.actionDescriptionForLinks.SetValue(conf.get("actionDescriptionForLinks"))
		self.voiceFullDescriptionOfLinkToYoutube = settingsSizerHelper.addItem(
			wx.CheckBox(self, label=_("Read full video description in YouTube URLs"))
		)
		self.voiceFullDescriptionOfLinkToYoutube.SetValue(conf.get("voiceFullDescriptionOfLinkToYoutube"))

	def get_key(self, d, value):
		for k, v in d.items():
			if v == value: return k

	def onSave(self):
		conf.set("lang", self.get_key(listLanguages, self.lang.GetStringSelection()))
		conf.set("voiceTypeAfterChatName", self.get_key(self.listVoiceTypeAfterChatName, self.voiceTypeAfterChatName.GetStringSelection()))
		conf.set("saySenderName", self.get_key(self.listSaySenderName, self.saySenderName.GetStringSelection()))
		conf.set("unreadBeforeMessageContent", self.unreadBeforeMessageContent.IsChecked())
		conf.set("voice_the_presence_of_a_reaction", self.voice_the_presence_of_a_reaction.IsChecked())
		conf.set("notify_administrators_in_messages", self.notify_administrators_in_messages.IsChecked())
		conf.set("voiceFolderNames", self.voiceFolderNames.IsChecked())
		conf.set("voiceMessageRecordingIndicator", self.get_key(
			{"none": "none", "text notification": "text", "sound notification": "audio"},
			self.voiceMessageRecordingIndicator.GetStringSelection()
		))
		conf.set("actionDescriptionForLinks", self.actionDescriptionForLinks.IsChecked())
		conf.set("voiceFullDescriptionOfLinkToYoutube", self.voiceFullDescriptionOfLinkToYoutube.IsChecked())
		conf.set("action_when_pressing_up_arrow_in_text_field", self.get_key(
			self.list_actions_when_pressing_up_arrow_in_text_field,
			self.action_when_pressing_up_arrow_in_text_field.GetStringSelection()
		))

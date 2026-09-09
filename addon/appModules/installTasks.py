# -*- coding: UTF-8 -*-
import addonHandler

def onInstall():
	for addon in addonHandler.getAvailableAddons():
		if addon.manifest['name'] in ("unigramPlus", "TelegramJusti"):
			addon.requestRemove()

def onUninstall():
	pass

def onPostInstall():
	pass

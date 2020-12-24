import json, os

from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import *

class Settings:
    notify = directNotify.newCategory('Settings')
    GL = 0
    DX7 = 1
    DX8 = 5
    windowedMode = 1
    music = 1
    sfx = 1
    toonChatSounds = 1
    musicVolume = 1.0
    sfxVolume = 1.0
    embeddedMode = 0
    acceptingNewFriends = 1
    acceptingNonFriendWhispers = 1
    resolutionDimensions = (800, 600)
    resList = [(640, 480),
               (800, 600),
               (1024, 768),
               (1280, 1024),
               (1600, 1200),
               (1920, 1080),
               (4096, 2160)]


    @staticmethod
    def readSettings():
        if Settings.doSavedSettingsExist():
            settingsFile = open('user/ttgsettings.json')
            settingsData = settingsFile.read()
            del settingsFile
            try:
                settings = json.loads(settingsData).get('UserSettings')
            except:
                settings = {}

            Settings.setMusic(settings.get('music', 1))
            Settings.setSfx(settings.get('sfx', 1))
            Settings.setToonChatSounds(settings.get('toonChatSounds', 1))
            Settings.setAcceptingNewFriends(settings.get('acceptingNewFriends', 1))
            Settings.setAcceptingNonFriendWhispers(settings.get('acceptingNonFriendWhispers', 1))
            Settings.setResolutionDimensions(Settings.resList[settings.get('resolution', 1)][0],
                                             Settings.resList[settings.get('resolution', 1)][1])
            Settings.setWindowedMode(settings.get('windowedMode', 1))
            Settings.setEmbeddedMode(settings.get('embeddedMode', 0))

    @staticmethod
    def writeSettings():
        if Settings.doSavedSettingsExist():
            settingsFile = open('user/ttgsettings.json')
            settingsData = settingsFile.read()
            del settingsFile
            try:
                settings = json.loads(settingsData)
            except:
                settings = {}
                settings['UserSettings'] = {}
        else:
            settings = {}
            settings['UserSettings'] = {}

        settings['UserSettings']['music'] = Settings.getMusic()
        settings['UserSettings']['sfx'] = Settings.getSfx()
        settings['UserSettings']['toonChatSounds'] = Settings.getToonChatSounds()
        settings['UserSettings']['acceptingNewFriends'] = Settings.getAcceptingNewFriends()
        settings['UserSettings']['acceptingNonFriendWhispers'] = Settings.getAcceptingNonFriendWhispers()
        settings['UserSettings']['resolution'] = Settings.getResolution()
        settings['UserSettings']['windowedMode'] = Settings.getWindowedMode()
        settings['UserSettings']['embeddedMode'] = Settings.getEmbeddedMode()

        with open('user/ttgsettings.json', 'w') as f:
            f.write(json.dumps(settings))

    @staticmethod
    def setWindowedMode(windowedMode):
        Settings.windowedMode = windowedMode

    @staticmethod
    def getWindowedMode():
        return Settings.windowedMode

    @staticmethod
    def setMusic(music):
        Settings.music = music

    @staticmethod
    def getMusic():
        return Settings.music

    @staticmethod
    def setSfx(sfx):
        Settings.sfx = sfx

    @staticmethod
    def getSfx():
        return Settings.sfx

    @staticmethod
    def setToonChatSounds(toonChatSounds):
        Settings.toonChatSounds = toonChatSounds

    @staticmethod
    def getToonChatSounds():
        return Settings.toonChatSounds

    @staticmethod
    def getMusicVolume():
        return Settings.musicVolume

    @staticmethod
    def getSfxVolume():
        return Settings.sfxVolume

    @staticmethod
    def getResolution():
        return Settings.resList.index(Settings.resolutionDimensions)

    @staticmethod
    def setEmbeddedMode(embeddedMode):
        Settings.embeddedMode = embeddedMode

    @staticmethod
    def getEmbeddedMode():
        return Settings.embeddedMode

    @staticmethod
    def doSavedSettingsExist():
        return os.path.exists('user/ttgsettings.json')

    @staticmethod
    def setAcceptingNewFriends(acceptingNewFriends):
        Settings.acceptingNewFriends = acceptingNewFriends

    @staticmethod
    def getAcceptingNewFriends():
        return Settings.acceptingNewFriends

    @staticmethod
    def setAcceptingNonFriendWhispers(acceptingNonFriendWhispers):
        Settings.acceptingNonFriendWhispers = acceptingNonFriendWhispers

    @staticmethod
    def getAcceptingNonFriendWhispers():
        return Settings.acceptingNonFriendWhispers

    @staticmethod
    def setResolutionDimensions(x, y):
        Settings.resolutionDimensions = (x, y)

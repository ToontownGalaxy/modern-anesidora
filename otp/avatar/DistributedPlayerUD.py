from otp.avatar.DistributedAvatarUD import DistributedAvatarUD
from direct.directnotify.DirectNotifyGlobal import directNotify

class DistributedPlayerUD(DistributedAvatarUD):
    notify = directNotify.newCategory('DistributedPlayerUD')

    def arrivedOnDistrict(self, districtId):
        pass

    def setChat(self, chatString, chatFlags, accountId):
        pass

    def setWLChat(self, chatString, chatFlags, accountId):
        pass

    def setWhisperFrom(self, fromId, chatString, senderAccountId):
        pass

    def setWhisperWLFrom(self, fromId, chatString, senderAccountId):
        pass

    def setWhisperSCFrom(self, fromId, msgIndex):
        pass

    def setWhisperSCCustomFrom(self, fromId, msgIndex):
        pass

    def setWhisperSCEmoteFrom(self, fromId, emoteId):
        pass

    def setSystemMessage(self, aboutId, chatString):
        pass

    def setChatFlag(self, chatFlag):
        pass

    def setSC(self, msgIndex):
        pass

    def setSCCustom(self, msgIndex):
        pass

    def setFriendsList(self, friendsList):
        pass

    def setAccountId(self, accountId):
        pass

    def setAccountName(self, name):
        pass

    def setAccessLevel(self, access):
        pass

    def OwningAccount(self, doId):
        pass

    def WishName(self, name):
        pass

    def WishNameState(self, state):
        pass

    def setPreviousAccess(self, access):
        pass

    def setAccess(self, access):
        pass
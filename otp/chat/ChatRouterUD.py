from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from toontown.chat.TTWhiteList import TTWhiteList

whiteList = TTWhiteList()

class ChatRouterUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('ChatRouterUD')

    def filterWhitelist(self, message):
        words = message.split(' ')
        offset = 0
        mods = []

        for word in words:
            if not whiteList.isWord(word):
                mods.append((offset, offset + len(word) - 1))

            offset += len(word) + 1

        return mods

    def chatMessage(self, message):
        avId = self.air.getAvatarIdFromSender()

        if not avId:
            return

        channel = avId

        mods = self.filterWhitelist(message)

        do = self.air.dclassesByName['DistributedPlayerUD']
        args = [avId, 0, '', message, mods, 0]
        datagram = do.aiFormatUpdate('setTalk', avId, channel, self.air.ourChannel, args)
        self.air.send(datagram)

    def whisperMessage(self, message, receiverAvId):
        avId = self.air.getAvatarIdFromSender()

        if not avId:
            return

        mods = self.filterWhitelist(message)

        do = self.air.dclassesByName['DistributedPlayerUD']
        args = [avId, 0, '', message, mods, 0]
        datagram = do.aiFormatUpdate('setTalkWhisper', receiverAvId, receiverAvId, self.air.ourChannel, args)
        self.air.send(datagram)
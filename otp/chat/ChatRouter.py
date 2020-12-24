from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal

class ChatRouter(DistributedObjectGlobal):
    notify = directNotify.newCategory('ChatRouter')

    def sendChatMessage(self, message):
        self.sendUpdate('chatMessage', [message])

    def sendWhisperMessage(self, message, receiverAvId):
        self.sendUpdate('whisperMessage', [message, receiverAvId])
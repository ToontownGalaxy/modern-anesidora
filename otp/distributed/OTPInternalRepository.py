from direct.directnotify import DirectNotifyGlobal
from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.distributed.PyDatagram import *
from otp.ai import AIMsgTypes
from direct.distributed import MsgTypes

class OTPInternalRepository(AstronInternalRepository):
    notify = DirectNotifyGlobal.directNotify.newCategory('OTPInternalRepository')
    dbId = 4003

    def __init__(self, baseChannel, serverId, dcFileNames, dcSuffix, connectMethod, threadedNet):
        AstronInternalRepository.__init__(self, baseChannel, serverId=serverId, dcFileNames=dcFileNames,
                                          dcSuffix=dcSuffix, connectMethod=connectMethod, threadedNet=threadedNet)

    def handleConnected(self):
        AstronInternalRepository.handleConnected(self)

    def getAccountIdFromSender(self):
        return (self.getMsgSender() >> 32) & 0xFFFFFFFF

    def getAvatarIdFromSender(self):
        return self.getMsgSender() & 0xFFFFFFFF

    def sendSetZone(self, distObj, zoneId):
        distObj.setLocation(distObj.parentId, zoneId)
        self.sendSetLocation(distObj, distObj.parentId, zoneId)

    def setAllowClientSend(self, avId, distObj, fieldNameList=[]):
        dg = PyDatagram()
        dg.addServerHeader(distObj.GetPuppetConnectionChannel(avId), self.ourChannel, CLIENTAGENT_SET_FIELDS_SENDABLE)
        fieldIds = []
        for fieldName in fieldNameList:
            field = distObj.dclass.getFieldByName(fieldName)
            if field:
                fieldIds.append(field.getNumber())

        dg.addUint32(distObj.getDoId())
        dg.addUint16(len(fieldIds))
        for fieldId in fieldIds:
            dg.addUint16(fieldId)

        self.send(dg)

    def createDgUpdateToDoId(self, dclassName, fieldName, doId, args,
                         channelId=None):
        """
        channelId can be used as a recipient if you want to bypass the normal
        airecv, ownrecv, broadcast, etc.  If you don't include a channelId
        or if channelId == doId, then the normal broadcast options will
        be used.

        This is just like sendUpdateToDoId, but just returns
        the datagram instead of immediately sending it.
        """
        result = None
        dclass=self.dclassesByName.get(dclassName+self.dcSuffix)
        assert dclass is not None
        if channelId is None:
            channelId=doId
        if dclass is not None:
            dg = dclass.aiFormatUpdate(
                    fieldName, doId, channelId, self.ourChannel, args)
            result = dg
        return result

    def addPostSocketClose(self, themessage):
        # Time to send a register for channel message to the msgDirector
        datagram = PyDatagram()
#        datagram.addServerControlHeader(CONTROL_ADD_POST_REMOVE)
        datagram.addInt8(1)
        datagram.addChannel(AIMsgTypes.CONTROL_MESSAGE)
        datagram.addUint16(MsgTypes.CONTROL_ADD_POST_REMOVE)

        datagram.addBlob(themessage.getMessage())
        self.send(datagram)

    def getSenderReturnChannel(self):
        return self.getMsgSender()

#from otp.ai.airepository 

    def sendUpdateToDoId(self, dclassName, fieldName, doId, args,
                         channelId=None):
        """
        channelId can be used as a recipient if you want to bypass the normal
        airecv, ownrecv, broadcast, etc.  If you don't include a channelId
        or if channelId == doId, then the normal broadcast options will
        be used.
        
        See Also: def queryObjectField
        """
        dclass=self.dclassesByName.get(dclassName+self.dcSuffix)
        assert dclass is not None
        if channelId is None:
            channelId=doId
        if dclass is not None:
            dg = dclass.aiFormatUpdate(
                    fieldName, doId, channelId, self.ourChannel, args)
            self.send(dg)

    def allocateContext(self):
        self.context+=1
        if self.context >= (1<<32):
            self.context=self.InitialContext
        return self.context
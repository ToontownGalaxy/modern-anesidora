from direct.directnotify import DirectNotifyGlobal

from otp.distributed.DistributedDirectoryAI import DistributedDirectoryAI
from otp.distributed.OtpDoGlobals import *
from otp.distributed import OtpDoGlobals
from toontown.distributed.ToontownInternalRepository import ToontownInternalRepository
from panda3d.core import *
from direct.showbase.PythonUtil import *
from otp.ai.AIMsgTypes import *
from otp.ai import TimeManagerAI
from otp.friends.AvatarFriendsManagerUD import AvatarFriendsManagerUD
from toontown.uberdog.DistributedDeliveryManagerUD import DistributedDeliveryManagerUD
from toontown.uberdog.DistributedMailManagerUD import DistributedMailManagerUD
from toontown.parties import ToontownTimeManager
#from toontown.rpc.RATManagerUD import RATManagerUD #TODO
#from toontown.rpc.AwardManagerUD import AwardManagerUD #TODO
from toontown.uberdog import TTSpeedchatRelayUD
from toontown.uberdog import DistributedInGameNewsMgrUD
from toontown.uberdog import DistributedCpuInfoMgrUD
from direct.distributed.PyDatagram import PyDatagram

from otp.uberdog.RejectCode import RejectCode
#from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from toontown.coderedemption import TTCodeRedemptionConsts

import time

class ToontownUDRepository(ToontownInternalRepository):
    InitialContext = 100000

    notify = DirectNotifyGlobal.directNotify.newCategory('ToontownUDRepository')

    def __init__(self, baseChannel, serverId):
        ToontownInternalRepository.__init__(self, baseChannel, serverId, dcSuffix='UD')
        self.astronLoginManager = None
        # TODO: The UD needs to know server time, but perhaps this isn't
        # the place to do this? -SG-SLWP
        self.toontownTimeManager = ToontownTimeManager.ToontownTimeManager()
        self.toontownTimeManager.updateLoginTimes(time.time(), time.time(), globalClock.getRealTime())
       # def isManagerFor(name):
         #   return len(uber.objectNames) == 0 or name in uber.objectNames
        #self.isFriendsManager = False # latest from Ian this should not run anymore
        #self.isFriendsManager = isManagerFor('friends')
        #self.isSpeedchatRelay = isManagerFor('speedchatRelay')
        #self.isGiftingManager = isManagerFor('gifting')
        #self.isMailManager = False # isManagerFor('mail')
        #self.isPartyManager = isManagerFor('party')
       # self.isRATManager = False # isManagerFor('RAT')
       # self.isAwardManager = False #isManagerFor('award')
       # self.isCodeRedemptionManager = isManagerFor('coderedemption')
       # self.isInGameNewsMgr = isManagerFor('ingamenews')
       # self.isCpuInfoMgr = isManagerFor('cpuinfo')
       # self.isRandomSourceManager = False # isManagerFor('randomsource')
        self.context=self.InitialContext
        self.contextToClassName={}

      # We're responsible for keeping track of who's online with which avatar
        self.onlineAccountDetails = {}
        self.onlineAvatars = {}
        self.onlinePlayers = {}
        self.allowUnfilteredChat = config.GetBool('want-unfiltered-chat', 1)
        uber.allowUnfilteredChat = self.allowUnfilteredChat
        uber.config = config
        uber.bwDictPath = ''
        self.pending={}
        self.doId2doCache={}
        uber.mysqlhost = 'localhost'
        uber.codeRedemptionMgrHTTPListenPort = uber.config.GetInt('code-redemption-port', 8998)
        uber.crDbName = uber.config.GetString("tt-code-db-name", TTCodeRedemptionConsts.DefaultDbName)
        uber.inGameNewsMgrHTTPListenPort = uber.config.GetInt("in-game-news-port",8889)

        uber.cpuInfoMgrHTTPListenPort = uber.config.GetInt("security_ban_mgr_port",8892)

        if hasattr(self, 'setVerbose'):
            if self.config.GetBool('verbose-uberrepository'):
                self.setVerbose(1)
        self.ttFriendsManager = None 
        
    def handleConnected(self):
        ToontownInternalRepository.handleConnected(self)

        # Create our root object.
        self.notify.info('Creating root object (%d)...' % self.getGameDoId())
        rootObj = DistributedDirectoryAI(self)
        rootObj.generateWithRequiredAndId(self.getGameDoId(), 0, 0)

        # Create our global objects.
        self.notify.info('Creating global objects...')
        self.createGlobals()

        self.notify.info('UberDOG server is ready.')

    def createGlobals(self):
        # Create our Astron login manager...
        self.astronLoginManager = self.generateGlobalObject(OTP_DO_ID_ASTRON_LOGIN_MANAGER, 'AstronLoginManager')

        #self.queryObjectAll(self.serverId)

        #self.playerFriendsManager = self.generateGlobalObject(
         #       OtpDoGlobals.OTP_DO_ID_PLAYER_FRIENDS_MANAGER,
          #      "TTPlayerFriendsManager")
          #we dont need player friends

        self.speedchatRelay = self.generateGlobalObject(
                OtpDoGlobals.OTP_DO_ID_TOONTOWN_SPEEDCHAT_RELAY,
                "TTSpeedchatRelay")

        self.deliveryManager = self.generateGlobalObject(
                OtpDoGlobals.OTP_DO_ID_TOONTOWN_DELIVERY_MANAGER,
                "DistributedDeliveryManager")

        self.mailManager = self.generateGlobalObject(
                OtpDoGlobals.OTP_DO_ID_TOONTOWN_MAIL_MANAGER,
                "DistributedMailManager")

        self.partyManager = self.generateGlobalObject(
                OtpDoGlobals.OTP_DO_ID_TOONTOWN_PARTY_MANAGER,
                "DistributedPartyManager")

        self.dataStoreManager = self.generateGlobalObject(
                OtpDoGlobals.OTP_DO_ID_TOONTOWN_TEMP_STORE_MANAGER,
                "DistributedDataStoreManager")
        self.ttFriendsManager = self.generateGlobalObject(OTP_DO_ID_TT_FRIENDS_MANAGER, 'TTFriendsManager')

#TODO get ratmanager and awardmanager working
      #  if self.isRATManager:
       #     self.RATManager = self.generateGlobalObject(
        #        OtpDoGlobals.OTP_DO_ID_TOONTOWN_RAT_MANAGER,
         #       "RATManager")

        #if self.isAwardManager:
         #   self.awardManager = self.generateGlobalObject(
          #      OtpDoGlobals.OTP_DO_ID_TOONTOWN_AWARD_MANAGER,
           #     "AwardManager")

        if config.GetBool('want-code-redemption', 1):
            self.codeRedemptionManager = self.generateGlobalObject(
                    OtpDoGlobals.OTP_DO_ID_TOONTOWN_CODE_REDEMPTION_MANAGER,
                    "TTCodeRedemptionMgr")

        self.inGameNewsMgr = self.generateGlobalObject(
                OtpDoGlobals.OTP_DO_ID_TOONTOWN_IN_GAME_NEWS_MANAGER,
                "DistributedInGameNewsMgr")

        self.cpuInfoMgr = self.generateGlobalObject(
                OtpDoGlobals.OTP_DO_ID_TOONTOWN_CPU_INFO_MANAGER,
                "DistributedCpuInfoMgr")

        self.randomSourceManager = self.generateGlobalObject(
                OtpDoGlobals.OTP_DO_ID_TOONTOWN_NON_REPEATABLE_RANDOM_SOURCE,
                "NonRepeatableRandomSource")

        self.chatRouter = self.generateGlobalObject(OtpDoGlobals.OTP_DO_ID_CHAT_ROUTER, 'ChatRouter')

    def getDatabaseIdForClassName(self, className):
        return DatabaseIdFromClassName.get(
            className, DefaultDatabaseChannelId)


    if __debug__:
        def status(self):
            if self.isGiftingManager:
                print("deliveryManager is", self.deliveryManager)
            if self.isFriendsManager:
                print("playerFriendsManager is ",self.playerFriendsManager)

    def allocateContext(self):
        self.context+=1
        if self.context >= (1<<32):
            self.context=self.InitialContext
        return self.context

    def dispatchUpdateToDoId(self, dclassName, fieldName, doId, args, channelId=None):
        # dispatch immediately to local object if it's local, otherwise send
        # it over the wire
        obj = self.doId2do.get(doId)
        if obj is not None:
            assert obj.__class__.__name__ == (dclassName + self.dcSuffix)
            method = getattr(obj, fieldName)
            method(*args)
        else:
            self.sendUpdateToDoId(dclassName, fieldName, doId, args, channelId)

    def dispatchUpdateToGlobalDoId(self, dclassName, fieldName, doId, args):
        # dispatch immediately to local object if it's local, otherwise send
        # it over the wire
        obj = self.doId2do.get(doId)
        if obj is not None:
            assert obj.__class__.__name__ == dclassName
            method = getattr(obj, fieldName)
            method(*args)
        else:
            self.sendUpdateToGlobalDoId(dclassName, fieldName, doId, args)

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def accountOnline(self, accountId, accountDetailRecord):
        self.writeServerEvent('accountOnline', accountId, '')
        self.onlineAccountDetails[accountId] = accountDetailRecord
        messenger.send('accountOnline', [accountId])
        pass

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def accountOffline(self, accountId):
        self.writeServerEvent('accountOffline', accountId, '')
        self.onlineAccountDetails.pop(accountId, None)
        self.onlinePlayers.pop(accountId, None)
        messenger.send('accountOffline', [accountId])
        pass

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def getAccountDetails(self, accountId):
        return self.onlineAccountDetails.get(accountId)

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def isAccountOnline(self, accountId):
        return accountId in self.onlineAccountDetails

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def isAvatarOnline(self, avatarId):
        return avatarId in self.onlineAvatars

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def getAvatarAccountOnline(self, avatarId):
        return self.onlineAvatars.get(avatarId, 0)

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def getAccountOnlineAvatar(self, accountId):
        return self.onlinePlayers.get(accountId, 0)

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def getAccountDetails(self, accountId):
        return self.onlineAccountDetails.get(accountId)

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def isAccountOnline(self, accountId):
        return accountId in self.onlineAccountDetails

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def isAvatarOnline(self, avatarId):
        return avatarId in self.onlineAvatars

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def getAvatarAccountOnline(self, avatarId):
        return self.onlineAvatars.get(avatarId, 0)

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def getAccountOnlineAvatar(self, accountId):
        return self.onlinePlayers.get(accountId, 0)

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def checkAccountId(self, accountId):
        if not accountId:
            # SUSPICIOUS
            self.notify.warning("Bogus accountId: %s" % accountId)
            self.writeServerEvent('suspicious', accountId, 'bogus accountId in OtpAvatarManagerUD')
        elif not self.isAccountOnline(accountId):
            # SUSPICIOUS
            self.notify.warning("Got request from account not online: %s" % accountId)
            self.writeServerEvent('suspicious', accountId, 'request from offline account in OtpAvatarManagerUD')
        else:
            # Everything checks out
            return True
        return False

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def avatarOnline(self, avatarId, avatarType, accountId, playerName, playerNameApproved,
                     openChatEnabled, createFriendsWithChat, chatCodeCreation):
        self.writeServerEvent('avatarOnline', avatarId, '%s|%s|%s|%s|%s|%s' % (
            accountId, playerName, playerNameApproved, openChatEnabled,
            createFriendsWithChat, chatCodeCreation))

        self.onlineAvatars[avatarId] = accountId
        self.onlinePlayers[accountId] = avatarId

        simpleInfo = [avatarId, avatarType]
        fullInfo = [avatarId,
                    accountId,
                    playerName,
                    playerNameApproved,
                    openChatEnabled,
                    createFriendsWithChat,
                    chatCodeCreation]

        # necessary for local UD manager objects
        messenger.send("avatarOnline", simpleInfo)
        messenger.send("avatarOnlinePlusAccountInfo", fullInfo)
        pass

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def avatarOffline(self, accountId, avatarId):
        self.writeServerEvent('avatarOffline', avatarId, '')

        self.onlinePlayers.pop(accountId, None)
        self.onlineAvatars.pop(avatarId, None)

        # necessary for local UD manager objects
        messenger.send("avatarOffline", [avatarId])
        pass

    def setConnectionName(self):
        #TODO
        pass

    def setConnectionUrl(self):
        #TODO
        pass

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def queryObjectFieldId(self, doId, fieldId, context=0):
        """
        Get a one-time snapshot look at the object.
        """
        assert self.notify.debugStateCall(self)
        # Create a message
        datagram = PyDatagram()
        datagram.addServerHeader(
            doId, self.ourChannel, STATESERVER_OBJECT_QUERY_FIELD)           
        datagram.addUint32(doId)
        datagram.addUint16(fieldId)
        # A context that can be used to index the response if needed
        datagram.addUint32(context)
        self.send(datagram)
        # Make sure the message gets there.
        self.flush()

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def queryObjectFieldIds(self, doId, fieldIds, context=0):
        """
        Get a one-time snapshot look at the object.
        Query multiple field IDs from the same object.
        """
        assert self.notify.debugStateCall(self)
        # Create a message
        datagram = PyDatagram()
        datagram.addServerHeader(
            doId, self.ourChannel, STATESERVER_OBJECT_QUERY_FIELDS)           
        datagram.addUint32(doId)
        datagram.addUint32(context)
        for x in fieldIds:
            datagram.addUint16(x)
        self.send(datagram)
        # Make sure the message gets there.
        self.flush()

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def queryObjectStringFieldIds(self, dbId, objString, fieldIds, context=0):
        """
        Get a one-time snapshot look at the object.
        Query multiple field IDs from the same object, by object string.
        """
        assert self.notify.debugStateCall(self)
        # Create a message
        dg = PyDatagram()
        dg.addServerHeader(
            dbId, self.ourChannel, STATESERVER_OBJECT_QUERY_FIELDS_STRING)           
        dg.addString(objString)
        dg.addUint32(context)
        for x in fieldIds:
            dg.addUint16(x)
        self.send(dg)
        # Make sure the message gets there.
        self.flush()

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def queryObjectStringFields(
            self, dbId, dclassName, objString, fieldNames, context=0):
        """
        Get a one-time snapshot look at the object.
        Query multiple field names from the same object, by object string.
        """
        assert self.notify.debugStateCall(self)
        assert len(dclassName) > 0
        for fn in fieldNames:
            assert len(fn) > 0
        dclass = self.dclassesByName.get(dclassName)
        assert dclass is not None
        if not dclass:
            self.notify.error(
                "queryObjectStringFields invalid dclassName %s"%(dclassName))
            return
        if dclass is not None:
            fieldIds = []
            for fn in fieldNames:
                id = dclass.getFieldByName(fn).getNumber()
                assert id
                if not id:
                    self.notify.error(
                        "queryObjectStrongFields invalid field %s, %s"%(doId,fn))
                    return
                fieldIds.append(id)
            self.queryObjectStringFieldIds(dbId,objString,fieldIds,context)

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def queryObjectField(self, dclassName, fieldName, doId, context=0):
        """
        See Also: def sendUpdateToDoId
        """
        assert self.notify.debugStateCall(self)
        assert len(dclassName) > 0
        assert len(fieldName) > 0
        assert doId > 0
        dclass = self.dclassesByName.get(dclassName)
        assert dclass is not None
        if not dclass:
            self.notify.error(
                "queryObjectField invalid dclassName %s, %s"%(doId, fieldName))
            return
        if dclass is not None:
            fieldId = dclass.getFieldByName(fieldName).getNumber()
            assert fieldId # is 0 a valid value?
            if not fieldId:
                self.notify.error(
                    "queryObjectField invalid field %s, %s"%(doId, fieldName))
                return
            self.queryObjectFieldId(doId, fieldId, context)

    @report(types = ['args'], dConfigParam = 'avatarmgr')
    def queryObjectFields(self, dclassName, fieldNames, doId, context=0):
        """
        See Also: def sendUpdateToDoId
        """
        assert self.notify.debugStateCall(self)
        assert len(dclassName) > 0
        assert len(fieldNames) > 0
        for fieldName in fieldNames:
            assert len(fieldName) > 0
        assert doId > 0
        dclass = self.dclassesByName.get(dclassName)
        assert dclass is not None
        if not dclass:
            self.notify.error(
                "queryObjectField invalid dclassName %s, %s"%(doId, fieldName))
            return
        if dclass is not None:
            fieldIds = [dclass.getFieldByName(fieldName).getNumber() \
                        for fieldName in fieldNames]
            # is 0 a valid value?
            assert 0 not in fieldIds
            if 0 not in fieldIds:
                self.queryObjectFieldIds(doId, fieldIds, context)
            else:
                assert self.notify.error(
                        "queryObjectFields invalid field in %s, %s"%(doId,fieldNames))
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.distributed.PyDatagram import *
from direct.fsm.FSM import FSM
import time

#  FSMS 
class OperationFSM(FSM):

    def __init__(self, mgr, air, senderId, targetId=None, callback=None):
        FSM.__init__(self, 'OperationFSM-%s' % senderId)
        self.mgr = mgr
        self.air = air
        self.sender = senderId
        self.result = None
        self.target = targetId
        self.callback = callback

    def enterOff(self):
        if self.callback:
            if self.result is not None:
                self.callback(self.sender, self.result)
            else:
                self.callback()

        if self in self.mgr.operations:
            self.mgr.operations.remove(self)

    def enterError(self, message=None):
        self.mgr.notify.warning("An error has occurred in a '%s'. Message: %s" %
            (type(self).__name__, message) )
        if self.sender in self.mgr.operations:
            del self.mgr.operations[self.sender]


# Friends list 
class FriendsListOperation(OperationFSM):

    def enterStart(self):
        self.air.dbInterface.queryObject(self.air.dbId, self.sender,
            self.handleRetrieveSender)

    def handleRetrieveSender(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.demand('Error', 'Distributed Class was not a Toon.')
            return

        self.demand('Retrieved', fields['setFriendsList'][0])

    def enterRetrieved(self, friendsList):
        self.friendsList = friendsList
        if len(self.friendsList) <= 0:
            self.result = []
            self.demand('Off')
            return

        self.friendIndex = 0
        self.actualFriendsList = []

        self.air.dbInterface.queryObject(self.air.dbId, self.friendsList[0],
            self.addFriend)

    def addFriend(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.demand('Error', 'Friend was not a Toon')
            return
        friendId = self.friendsList[self.friendIndex]
        self.actualFriendsList.append([friendId, fields['setName'][0],
            fields['setDNAString'][0], fields['setPetId'][0]])

        if len(self.actualFriendsList) >= len(self.friendsList):
            self.result = self.actualFriendsList
            self.demand('Off')
            return

        self.friendIndex += 1
        self.air.dbInterface.queryObject(self.air.dbId,
            self.friendsList[self.friendIndex], self.addFriend)


# Remove Friends
class RemoveFriendOperation(OperationFSM):

    def __init__(self, mgr, air, senderId, targetId=None, callback=None, alert=False):
        OperationFSM.__init__(self, mgr, air, senderId, targetId, callback)
        self.alert = alert

    def enterStart(self):
        self.air.dbInterface.queryObject(self.air.dbId, self.sender,
            self.handleRetrieve)

    def handleRetrieve(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.demand('Error', 'Distributed Class was not a Toon.')
            return

        self.demand('Retrieved', fields['setFriendsList'][0], fields['setTrueFriends'][0])

    def enterRetrieved(self, friends, trueFriends):
        if self.target in friends:
            friends.remove(self.target)
        if self.target in trueFriends:
            trueFriends.remove(self.target)
        if self.sender in self.mgr.onlineToons:
            dg = self.air.dclassesByName['DistributedToonUD'].aiFormatUpdate(
                    'setFriendsList', self.sender, self.sender,
                    self.air.ourChannel, [friends])
            self.air.send(dg)
            if self.alert:
                dg = self.air.dclassesByName['DistributedToonUD'].aiFormatUpdate(
                     'friendsNotify', self.sender, self.sender,
                     self.air.ourChannel, [self.target, 1])
                self.air.send(dg)
            self.demand('Off')
            return

        self.air.dbInterface.updateObject(self.air.dbId, self.sender,
            self.air.dclassesByName['DistributedToonUD'],
            {'setFriendsList' : [friends], 'setTrueFriends': [trueFriends]})
        self.demand('Off')

# Clear the friends List
class ClearListOperation(OperationFSM):

    def enterStart(self):
        self.air.dbInterface.queryObject(self.air.dbId, self.sender,
            self.handleRetrieved)

    def handleRetrieved(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.demand('Error', 'Distributed Class was not a Toon.')
            return
        self.demand('Retrieved', fields['setFriendsList'][0])

    def enterRetrieved(self, friends):
        for friend in friends:
            newOperation = RemoveFriendOperation(self.mgr, self.air, friend,
                targetId=self.sender, alert=True)
            self.mgr.operations.append(newOperation)
            newOperation.demand('Start')
        self.demand('Off')

# TTFriendsManager class

class TTFriendsManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('TTFriendsManagerUD')

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)

        self.onlineFriends = []
        self.teleportRequests = {}
        self.whisperRequests = {}
        self.toonToData = {}
        self.operations = []
        self.delay = 1.0


    def requestFriends(self):
        avId = self.air.getAvatarIdFromSender()
        newOperation = FriendsListOperation(self, self.air, avId,
            callback = self.sendFriendsList)
        self.operations.append(newOperation)
        newOperation.demand('Start')

    def sendFriendsList(self, sender, friendsList):
        self.sendUpdateToAvatarId(sender, 'friendsList', [friendsList])
        if sender not in self.onlineFriends:
            self.friendOnline(sender, friendsList)


    def deleteFriend(self, friendId):
        avId = self.air.getAvatarIdFromSender()

        # Sender remove Friend
        newOperation = RemoveFriendOperation(self, self.air, avId, friendId)
        self.operations.append(newOperation)
        newOperation.demand('Start')

        # Friend remove Sender
        newOperation = RemoveFriendOperation(self, self.air, friendId, avId,
            alert=True)
        self.operations.append(newOperation)
        newOperation.demand('Start')

    # -- Avatar Info --
    def getToonDetails(self, friendId):
        senderId = self.air.getAvatarIdFromSender()
        def handleToon(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                return
            inventory = fields['setInventory'][0]
            trackAccess = fields['setTrackAccess'][0]
            hp = fields['setHp'][0]
            maxHp = fields['setMaxHp'][0]
            defaultShard = fields['setDefaultShard'][0]
            lastHood = fields['setLastHood'][0]
            dnaString =  fields['setDNAString'][0]
            experience = fields['setExperience'][0]
            trackBonusLevel = fields['setTrackBonusLevel'][0]
            npcFriends = fields['setNPCFriendsDict'][0]
            self.sendUpdateToAvatarId(senderId, 'friendDetails', [friendId, inventory, trackAccess, hp, maxHp, defaultShard, lastHood, dnaString, experience, trackBonusLevel, npcFriends])
        self.air.dbInterface.queryObject(self.air.dbId, friendId, handleToon)
    
    def getPetInfo(self, petId):
        senderId = self.air.getAvatarIdFromSender()
        def handlePet(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedPetAI']:
                return
            dna = [fields.get(x, [0])[0] for x in ("setHead", "setEars", "setNose", "setTail", "setBodyTexture", "setColor",
                                                 "setColorScale", "setEyeColor", "setGender")]
            moods = [fields.get(x, [0])[0] for x in ("setBoredom", "setRestlessness", "setPlayfulness", "setLoneliness",
                                                   "setSadness", "setAffection", "setHunger", "setConfusion", "setExcitement",
                                                   "setFatigue", "setAnger", "setSurprise")]
            traits = [fields.get(x, [0])[0] for x in ("setForgetfulness", "setBoredomThreshold", "setRestlessnessThreshold",
                                                    "setPlayfulnessThreshold", "setLonelinessThreshold", "setSadnessThreshold",
                                                    "setFatigueThreshold", "setHungerThreshold", "setConfusionThreshold",
                                                    "setExcitementThreshold", "setAngerThreshold", "setSurpriseThreshold",
                                                    "setAffectionThreshold")]
            self.sendUpdateToAvatarId(senderId, 'petInfo', [petId, fields.get("setOwnerId", [0])[0], fields.get("setPetName", ["???"])[0],
                                                               fields.get("setTraitSeed", [0])[0], fields.get("setSafeZone", [0])[0],
                                                               traits, moods, dna, fields.get("setLastSeenTimestamp", [0])[0]])
        self.air.dbInterface.queryObject(self.air.dbId, petId, handlePet)


    def friendOnline(self, toonId, friendsList):
        if toonId not in self.onlineFriends:
            self.onlineFriends.append(toonId)

        channel = self.GetPuppetConnectionChannel(toonId)
        dgcleanup = self.dclass.aiFormatUpdate('goingOffline', self.doId, self.doId, self.air.ourChannel, [toonId])
        dg = PyDatagram()
        dg.addServerHeader(channel, self.air.ourChannel, CLIENTAGENT_ADD_POST_REMOVE)
        dg.addBlob(dgcleanup.getMessage())
        self.air.send(dg)

        for friend in friendsList:
            friendId = friend[0]
            if friendId in self.onlineFriends:
                self.sendUpdateToAvatarId(toonId, 'friendIsOnline', [friendId])
            self.sendUpdateToAvatarId(friendId, 'friendIsOnline', [toonId])

    def goingOffline(self, friendId):
        self.friendOffline(friendId)

    def friendOffline(self, friendId):
        if friendId not in self.onlineFriends:
            return
        def handleToon(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                return
            friendsList = fields['setFriendsList'][0]
            for friend in friendsList:
                if friend in self.onlineFriends:
                    self.sendUpdateToAvatarId(friend, 'friendIsOffline', [friendId])
            if friendId in self.onlineFriends:
                self.onlineFriends.remove(friendId)
            if friendId in self.toonToData:
                del self.toonToData[friendId]
        self.air.dbInterface.queryObject(self.air.dbId, friendId, handleToon)

    # -- Clear List --
    def clearList(self, id):
        newOperation = ClearListOperation(self, self.air, id)
        self.operations.append(newOperation)
        newOperation.demand('Start')

    # -- Teleport and Whispers --
    def routeTeleportQuery(self, id):
        senderId = self.air.getAvatarIdFromSender()
        if senderId in self.teleportRequests.values():
            return
        self.teleportRequests[senderId] = id
        self.sendUpdateToAvatarId(id, 'teleportQuery', [senderId])
        taskMgr.doMethodLater(5, self.giveUpTeleportQuery, 'tp-query-timeout-%d' % senderId, extraArgs=[senderId, id])

    def giveUpTeleportQuery(self, senderId, toId):
        if senderId in self.teleportRequests:
            del self.teleportRequests[senderId]
            self.sendUpdateToAvatarId(senderId, 'setTeleportResponse', [toId, 0, 0, 0, 0])
            self.notify.warning('Teleport request that was sent by %d to %d timed out.' % (senderId, toId))

    def teleportResponse(self, id, available, shardId, hoodId, zoneId):
        senderId = self.air.getAvatarIdFromSender()

        # We got the query response, so no need to give up!
        if taskMgr.hasTaskNamed('tp-query-timeout-%d' % id):
            taskMgr.remove('tp-query-timeout-%d' % id)

        if id not in self.teleportRequests:
            return
        if self.teleportRequests.get(id) != senderId:
            self.air.writeServerEvent('suspicious', senderId, "toon tried to send a teleportResponse for a query that isn't theirs!")
            return
        self.sendUpdateToAvatarId(id, 'setTeleportResponse', [senderId, available, shardId, hoodId, zoneId])
        del self.teleportRequests[id]

    def whisperSCTo(self, id, msgIndex):
        senderId = self.air.getAvatarIdFromSender()
        currStamp = time.time()
        if senderId in self.whisperRequests:
            elapsed = currStamp - self.whisperRequests[senderId]
            if elapsed < self.delay:
                self.whisperRequests[senderId] = currStamp
                return
        self.whisperRequests[senderId] = currStamp
        self.sendUpdateToAvatarId(id, 'setWhisperSCFrom', [senderId, msgIndex])

    def whisperSCCustomTo(self, id, msgIndex):
        senderId = self.air.getAvatarIdFromSender()
        currStamp = time.time()
        if senderId in self.whisperRequests:
            elapsed = currStamp - self.whisperRequests[senderId]
            if elapsed < self.delay:
                self.whisperRequests[senderId] = currStamp
                return
        self.whisperRequests[senderId] = currStamp
        self.sendUpdateToAvatarId(id, 'setWhisperSCCustomFrom', [senderId, msgIndex])

    def whisperSCEmoteTo(self, id, msgIndex):
        senderId = self.air.getAvatarIdFromSender()
        currStamp = time.time()
        if senderId in self.whisperRequests:
            elapsed = currStamp - self.whisperRequests[senderId]
            if elapsed < self.delay:
                self.whisperRequests[senderId] = currStamp
                return
        self.whisperRequests[senderId] = currStamp
        self.sendUpdateToAvatarId(id, 'setWhisperSCEmoteFrom', [senderId, msgIndex])


    # -- Routes --
    def battleSOS(self, id):
        requester = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(id, 'setBattleSOS', [requester])

    def teleportGiveup(self, id):
        requester = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(id, 'setTeleportGiveup', [requester])

    def whisperSCToontaskTo(self, id, taskId, toNpcId, toonProgress, msgIndex):
        requester = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(id, 'setWhisperSCToontaskFrom', [requester,
            taskId, toNpcId, toonProgress, msgIndex]
        )

    def sleepAutoReply(self, id):
        requester = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(id, 'setSleepAutoReply', [requester])

    def getFriendAccess(self, friendId):
        return self.toonToData.get(friendId, {}).get('access', 0)
        
    def getFriendName(self, friendId):
        return self.toonToData.get(friendId, {}).get('name', '???')
        
    def getFriendAccountId(self, friendId):
        return self.toonToData.get(friendId, {}).get('accId', 0)

    def addFriendData(self, friendId, fields):
        data = {}
        data['name'] = fields['setName'][0]
        data['accId'] = fields.get('setDISLid', [0])[0]
        self.toonToData[friendId] = data
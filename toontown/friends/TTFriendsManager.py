from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from otp.otpbase import OTPLocalizer, OTPGlobals
from toontown.hood import ZoneUtil
import time

class TTFriendsManager(DistributedObjectGlobal):
    
    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)
        self.nextTeleportFail = 0
    
    def d_deleteFriend(self, friendId):
        self.sendUpdate('deleteFriend', [friendIdid])

    def d_requestFriends(self):
        self.sendUpdate('requestFriends', [])

    def friendsList(self, resp):
        base.cr.handleGetFriendsList(resp)

    def friendIsOnline(self, friendId):
        base.cr.handleFriendOnline(friendId)

    def friendIsOffline(self, friendId):
        base.cr.handleFriendOffline(friendId)

    def d_getToonDetails(self, toonId):
        self.sendUpdate('getToonDetails', [toonId])

    def friendDetails(self, friendId, inventory, trackAccess, hp, maxHp, defaultShard, lastHood, dnaString, experience, trackBonusLevel, NPCFriendsDict):
        fields = [
            ['setExperience' , experience],
            ['setTrackAccess' , trackAccess],
            ['setTrackBonusLevel' , trackBonusLevel],
            ['setInventory' , inventory],
            ['setHp' , hp],
            ['setMaxHp' , maxHp],
            ['setDefaultShard' , defaultShard],
            ['setLastHood' , lastHood],
            ['setDNAString' , dnaString],
            ['setNPCFriendsDict', NPCFriendsDict] 
        ]
        base.cr.n_handleGetAvatarDetailsResp(friendId, fields=fields)

    def d_getPetInfo(self, petId):
        self.sendUpdate('getPetInfo', [petId])

    def petInfo(self, petId, owner, name, seed, safezone, traits, moods, dna, lastSeen):
        fields = list(zip(("setHead", "setEars", "setNose", "setTail", "setBodyTexture", "setColor", "setColorScale", "setEyeColor", "setGender"), dna))
        fields.extend(zip(("setBoredom", "setRestlessness", "setPlayfulness", "setLoneliness",
                           "setSadness", "setAffection", "setHunger", "setConfusion", "setExcitement",
                           "setFatigue", "setAnger", "setSurprise"), moods))
        fields.extend(zip(("setForgetfulness", "setBoredomThreshold", "setRestlessnessThreshold",
                           "setPlayfulnessThreshold", "setLonelinessThreshold", "setSadnessThreshold",
                           "setFatigueThreshold", "setHungerThreshold", "setConfusionThreshold",
                           "setExcitementThreshold", "setAngerThreshold", "setSurpriseThreshold",
                           "setAffectionThreshold"), traits))
        fields.append(("setOwnerId", owner))
        fields.append(("setPetName", name))
        fields.append(("setTraitSeed", seed))
        fields.append(("setSafeZone", safezone))
        fields.append(("setLastSeenTimestamp", lastSeen))
        base.cr.n_handleGetAvatarDetailsResp(petId, fields=fields)

    def d_teleportQuery(self, id):
        self.sendUpdate('routeTeleportQuery', [id])

    def teleportQuery(self, id):
        if not hasattr(base, 'localAvatar'):
            self.sendUpdate('teleportResponse', [ id, 0, 0, 0, 0 ])
            return
        if not hasattr(base.localAvatar, 'ghostMode' or hasattr(base.localAvatar, 'getTeleportAvailable')):
            self.sendUpdate('teleportResponse', [ id, 0, 0, 0, 0 ])
            return


        avatar = base.cr.identifyFriend(id)

        if base.localAvatar.ghostMode or not base.localAvatar.getTeleportAvailable():
            if hasattr(avatar, 'getName'):
                base.localAvatar.setSystemMessage(id, OTPLocalizer.WhisperFailedVisit % avatar.getName())
            self.sendUpdate('teleportResponse', [ id, 0, 0, 0, 0 ])
            return

        hoodId = base.cr.playGame.getPlaceId()
        if hasattr(avatar, 'getName'):
            base.localAvatar.setSystemMessage(id, OTPLocalizer.WhisperComingToVisit % avatar.getName())
        self.sendUpdate('teleportResponse', [
            id,
            base.localAvatar.getTeleportAvailable(),
            base.localAvatar.defaultShard,
            hoodId,
            base.localAvatar.getZoneId()
        ])

    def d_teleportResponse(self, id, available, shardId, hoodId, zoneId):
        self.sendUpdate('teleportResponse', [id, available, shardId,
            hoodId, zoneId]
        )

    def setTeleportResponse(self, id, available, district, hoodId, zoneId):
        base.localAvatar.teleportResponse(id, available, district, hoodId, zoneId)

    def d_whisperSCTo(self, id, msgIndex):
        self.sendUpdate('whisperSCTo', [id, msgIndex])

    def setWhisperSCFrom(self, id, msgIndex):
        if not hasattr(base, 'localAvatar'):
            return
        if not hasattr(base.localAvatar, 'setWhisperSCFrom'):
            return
        base.localAvatar.setWhisperSCFrom(id, msgIndex)

    def d_whisperSCCustomTo(self, id, msgIndex):
        self.sendUpdate('whisperSCCustomTo', [id, msgIndex])

    def setWhisperSCCustomFrom(self, id, msgIndex):
        if not hasattr(base, 'localAvatar'):
            return
        if not hasattr(base.localAvatar, 'setWhisperSCCustomFrom'):
            return
        base.localAvatar.setWhisperSCCustomFrom(id, msgIndex)

    def d_whisperSCEmoteTo(self, id, emoteId):
        self.sendUpdate('whisperSCEmoteTo', [id, emoteId])

    def setWhisperSCEmoteFrom(self, id, emoteId):
        if not hasattr(base, 'localAvatar'):
            return
        if not hasattr(base.localAvatar, 'setWhisperSCEmoteFrom'):
            return
        base.localAvatar.setWhisperSCEmoteFrom(id, emoteId)



    def d_battleSOS(self, id):
        self.sendUpdate('battleSOS', [id])

    def setBattleSOS(self, id):
        base.localAvatar.battleSOS(id)

    def d_teleportGiveup(self, id):
        self.sendUpdate('teleportGiveup', [id])

    def setTeleportGiveup(self, id):
        base.localAvatar.teleportGiveup(id)

    def d_whisperSCToontaskTo(self, id, taskId, toNpcId, toonProgress, msgIndex):
        self.sendUpdate('whisperSCToontaskTo', [id, taskId, toNpcId,
            toonProgress, msgIndex]
        )

    def setWhisperSCToontaskFrom(self, id, taskId, toNpcId, toonProgress, msgIndex):
        base.localAvatar.setWhisperSCToontaskFrom(id, taskId, toNpcId,
            toonProgress, msgIndex
        )

    def d_sleepAutoReply(self, id):
        self.sendUpdate('sleepAutoReply', [id])

    def setSleepAutoReply(self, id):
        base.localAvatar.setSleepAutoReply(id)
from otp.ai.AIBaseGlobal import *
from pandac.PandaModules import *
from direct.showbase import PythonUtil
from direct.distributed import DistributedObjectAI
from direct.directnotify import DirectNotifyGlobal
from direct.showbase.PythonUtil import Functor
from . import DistributedEstateAI
from direct.task.Task import Task
from . import HouseGlobals
import random
import functools
from direct.fsm.FSM import FSM
from toontown.toon import ToonDNA
from toontown.estate.DistributedHouseAI import DistributedHouseAI
from toontown.estate.GardenManagerAI import GardenManagerAI

#Other classes from toontown school house
class LoadHouseOperation(FSM):
    def __init__(self, mgr, estate, index, avatar, callback):
        FSM.__init__(self, 'LoadHouseOperation')
        self.mgr = mgr
        self.estate = estate
        self.index = index
        self.avatar = avatar
        self.callback = callback
        self.done = False
        self.houseId = None
        self.house = None
        self.gender = None

    def start(self):
        # We have a few different cases here:
        if self.avatar is None:
            # Case #1: There isn't an avatar in that estate slot. Make a blank house.
            # Because this state completes so fast, we'll use taskMgr to delay
            # it until the next iteration. This solves reentrancy problems.
            taskMgr.doMethodLater(0.0, self.demand, 'makeBlankHouse-%s' % id(self), extraArgs=['MakeBlankHouse'])
            return

        style = ToonDNA.ToonDNA()
        style.makeFromNetString(self.avatar.get('setDNAString')[0])
        self.houseId = self.avatar.get('setHouseId', [0])[0]
        self.gender = style.gender
        if self.houseId == 0:
            # Case #2: There is an avatar, but no setHouseId. Make a new house:
            self.demand('CreateHouse')
        else:
            # Case #3: Avatar with a setHouseId. Load it:
            self.demand('LoadHouse')

    def enterMakeBlankHouse(self):
        self.house = DistributedHouseAI(self.mgr.air)
        self.house.setHousePos(self.index)
        self.house.setColor(self.index)
        self.house.generateWithRequired(self.estate.zoneId)
        self.estate.houses[self.index] = self.house
        self.demand('Off')

    def enterCreateHouse(self):
        self.mgr.air.dbInterface.createObject(self.mgr.air.dbId, self.mgr.air.dclassesByName['DistributedHouseAI'],
                                              {'setName': [self.avatar['setName'][0]],
                                               'setAvatarId': [self.avatar['avId']]}, self.__handleHouseCreated)

    def __handleHouseCreated(self, houseId):
        if self.state != 'CreateHouse':
            # This operation was likely aborted.
            return

        # Update the avatar's houseId:
        av = self.mgr.air.doId2do.get(self.avatar['avId'])
        if av:
            av.b_setHouseId(houseId)
        else:
            self.mgr.air.dbInterface.updateObject(self.mgr.air.dbId, self.avatar['avId'],
                                                  self.mgr.air.dclassesByName['DistributedToonAI'],
                                                  {'setHouseId': [houseId]})

        self.houseId = houseId
        self.demand('LoadHouse')

    def enterLoadHouse(self):
        # Activate the house:
        self.mgr.air.sendActivate(self.houseId, self.mgr.air.districtId, self.estate.zoneId,
                                  self.mgr.air.dclassesByName['DistributedHouseAI'],
                                  {'setHousePos': [self.index],
                                   'setColor': [self.index],
                                   'setName': [self.avatar['setName'][0]],
                                   'setAvatarId': [self.avatar['avId']]})

        # Wait for the house to generate:
        self.acceptOnce('generate-%d' % self.houseId, self.__handleHouseGenerated)

    def __handleHouseGenerated(self, house):
        # The house will need to be able to reference
        # the estate for setting up gardens, so:
        house.estate = self.estate

        # Initialize our interior:
        house.interior.gender = self.gender
        #house.interior.start()

        self.house = house
        self.estate.houses[self.index] = self.house
        #if config.GetBool('want-gardening', True):
            #Have distributedestateai take care of it like tto
            #self.house.createGardenManager()

        self.demand('Off')

    def exitLoadHouse(self):
        self.ignore('generate-%d' % self.houseId)

    def enterOff(self):
        self.done = True
        self.callback(self.house)


class LoadEstateOperation(FSM):
    def __init__(self, mgr, callback):
        FSM.__init__(self, 'LoadEstateOperation')
        self.mgr = mgr
        self.callback = callback
        self.estate = None
        self.accId = None
        self.zoneId = None
        self.avIds = None
        self.avatars = None
        self.houseOperations = None
        self.petOperations = None

    def start(self, accId, zoneId):
        self.accId = accId
        self.zoneId = zoneId
        self.demand('QueryAccount')

    def enterQueryAccount(self):
        self.mgr.air.dbInterface.queryObject(self.mgr.air.dbId, self.accId, self.__handleQueryAccount)

    def __handleQueryAccount(self, dclass, fields):
        if self.state != 'QueryAccount':
            # This operation was likely aborted.
            return

        if dclass != self.mgr.air.dclassesByName['AccountAI']:
            self.mgr.notify.warning('Account %d has non-account dclass %d!' % (self.accId, dclass))
            self.demand('Failure')
            return

        self.accFields = fields
        self.estateId = fields.get('ESTATE_ID', 0)
        self.demand('QueryAvatars')

    def enterQueryAvatars(self):
        self.avIds = self.accFields.get('ACCOUNT_AV_SET', [0] * 6)
        self.avatars = {}
        for index, avId in enumerate(self.avIds):
            if avId == 0:
                self.avatars[index] = None
                continue

            self.mgr.air.dbInterface.queryObject(self.mgr.air.dbId, avId,
                                                 functools.partial(self.__handleQueryAvatar, index=index))

    def __handleQueryAvatar(self, dclass, fields, index):
        if self.state != 'QueryAvatars':
            # This operation was likely aborted.
            return

        if dclass != self.mgr.air.dclassesByName['DistributedToonAI']:
            self.mgr.notify.warning(
                'Account %d has avatar %d with non-Toon dclass %d!' % (self.accId, self.avIds[index], dclass))
            self.demand('Failure')
            return

        fields['avId'] = self.avIds[index]
        self.avatars[index] = fields
        if len(self.avatars) == 6:
            self.__gotAllAvatars()

    def __gotAllAvatars(self):
        # We have all of our avatars, so now we can handle the estate.
        if self.estateId:
            # We already have an estate, so let's load that:
            self.demand('LoadEstate')
        else:
            # We don't yet have an estate, so let's make one:
            self.demand('CreateEstate')

    def enterCreateEstate(self):
        # Create a blank estate object:
        self.mgr.air.dbInterface.createObject(self.mgr.air.dbId, self.mgr.air.dclassesByName['DistributedEstateAI'], {},
                                              self.__handleEstateCreated)

    def __handleEstateCreated(self, estateId):
        if self.state != 'CreateEstate':
            # This operation was likely aborted.
            return

        self.estateId = estateId

        # Store the new estate object on our account:
        self.mgr.air.dbInterface.updateObject(self.mgr.air.dbId, self.accId, self.mgr.air.dclassesByName['AccountAI'],
                                              {'ESTATE_ID': estateId})

        self.demand('LoadEstate')

    def enterLoadEstate(self):
        # Set the estate fields:
        fields = {'setSlot%dToonId' % i: (avId,) for i, avId in enumerate(self.avIds)}

        # Activate the estate:
        self.mgr.air.sendActivate(self.estateId, self.mgr.air.districtId, self.zoneId,
                                  self.mgr.air.dclassesByName['DistributedEstateAI'], fields)

        # Wait for the estate to generate:
        self.acceptOnce('generate-%d' % self.estateId, self.__handleEstateGenerated)

    def __handleEstateGenerated(self, estate):
        # Get the estate:
        self.estate = estate

        # For keeping track of pets in this estate:
        self.estate.pets = []

        # Map the owner to the estate:
        ownerId = self.mgr.getOwnerFromZone(self.estate.zoneId)
        owner = self.mgr.air.doId2do.get(ownerId)
        if owner:
            self.mgr.toon2estate[owner] = self.estate

        # Set the estate's ID list:
        self.estate.b_setIdList(self.avIds)
        #start the garden process
        self.estate.gardenInit(self.avIds)


        # Load houses:
        self.demand('LoadHouses')

    def exitLoadEstate(self):
        self.ignore('generate-%d' % self.estateId)

    def enterLoadHouses(self):
        self.houseOperations = []
        for houseIndex in range(6):
            houseOperation = LoadHouseOperation(self.mgr, self.estate, houseIndex, self.avatars[houseIndex],
                                                self.__handleHouseLoaded)
            self.houseOperations.append(houseOperation)
            houseOperation.start()

    def __handleHouseLoaded(self, house):
        if self.state != 'LoadHouses':
            # We aren't loading houses, so we probably got cancelled. Therefore,
            # the only sensible thing to do is simply destroy the house.
            house.requestDelete()
            return

        # A house operation just finished! Let's see if all of them are done:
        if all(houseOperation.done for houseOperation in self.houseOperations):
            # Load our pets:
            self.demand('LoadPets')

    def enterLoadPets(self):
        self.petOperations = []
        for houseIndex in range(6):
            av = self.avatars[houseIndex]
            if av and av['setPetId'][0] != 0:
                petOperation = LoadPetOperation(self.mgr, self.estate, av, self.__handlePetLoaded)
                self.petOperations.append(petOperation)
                petOperation.start()

        if not self.petOperations:
            taskMgr.doMethodLater(0, lambda: self.demand('Finished'), 'no-pets', extraArgs=[])

    def __handlePetLoaded(self, pet):
        if self.state != 'LoadPets':
            pet.requestDelete()
            return

        # A pet operation just finished! Let's see if all of them are done:
        if all(petOperation.done for petOperation in self.petOperations):
            self.demand('Finished')

    def enterFinished(self):
        self.petOperations = []
        self.callback(True)

    def enterFailure(self):
        self.cancel()
        self.callback(False)

    def cancel(self):
        if self.estate:
            self.estate.destroy()
            self.estate = None

        self.demand('Off')


class LoadPetOperation(FSM):
    def __init__(self, mgr, estate, toon, callback):
        FSM.__init__(self, 'LoadPetFSM')
        self.mgr = mgr
        self.estate = estate
        self.toon = toon
        self.callback = callback
        self.done = False
        self.petId = 0

    def start(self):
        if type(self.toon) == dict:
            self.petId = self.toon['setPetId'][0]
        else:
            self.petId = self.toon.getPetId()

        if self.petId not in self.mgr.air.doId2do:
            self.mgr.air.sendActivate(self.petId, self.mgr.air.districtId, self.estate.zoneId)
            self.acceptOnce('generate-%d' % self.petId, self.__generated)
        else:
            self.__generated(self.mgr.air.doId2do[self.petId])

    def __generated(self, pet):
        self.pet = pet
        self.estate.pets.append(pet)
        self.demand('Off')

    def enterOff(self):
        self.ignore('generate-%d' % self.petId)
        self.done = True
        self.callback(self.pet)
TELEPORT_TO_OWNER_ONLY = 0

class EstateManagerAI(DistributedObjectAI.DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("EstateManagerAI")
    #notify.setDebug(True)

    def __init__(self, air):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.previousZone = None
        self.refCount = {}      # dict of lists containing avId's visiting an estate. keyed on owner's avId
        self.estateZone = {}    # dict of tuple of [zoneId, isOwner, userName] keyed on avId
        self.estate = {}        # dict of DistributedEstateAI's keyed on avId
        self.house = {}         # dict of lists of DistributedHouseAI's keyed on avId
        self.account2avId = {}  # mapping of userName to avId that created estate
        self.toBeDeleted = {}   # temporary list of av's to be deleted after a delay
        self.zone2owner = {}    # get the owner of a zone
        self.houseZone2estateZone = {}
        self.avId2pendingEnter = {} # table of avatars that are on their way to an estate
        self.petOperations  = []
        # Number of seconds between spontaneous heals
        self.healFrequency = 30 # seconds
        self.toon2estate = {}
        self.estate2toons = {}
        self.estate2timeout = {}
        self.zone2toons = {}


        self.randomGenerator = random.Random()

        return None

    #def delete(self):
        #self.notify.debug("BASE: delete: deleting EstateManagerAI object")
       # self.ignoreAll()
       # DistributedObjectAI.DistributedObjectAI.delete(self)
        #for estate in list(self.estate.values()):
         #   estate.requestDelete()
            # This automatically gets called by the server
            # estate.delete()
        #for hList in list(self.house.values()):
          #  for house in hList:
         #       house.requestDelete()
                # This automatically gets called by the server
                # house.delete()
        #del self.account2avId
        #del self.avId2pendingEnter
        #del self.refCount
        #del self.estateZone
        #del self.randomGenerator


    def getOwnerFromZone(self, zoneId):
        # returns doId of estate owner given a zoneId
        # zoneId can be estate exterior or house interior
        # returns None if zone not found
        estateZoneId = self.houseZone2estateZone.get(zoneId, zoneId)
        return self.zone2owner.get(estateZoneId)

    ## -----------------------------------------------------------
    ## Zone allocation and enter code
    ## -----------------------------------------------------------

    def getEstateZone(self, avId, name):
        #credit to Toontown School House
        # Thank you name, very cool!
        senderId = self.air.getAvatarIdFromSender()
        accId = self.air.getAccountIdFromSender()
        senderAv = self.air.doId2do.get(senderId)
        if not senderAv:
            self.air.writeServerEvent('suspicious', senderId, 'Sent getEstateZone() but not on district!')
            return

        # If an avId has been provided, then the sender wants to visit a friend.
        # In this case, we do not need to load the estate, we only need to check
        # to see if it already exists.
        if avId and avId != senderId:
            av = self.air.doId2do.get(avId)
            if av and av.dclass == self.air.dclassesByName['DistributedToonAI']:
                estate = self.toon2estate.get(av)
                if estate:
                    # Found an estate!
                    avId = estate.owner.doId
                    zoneId = estate.zoneId
                    self._mapToEstate(senderAv, estate)

                    # In case the sender is teleporting from their estate
                    # to another estate, we want to unload their estate.
                    self._unloadEstate(senderAv)

                    if senderAv and senderAv.getPetId() != 0:
                        pet = self.air.doId2do.get(senderAv.getPetId())
                        if pet:
                            self.acceptOnce(self.air.getAvatarExitEvent(senderAv.getPetId()), self.__handleLoadPet,
                                            extraArgs=[estate, senderAv])
                            pet.requestDelete()
                        else:
                            self.__handleLoadPet(estate, senderAv)

                    # Now we want to send the sender to the estate.
                    if hasattr(senderAv, 'enterEstate'):
                        senderAv.enterEstate(avId, zoneId)

                    self.sendUpdateToAvatarId(senderId, 'setEstateZone', [avId, zoneId])

            # We weren't able to find the given avId at an estate, that's pretty sad.
            self.sendUpdateToAvatarId(senderId, 'setEstateZone', [0, 0])
            return

        # Otherwise, the sender wants to go to their own estate.
        estate = getattr(senderAv, 'estate', None)
        if estate:
            # The sender already has an estate loaded, so let's send them there.
            self._mapToEstate(senderAv, senderAv.estate)

            if senderAv and senderAv.getPetId() != 0:
                pet = self.air.doId2do.get(senderAv.getPetId())
                if pet:
                    self.acceptOnce(self.air.getAvatarExitEvent(senderAv.getPetId()), self.__handleLoadPet,
                                    extraArgs=[estate, senderAv])
                    pet.requestDelete()
                else:
                    self.__handleLoadPet(estate, senderAv)

            if hasattr(senderAv, 'enterEstate'):
                senderAv.enterEstate(senderId, estate.zoneId)

            self.sendUpdateToAvatarId(senderId, 'setEstateZone', [senderId, estate.zoneId])

            # If a timeout is active, cancel it:
            if estate in self.estate2timeout:
                self.estate2timeout[estate].remove()
                del self.estate2timeout[estate]

            return

        if getattr(senderAv, 'loadEstateOperation', None):
            # We already have a loading operation underway; ignore this second
            # request since the first operation will setEstateZone() when it
            # finishes anyway.
            return

        zoneId = self.air.allocateZone()
        self.zone2owner[zoneId] = avId

        def estateLoaded(success):
            if success:
                senderAv.estate = senderAv.loadEstateOperation.estate
                senderAv.estate.owner = senderAv
                self._mapToEstate(senderAv, senderAv.estate)
                if hasattr(senderAv, 'enterEstate'):
                    senderAv.enterEstate(senderId, zoneId)

                self.sendUpdateToAvatarId(senderId, 'setEstateZone', [senderId, zoneId])
            else:
                # Estate loading failed. Sad!
                self.sendUpdateToAvatarId(senderId, 'setEstateZone', [0, 0])

                # Might as well free up the zoneId as well.
                self.air.deallocateZone(zoneId)
                del self.zone2owner[zoneId]

            senderAv.loadEstateOperation = None

        self.acceptOnce(self.air.getAvatarExitEvent(senderAv.doId), self.__handleUnexpectedExit, extraArgs=[senderAv])

        if senderAv and senderAv.getPetId() != 0:
            pet = self.air.doId2do.get(senderAv.getPetId())
            if pet:
                self.acceptOnce(self.air.getAvatarExitEvent(senderAv.getPetId()), self.__handleLoadEstate,
                                extraArgs=[senderAv, estateLoaded, accId, zoneId])
                pet.requestDelete()
                return
        self.__handleLoadEstate(senderAv, estateLoaded, accId, zoneId)

    def getAvEnterEvent(self):
        return 'avatarEnterEstate'

    def getAvExitEvent(self, avId=None):
        # listen for all exits or a particular exit
        # event args:
        #  if avId given: none
        #  if avId not given: avId, ownerId, zoneId
        if avId is None:
            return 'avatarExitEstate'
        else:
            return 'avatarExitEstate-%s' % avId

    def __enterEstate(self, avId, ownerId):
        # Tasks that should always get called when entering an estate

        # Handle unexpected exit
        self.acceptOnce(self.air.getAvatarExitEvent(avId),
                        self.__handleUnexpectedExit, extraArgs=[avId])

        # Toonup
        try:
            av = self.air.doId2do[avId]
            av.startToonUp(self.healFrequency)
        except:
            self.notify.info("couldn't start toonUpTask for av %s" % avId)

    def _listenForToonEnterEstate(self, avId, ownerId, zoneId):
        #self.notify.debug('_listenForToonEnterEstate(avId=%s, ownerId=%s, zoneId=%s)' % (avId, ownerId, zoneId))
        if avId in self.avId2pendingEnter:
            self.notify.warning(
                '_listenForToonEnterEstate(avId=%s, ownerId=%s, zoneId=%s): '
                '%s already in avId2pendingEnter. overwriting' % (
                avId, ownerId, zoneId, avId))
        self.avId2pendingEnter[avId] = (ownerId, zoneId)
        self.accept(DistributedObjectAI.
                    DistributedObjectAI.staticGetLogicalZoneChangeEvent(avId),
                    Functor(self._toonChangedZone, avId))

    def _toonLeftBeforeArrival(self, avId):
        #self.notify.debug('_toonLeftBeforeArrival(avId=%s)' % avId)
        if avId not in self.avId2pendingEnter:
            self.notify.warning('_toonLeftBeforeArrival: av %s not in table' %
                                avId)
            return
        ownerId, zoneId = self.avId2pendingEnter[avId]
        self.notify.warning(
            '_toonLeftBeforeArrival: av %s left server before arriving in '
            'estate (owner=%s, zone=%s)' % (avId, ownerId, zoneId))
        del self.avId2pendingEnter[avId]

    def _toonChangedZone(self, avId, newZoneId, oldZoneId):
        #self.notify.debug('_toonChangedZone(avId=%s, newZoneId=%s, oldZoneId=%s)' % (avId, newZoneId, oldZoneId))
        if avId not in self.avId2pendingEnter:
            self.notify.warning('_toonChangedZone: av %s not in table' %
                                avId)
            return
        av = self.air.doId2do.get(avId)
        if not av:
            self.notify.warning('_toonChangedZone(%s): av not present' % avId)
            return
        ownerId, estateZoneId = self.avId2pendingEnter[avId]
        estateZoneIds = self.getEstateZones(ownerId)
        if newZoneId in estateZoneIds:
            del self.avId2pendingEnter[avId]
            self.ignore(DistributedObjectAI.
                        DistributedObjectAI.staticGetLogicalZoneChangeEvent(avId))
            self.announceToonEnterEstate(avId, ownerId, estateZoneId)

    def announceToonEnterEstate(self, avId, ownerId, zoneId):
        """ announce to the rest of the system that a toon is entering
        an estate """
        EstateManagerAI.notify.debug('announceToonEnterEstate: %s %s %s' %
                                     (avId, ownerId, zoneId))
        messenger.send(self.getAvEnterEvent(), [avId, ownerId, zoneId])

    def announceToonExitEstate(self, avId, ownerId, zoneId):
        """ announce to the rest of the system that a toon is exiting
        an estate """
        EstateManagerAI.notify.debug('announceToonExitEstate: %s %s %s' %
                                     (avId, ownerId, zoneId))
        messenger.send(self.getAvExitEvent(avId))
        messenger.send(self.getAvExitEvent(), [avId, ownerId, zoneId])

    def getEstateZones(self, ownerId):
        # returns all zoneIds that belong to this estate
        zones = []
        estate = self.estate.get(ownerId)
        if estate is not None:
            if not hasattr(estate, 'zoneId'):
                self.notify.warning('getEstateZones: estate %s (owner %s) has no \'zoneId\'' %
                                    (estate.doId, ownerId))
            else:
                zones.append(estate.zoneId)
        houses = self.house.get(ownerId)
        if houses is not None:
            for house in houses:
                if not hasattr(house, 'interiorZoneId'):
                    self.notify.warning('getEstateZones: estate %s (owner %s) house has no interiorZoneId')
                else:
                    zones.append(house.interiorZoneId)
        return zones

    def getEstateHouseZones(self, ownerId):
        # returns all zoneIds that belong to houses on this estate
        zones = []
        houses = self.house.get(ownerId)
        if houses is not None:
            for house in houses:
                if not hasattr(house, 'interiorZoneId'):
                    self.notify.warning('getEstateHouseZones: (owner %s) house has no interiorZoneId')
                else:
                    zones.append(house.interiorZoneId)
        return zones

    def __sendZoneToClient(self, recipient, ownerId):
        try:
            zone = self.estateZone[ownerId][0]
            owner = self.zone2owner[zone]
            self.sendUpdateToAvatarId(recipient, "setEstateZone", [owner, zone])
        except:
            self.notify.warning("zone did not exist for estate owner %d, and visitor %d" % (ownerId, recipient))
            self.sendUpdateToAvatarId(recipient, "setEstateZone", [0, 0])

    def __createEstateZoneAndObjects(self, avId, isOwner, ownerId, name):
        # assume this is only called when isOwner == 1

        # stop any cleanup tasks that might be pending for this avId
        # (note: we might be in a case where we aren't in the toBeDeleted list
        # and still have a cleanup task pending.  this happens when we switch
        # shards)
        self.__stopCleanupTask(avId)

        # first check that we aren't in the toBeDeleted list
        avZone = self.toBeDeleted.get(avId)
        if avZone:

            # move our info back to estateZone
            self.setEstateZone(avId, avZone)
            del self.toBeDeleted[avId]
            return

        # check if our account has an estate created under a different avatar
        if self.__checkAccountSwitchedAvatars(name, avId):
            return

        # request the zone for the owners estate
        zoneId = self.air.allocateZone()
        self.setEstateZone(avId, [zoneId, isOwner, name]) # [zoneId, isOwner, userName (if owner)]
        self.account2avId[name] = avId
        self.zone2owner[zoneId] = avId

        # start a ref count for this zone id
        self.refCount[zoneId] = []

        # don't send a message back yet since the estate is not filled
        # in.  Do this later.
        #self.sendUpdateToAvatarId(avId, "setEstateZone", [avId, zoneId])

        # create the estate and generate the zone
        #callback = PythonUtil.Functor(self.handleGetEstate, avId, ownerId)
        #self.air.getEstate(avId, zoneId, callback)

    def __removeReferences(self, avId, zoneId):
        try:
            self.clearEstateZone(avId)
            self.refCount[zoneId].remove(avId)
        except:
            self.notify.debug("we weren't in the refcount for %s." % zoneId)
            pass

    def setEstateZone(self, index, info):
        self.estateZone[index] = info

        #print some debug info
        frame = sys._getframe(1)
        lineno = frame.f_lineno
        defName = frame.f_code.co_name
        #str = "%s(%s):Added %s:estateZone=%s" % (defName, lineno, index, self.estateZone)
        str = "%s(%s):Added %s:%s" % (defName, lineno, index, info)
        self.notify.debug(str)

    def clearEstateZone(self, index):
        assert index in self.estateZone

        #print some debug info
        frame = sys._getframe(1)
        lineno = frame.f_lineno
        defName = frame.f_code.co_name
        #str = "%s(%s):Removed %s:estateZone=%s" % (defName, lineno, index, self.estateZone)
        str = "%s(%s):Removed %s:%s" % (defName, lineno, index, self.estateZone[index])
        self.notify.debug(str)

        del self.estateZone[index]

    def __addReferences(self, avId, ownerId):
        avZone = self.estateZone.get(ownerId)
        if avZone:
            zoneId = avZone[0]
            self.setEstateZone(avId, [zoneId, 0, ""])  # [zoneId, isOwner, userName (if owner)]
            ref = self.refCount.get(zoneId)
            if ref:
                ref.append(avId)
            else:
                self.refCount[zoneId] = [avId]

    def __checkAccountSwitchedAvatars(self, name, ownerId):
        self.notify.debug("__checkAccountSwitchedAvatars")
        prevAvId = self.account2avId.get(name)
        if prevAvId:
            self.notify.debug("we indeed did switch avatars")
            # the estate exists, remap all references from prevAvId
            # to ownerId

            # first stop the cleanup task
            self.__stopCleanupTask(prevAvId)

            # now remap references
            self.account2avId[name] = ownerId

            #if self.estateZone.has_key(prevAvId):
            if prevAvId in self.toBeDeleted:
                self.setEstateZone(ownerId, self.toBeDeleted[prevAvId])
                del self.toBeDeleted[prevAvId]
            return 1
        return 0

    def handleGetEstate(self, avId, ownerId, estateId, estateVal,
                        numHouses, houseId, houseVal, petIds, valDict = None):
        self.notify.debug("handleGetEstate %s" % avId)
        # this function is called after the estate data is pulled
        # from the database.  the houseAI object is initialized
        # here, and if values don't exist for certain db fields
        # default values are given.

        # Note:  this is the place where randomized default values
        # should be assigned to the toons house.  For example:
        # door types, windows, colors, house selection, garden placement
        # etc.  The first time the toon visits his house, these
        # defaults will be computed and stored.

        # Note:  this function is only called by the owner of the estate

        # there is a chance that the owner will already have left (by
        # closing the window).  We need to handle that gracefully.

        if ownerId not in self.estateZone:
            self.notify.warning("Estate info was requested, but the owner left before it could be recived: %d" % estateId)
            return
        elif not avId in self.air.doId2do:
            self.notify.warning("Estate owner %s in self.estateZone, but not in doId2do" % avId)
            return

        # create the DistributedEstateAI object for this avId
        if avId in self.estateZone:
            if estateId in self.air.doId2do:
                self.notify.warning("Already have distobj %s, not generating again" % (estateId))
            else:
                self.notify.info('start estate %s init, owner=%s, frame=%s' %
                                 (estateId, ownerId, globalClock.getFrameCount()))

                # give the estate a time seed
                estateZoneId = self.estateZone[avId][0]
                ts = time.time() % HouseGlobals.DAY_NIGHT_PERIOD
                self.randomGenerator.seed(estateId)
                dawn = HouseGlobals.DAY_NIGHT_PERIOD * self.randomGenerator.random()
                estateAI = DistributedEstateAI.DistributedEstateAI(self.air, avId,
                                                                   estateZoneId, ts, dawn, valDict)
                # MPG - We should make sure this works across districts
                estateAI.dbObject = 1
                estateAI.generateWithRequiredAndId(estateId,
                                                   self.air.districtId,
                                                   estateZoneId)

                estateAI.initEstateData(estateVal, numHouses, houseId, houseVal)
                estateAI.setPetIds(petIds)
                self.estate[avId] = estateAI

                # create the DistributedHouseAI's.  This was originally done by the EstateAI
                # but we need to move it here so we can explicitly control when the
                # DistributedHouse objects get deleted from the stateserver.
                self.house[avId] = [None] * numHouses
                for i in range(numHouses):
                    if houseId[i] in self.air.doId2do:
                        self.notify.warning("doId of house %s conflicts with a %s!" % (houseId[i], self.air.doId2do[houseId[i]].__class__.__name__))

                    else:
                        house = DistributedHouseAI.DistributedHouseAI(self.air,
                                                                      houseId[i],
                                                                      estateId, estateZoneId, i)

                        # get house information
                        house.initFromServerResponse(houseVal[i])
                        self.house[avId][i] = house

                        # Now that we have all the data loaded, officially
                        # generate the distributed object

                        house.dbObject = 1

                        # MPG - We should make sure this works across districts
                        house.generateWithRequiredAndId(houseId[i],
                                                        self.air.districtId,
                                                        estateZoneId)

                        house.setupEnvirons()

                        # Finally, make sure that the house has a good owner,
                        # and then tell the client the house is ready.
                        house.checkOwner()

                        estateAI.houseList.append(house)

                estateAI.postHouseInit()

                #get us a list of the owners of the houses
                avIdList = []
                for id in houseId:
                    avHouse = simbase.air.doId2do.get(id)
                    avIdList.append(avHouse.ownerId)

                if simbase.wantPets:
                    self.notify.debug('creating pet collisions for estate %s' %
                                     estateId)
                    estateAI.createPetCollisions()

                # create a pond bingo manager ai for the new estate
                if simbase.wantBingo:
                    self.notify.info('creating bingo mgr for estate %s' %
                                     estateId)
                    self.air.createPondBingoMgrAI(estateAI)

                self.notify.info('finish estate %s init, owner=%s' %
                                 (estateId, ownerId))

                estateAI.gardenInit(avIdList)

        # Now that the zone is set up, send the notification back to
        # the client.
        self.__sendZoneToClient(avId, ownerId)
        zoneId = self.estateZone[ownerId][0]
        self._listenForToonEnterEstate(avId, ownerId, zoneId)

    ## -----------------------------------------------------------
    ## Cleanup and exit functions
    ## -----------------------------------------------------------

    def exitEstate(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        self.notify.debug("exitEstate(%s)" % avId)
        # This function is called from client in the normal case,
        # such as teleporting out, door out, exiting the game, etc
        self.__exitEstate(avId)

        self._unmapFromEstate(av)
        self._unloadEstate(av)

    def __handleUnexpectedExit(self, avId):
        self.notify.debug("we got an unexpected exit on av: %s:  deleting." % avId)
        taskMgr.remove("estateToonUp-" + str(avId))
        if avId in self.avId2pendingEnter:
            self._toonLeftBeforeArrival(avId)
        self.__exitEstate(avId)
        return None

    def __exitEstate(self, avId):
       # self.notify.debug("__exitEstate(%d)" % avId)
        # This is called whenever avId leaves an estate.
        # Determine if avId is the owner.  If so, set
        # a timer to cleanup all of the estate resources
        # and to kick all visitors out.  If we aren't the
        # owner, just remove references of avId from the estate
        avZone = self.estateZone.get(avId)
        if avZone:
            zoneId = avZone[0]
            ownerId = self.zone2owner[zoneId]
            self.announceToonExitEstate(avId, ownerId, zoneId)
            if avZone[1]:
                self.notify.debug("__exitEstate: av %d owns estate" % avId)
                # avId owns the estate
                ownerId = avId

                # warn visitors they have n seconds to finish what they were doing
                self.__warnVisitors(avZone[0])

                # start timers to kick people out and cleanup our resources
                if self.air:
                    self.ignore(self.air.getAvatarExitEvent(avId))
                taskMgr.doMethodLater(HouseGlobals.BOOT_GRACE_PERIOD,
                                      PythonUtil.Functor(self.__bootVisitorsAndCleanup, avId, avZone[0]),
                                      "bootVisitorsAndCleanup-"+str(avId))

                # remove avId references from estateZone
                self.clearEstateZone(avId)
                self.toBeDeleted[avId] = avZone
            else:
                self.notify.debug("__exitEstate: av %d doesn't own estate" % avId)
                # avId doesn't own this estate, just remove references to avId
                # from the data structures
                if avId in self.estateZone:
                    self.clearEstateZone(avId)
                try:
                    self.refCount[avZone[0]].remove(avId)
                except:
                    self.notify.debug("wasn't in refcount: %s, %s" % (avZone[0], avId))
        else:
            self.notify.debug("__exitEstate can't find zone for {0}".format(avId))

        # stop the healing
        if avId in self.air.doId2do:
            # Find the avatar
            av = self.air.doId2do[avId]
            # Stop healing them
            av.stopToonUp()

    def _cleanupEstate(self, avId, zoneId, task):
        self.notify.debug("cleanupEstate avId = %s, zoneId = %s" % (avId, zoneId))
        # we should always be cleaning up things from the toBeDeleted list,
        # not directly from estateZone

        # remove all 'hanging' entries left in estateZone
        # this is caused by:
        #   friend A is visting friend B
        #   friend B exits his estate
        #   friend C attempts to visit friend A at the same time
        for someAvId, avZone in list(self.estateZone.items()):
            if avZone[0] == zoneId:
                # This may be a slow client that just hasn't reported back.
                # If the toon is still in the zone, announce that they've
                # left before cleaning up the tables. When they report in that
                # they've left (client->AI: exitEstate), the code will not
                # find the avatar in the tables and will ignore.
                avatar = simbase.air.doId2do.get(someAvId)
                if ((avatar) and
                    (hasattr(avatar, "estateZones")) and
                    (zoneId in avatar.estateZones) and
                    (avatar.zoneId in avatar.estateZones)):
                    ownerId = self.zone2owner[zoneId]
                    self.notify.warning(
                        "forcing announcement of toon %s exit from %s %s" %
                        (someAvId, ownerId, zoneId))
                    self.announceToonExitEstate(someAvId, ownerId, zoneId)

                self.notify.warning(
                    "Manually removing (bad) entry in estateZone: %s" %
                    someAvId)
                self.clearEstateZone(someAvId)

        # give our zoneId back to the air
        self.air.deallocateZone(zoneId)
        avZone = self.toBeDeleted.get(avId)
        if avZone:
            if avZone[2] != "":
                if avZone[2] in self.account2avId:
                    self.notify.debug( "removing %s from account2avId" % avZone[2])
                    del self.account2avId[avZone[2]]
            del self.toBeDeleted[avId]
            del self.zone2owner[avZone[0]]

        # delete estate and houses from state server
        self.__deleteEstate(avId)

        # stop listening for unexpectedExit
        self.ignore(self.air.getAvatarExitEvent(avId))

        # refcount should be empty, just delete
        if zoneId in self.refCount:
            del self.refCount[zoneId]

        return Task.done

    def __stopCleanupTask(self, avId):
        self.notify.debug("stopCleanupTask %s" % avId)
        taskMgr.remove("cleanupEstate-"+str(avId))
        taskMgr.remove("bootVisitorsAndCleanup-"+str(avId))
        self.acceptOnce(self.air.getAvatarExitEvent(avId),
                        self.__handleUnexpectedExit, extraArgs=[avId])


    def __deleteEstate(self, avId):
        # remove all our objects from the stateserver
        self.notify.debug("__deleteEstate(avId=%s)" % avId)

        # delete from state server
        if avId in self.estate:
            if self.estate[avId] != None:
                self.estate[avId].destroyEstateData()
                self.notify.debug('DistEstate requestDelete, doId=%s' %
                                  getattr(self.estate[avId], 'doId'))
                self.estate[avId].requestDelete()
                # This automatically gets called by the server
                # self.estate[avId].delete()
                del self.estate[avId]
        # delete the houses
        houses = self.house.get(avId)
        if houses:
            for i in range(len(houses)):
                if self.house[avId][i]:
                    self.house[avId][i].requestDelete()
                    # This automatically gets called by the server
                    # self.house[avId][i].delete()
            del self.house[avId]

    """
    def __bootVisitors(self, zoneId, task):
        try:
            visitors = self.refCount[zoneId][:]
            for avId in visitors:
                self.__bootAv(avId, zoneId)
        except:
            # refCount might have already gotten deleted
            pass
        return Task.done
    """

    def __bootVisitorsAndCleanup(self, ownerId, zoneId, task):
        try:
            visitors = self.refCount[zoneId][:]
            for avId in visitors:
                self.__bootAv(avId, zoneId, ownerId)
        except:
            # refCount might have already gotten deleted
            pass
        taskMgr.doMethodLater(HouseGlobals.CLEANUP_DELAY_AFTER_BOOT,
                              PythonUtil.Functor(self._cleanupEstate, ownerId, zoneId),
                              "cleanupEstate-"+str(ownerId))
        return Task.done

    def __bootAv(self, avId, zoneId, ownerId, retCode=1):
        messenger.send("bootAvFromEstate-"+str(avId))
        self.sendUpdateToAvatarId(avId, "sendAvToPlayground", [avId, retCode])
        if avId in self.toBeDeleted:
            del self.toBeDeleted[avId]
        try:
            self.refCount[zoneId].remove(avId)
        except:
            self.notify.debug("didn't have refCount[%s][%s]" % (zoneId,avId))
            pass

    def __warnVisitors(self, zoneId):
        visitors = self.refCount.get(zoneId)
        if visitors:
            for avId in visitors:
                self.sendUpdateToAvatarId(avId, "sendAvToPlayground", [avId, 0])

    def removeFriend(self, ownerId, avId):
        self.notify.debug("removeFriend ownerId = %s, avId = %s" % (ownerId, avId))
        # check if ownerId is in an estate
        ownZone = self.estateZone.get(ownerId)
        if ownZone:
            if ownZone[1]:
                # owner is in his own estate.  kick out avId if he is
                # in the owner's estate.
                avZone = self.estateZone.get(avId)
                if avZone:
                    if avZone[0] == ownZone[0]:
                        # avId is indeed in owner's estate.  boot him
                        self.__bootAv(avId, ownZone[0], ownerId, retCode=2)
                    else:
                        print("visitor not in owners estate")
                else:
                    print("av is not in an estate")

        else:
            print("owner not in estate")

    ## -----------------------------------------------------------
    ## April fools stuff
    ## -----------------------------------------------------------

    def startAprilFools(self):
        self.sendUpdate("startAprilFools",[])

    def stopAprilFools(self):
        self.sendUpdate("stopAprilFools",[])


#credit to toontown school house

    def __handleLoadEstate(self, av, callback, accId, zoneId):
        self._unmapFromEstate(av)
        av.loadEstateOperation = LoadEstateOperation(self, callback)
        av.loadEstateOperation.start(accId, zoneId)

    def _unloadEstate(self, av):
        if getattr(av, 'estate', None):
            estate = av.estate
            avId = estate.owner.doId
            zoneId = estate.zoneId
            if estate not in self.estate2timeout:
                self.estate2timeout[estate] = taskMgr.doMethodLater(HouseGlobals.CLEANUP_DELAY_AFTER_BOOT,
                              PythonUtil.Functor(self._cleanupEstate, avId, zoneId),
                              "cleanupEstate-"+str(avId))
            # Send warning:
            self._sendToonsToPlayground(av.estate, 0)

        if getattr(av, 'loadEstateOperation', None):
            self.air.deallocateZone(av.loadEstateOperation.zoneId)
            av.loadEstateOperation.cancel()
            av.loadEstateOperation = None

        if av and hasattr(av, 'exitEstate') and hasattr(av, 'isInEstate') and av.isInEstate():
            av.exitEstate()

        if av and av.getPetId() != 0:
            self.ignore(self.air.getAvatarExitEvent(av.getPetId()))
            pet = self.air.doId2do.get(av.getPetId())
            if pet:
                pet.requestDelete()

        self.ignore(self.air.getAvatarExitEvent(av.doId))

    def _mapToEstate(self, av, estate):
        self._unmapFromEstate(av)
        self.estate[av.doId] = estate
        self.estate2toons.setdefault(estate, []).append(av)
        if av not in self.toon2estate:
            self.toon2estate[av] = estate

        self.zone2toons.setdefault(estate.zoneId, []).append(av.doId)
    def _unmapFromEstate(self, av):
        estate = self.toon2estate.get(av)
        if not estate:
            return

        try:
            del self.estate[av.doId]
        except KeyError:
            pass

        del self.toon2estate[av]
        try:
            self.estate2toons[estate].remove(av)
        except (KeyError, ValueError):
            pass

        try:
            self.zone2toons[estate.zoneId].remove(av.doId)
        except (KeyError, ValueError):
            pass
        
    def _sendToonsToPlayground(self, estate, reason):
        for toon in self.estate2toons.get(estate, []):
            self.sendUpdateToAvatarId(toon.doId, 'sendAvToPlayground', [toon.doId, reason])

    def __handleLoadPet(self, estate, av):
        petOperation = LoadPetOperation(self, estate, av, self.__handlePetLoaded)
        self.petOperations.append(petOperation)
        petOperation.start()

    def __handlePetLoaded(self, _):
        # A pet operation just finished! Let's see if all of them are done:
        if all(petOperation.done for petOperation in self.petOperations):
            self.petOperations = []
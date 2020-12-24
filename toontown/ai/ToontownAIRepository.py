from direct.directnotify import DirectNotifyGlobal
from direct.task.Task import Task
from panda3d.core import *
from otp.ai import BanManagerAI

from libpandadna import *
from otp.ai.AIZoneData import AIZoneDataStore
from otp.ai.TimeManagerAI import TimeManagerAI
from otp.distributed.OtpDoGlobals import *
from toontown.ai.HolidayManagerAI import HolidayManagerAI
from toontown.ai.NewsManagerAI import NewsManagerAI
from toontown.ai.WelcomeValleyManagerAI import WelcomeValleyManagerAI
from toontown.building.DistributedTrophyMgrAI import DistributedTrophyMgrAI
from toontown.catalog.CatalogManagerAI import CatalogManagerAI
from toontown.coghq.CogSuitManagerAI import CogSuitManagerAI
from toontown.coghq.CountryClubManagerAI import CountryClubManagerAI
from toontown.coghq.FactoryManagerAI import FactoryManagerAI
from toontown.coghq.LawOfficeManagerAI import LawOfficeManagerAI
from toontown.coghq.MintManagerAI import MintManagerAI
from toontown.coghq.PromotionManagerAI import PromotionManagerAI
from toontown.distributed.ToontownDistrictAI import ToontownDistrictAI
from toontown.distributed.ToontownDistrictStatsAI import ToontownDistrictStatsAI
from toontown.distributed.ToontownInternalRepository import ToontownInternalRepository
from toontown.hood import ZoneUtil
from toontown.hood.BRHoodDataAI import BRHoodDataAI
from toontown.hood.BossbotHQDataAI import BossbotHQDataAI
from toontown.hood.CSHoodDataAI import CSHoodDataAI
from toontown.hood.CashbotHQDataAI import CashbotHQDataAI
from toontown.hood.DDHoodDataAI import DDHoodDataAI
from toontown.hood.DGHoodDataAI import DGHoodDataAI
from toontown.hood.DLHoodDataAI import DLHoodDataAI
from toontown.hood.GSHoodDataAI import GSHoodDataAI
from toontown.hood.GZHoodDataAI import GZHoodDataAI
from toontown.hood.LawbotHQDataAI import LawbotHQDataAI
from toontown.hood.MMHoodDataAI import MMHoodDataAI
from toontown.hood.OZHoodDataAI import OZHoodDataAI
from toontown.hood.TTHoodDataAI import TTHoodDataAI
from toontown.pets.PetManagerAI import PetManagerAI
from toontown.quest.QuestManagerAI import QuestManagerAI
from toontown.racing import RaceGlobals
from toontown.racing.DistributedLeaderBoardAI import DistributedLeaderBoardAI
from toontown.racing.DistributedRacePadAI import DistributedRacePadAI
from toontown.racing.DistributedStartingBlockAI import DistributedStartingBlockAI
from toontown.racing.DistributedStartingBlockAI import DistributedViewingBlockAI
from toontown.racing.DistributedViewPadAI import DistributedViewPadAI
from toontown.racing.RaceManagerAI import RaceManagerAI
from toontown.safezone.SafeZoneManagerAI import SafeZoneManagerAI
from toontown.shtiker.CogPageManagerAI import CogPageManagerAI
from toontown.suit.SuitInvasionManagerAI import SuitInvasionManagerAI
from toontown.toon import NPCToons
from toontown.toonbase import ToontownGlobals
from toontown.uberdog.DistributedInGameNewsMgrAI import DistributedInGameNewsMgrAI
from toontown.estate.EstateManagerAI import EstateManagerAI
from toontown.tutorial.TutorialManagerAI import TutorialManagerAI
from toontown.fishing import DistributedFishingPondAI
from toontown.safezone import DistributedFishingSpotAI
from toontown.safezone import DistributedPartyGateAI
from toontown.ai.ToontownMagicWordManagerAI import ToontownMagicWordManagerAI
from toontown.uberdog.DistributedPartyManagerAI import DistributedPartyManagerAI
from toontown.parties.ToontownTimeManager import ToontownTimeManager
from toontown.coderedemption.TTCodeRedemptionMgrAI import TTCodeRedemptionMgrAI
import time
from direct.distributed.PyDatagram import PyDatagram
from toontown.ai.ToontownAIMsgTypes import *
from libpandadna import *
from toontown.fishing import FishManagerAI
from otp.friends.FriendManagerAI import FriendManagerAI
class ToontownAIRepository(ToontownInternalRepository):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToontownAIRepository')

    def __init__(self, baseChannel, serverId, districtName):
        ToontownInternalRepository.__init__(self, baseChannel, serverId, dcSuffix='AI')
        self.districtName = districtName
        self.doLiveUpdates = config.GetBool('want-live-updates', True)
        self.wantCogdominiums = config.GetBool('want-cogdominiums', True)
        self.wantBanManager = config.GetBool('want-ban-manager', False) #change to true once we have a working one
        self.useAllMinigames = config.GetBool('want-all-minigames', True)
        self.districtId = None
        self.district = None
        self.districtStats = None
        self.holidayManager = None
        self.zoneDataStore = None
        self.petMgr = None
        self.suitInvasionManager = None
        self.zoneAllocator = None
        self.zoneId2owner = {}
        self.questManager = None
        self.promotionMgr = None
        self.cogPageManager = None
        self.raceMgr = None
        self.countryClubMgr = None
        self.factoryMgr = None
        self.mintMgr = None
        self.lawMgr = None
        self.cogSuitMgr = None
        self.timeManager = None
        self.newsManager = None
        self.welcomeValleyManager = None
        self.inGameNewsMgr = None
        self.catalogManager = None
        self.trophyMgr = None
        self.safeZoneManager = None
        self.estateMgr = None
        self.tutorialManager = None
        self.magicWordManager = None
        self.partyManager = None
        self.codeRedemptionManager = None
        self.friendManager = None

        self.zoneTable = {}
        self.dnaStoreMap = {}
        self.dnaDataMap = {}
        self.hoods = []
        self.buildingManagers = {}
        self.suitPlanners = {}
        self.__queryEstateContext = 0
        self.__queryEstateFuncMap = {}
        # Guard for publish
        if simbase.wantBingo:
            self.bingoMgr = None

        # player avatars will increment and decrement this count
        self._population = 0

        # Record the reason each client leaves the shard, according to
        # the client.
        self._avatarDisconnectReasons = {}

        # These are used to query database objects directly; currently
        # used only for offline utilities.
        self.dbObjContext = 0
        self.dbObjMap = {}
    def handleConnected(self):
        ToontownInternalRepository.handleConnected(self)

        # Generate our district...
        self.districtId = self.allocateChannel()
        self.district = ToontownDistrictAI(self)
        self.district.setName(self.districtName)
        self.district.generateWithRequiredAndId(self.districtId, self.getGameDoId(), OTP_ZONE_ID_DISTRICTS)

        # Claim ownership of that district...
        self.district.setAI(self.ourChannel)

        # These are objects that are required before anything else.
        self.createFirstObjs()

        # Create our local objects.
        self.createLocals()

        # Create our global objects.
        self.createGlobals()

        # Create our zones.
        self.createZones()

        # Make our district available, and we're done.
        self.district.b_setAvailable(True)
        self.notify.info('Done.')
        # Now that everything's created, start checking the leader
        # boards for correctness.  We only need to check every 30
        # seconds or so.
        self.__leaderboardFlush(None)
        taskMgr.doMethodLater(30, self.__leaderboardFlush,
                              'leaderboardFlush', appendTask = True)
                              
    def __leaderboardFlush(self, task):
        messenger.send('leaderboardFlush')
        return Task.again

    def createFirstObjs(self):
        # Generate our news manager...
        self.newsManager = NewsManagerAI(self)
        self.newsManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)

        # Generate our estate manager...
        self.estateMgr = EstateManagerAI(self)
        self.estateMgr.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)

        self.dataStoreManager = self.generateGlobalObject(OTP_DO_ID_TOONTOWN_TEMP_STORE_MANAGER, 'DistributedDataStoreManager')

        #Generate our delivery manager
        self.deliveryManager = self.generateGlobalObject(
            OTP_DO_ID_TOONTOWN_DELIVERY_MANAGER,
            "DistributedDeliveryManager")
        #Generate our mail manager
        self.mailManager = self.generateGlobalObject(
            OTP_DO_ID_TOONTOWN_MAIL_MANAGER,
            "DistributedMailManager")
            
        # Create our suit invasion manager...
        self.suitInvasionManager = SuitInvasionManagerAI(self)

        # Create our holiday manager...
        self.holidayManager = HolidayManagerAI(self)

    def createLocals(self):
        """
        Creates "local" (non-distributed) objects.
        """

        # Create our zone data store...
        self.zoneDataStore = AIZoneDataStore()

        # Create our pet manager...
        self.petMgr = PetManagerAI(self)

        # Create our zone allocator...
        self.zoneAllocator = UniqueIdAllocator(ToontownGlobals.DynamicZonesBegin, ToontownGlobals.DynamicZonesEnd)

        # Create our quest manager...
        self.questManager = QuestManagerAI(self)

        #create our fish manager
        self.fishManager = FishManagerAI.FishManagerAI(self)

        # Create our promotion manager...
        self.promotionMgr = PromotionManagerAI(self)

        # Create our Cog page manager...
        self.cogPageManager = CogPageManagerAI(self)

        # Create our race manager...
        self.raceMgr = RaceManagerAI(self)

        # Create our country club manager...
        self.countryClubMgr = CountryClubManagerAI(self)

        # Create our factory manager...
        self.factoryMgr = FactoryManagerAI(self)

        # Create our mint manager...
        self.mintMgr = MintManagerAI(self)

        # Create our law office manager...
        self.lawMgr = LawOfficeManagerAI(self)

        # Create our Cog suit manager...
        self.cogSuitMgr = CogSuitManagerAI(self)

        # Create our Toontown time manager...
        self.toontownTimeManager = ToontownTimeManager()
        self.toontownTimeManager.updateLoginTimes(time.time(), time.time(), globalClock.getRealTime())
        if self.wantBanManager:
            self.banManager = BanManagerAI.BanManagerAI()


    def createGlobals(self):
        """
        Creates "global" (distributed) objects.
        """

        # Generate our district stats...
        self.districtStats = ToontownDistrictStatsAI(self)
        self.districtStats.toontownDistrictId = self.districtId
        self.districtStats.generateWithRequiredAndId(self.allocateChannel(), self.district.getDoId(),
                                                     OTP_ZONE_ID_DISTRICTS_STATS)

        # Generate our time manager...
        self.timeManager = TimeManagerAI(self)
        self.timeManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)

        # Generate our Welcome Valley manager...
        self.welcomeValleyManager = WelcomeValleyManagerAI(self)
        self.welcomeValleyManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)

        # Generate our in-game news manager...
        self.inGameNewsMgr = DistributedInGameNewsMgrAI(self)
        self.inGameNewsMgr.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)

        # Generate our catalog manager...
        self.catalogManager = CatalogManagerAI(self)
        self.catalogManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)

        # Generate our trophy manager...
        self.trophyMgr = DistributedTrophyMgrAI(self)
        self.trophyMgr.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)

        # Generate our safezone manager...
        self.safeZoneManager = SafeZoneManagerAI(self)
        self.safeZoneManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)

        # The Tutorial manager
        self.tutorialManager = TutorialManagerAI(self)
        self.tutorialManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)

        # The Magic Word Manager
        magicWordString = simbase.config.GetString('want-magic-words', '1')
        if magicWordString not in ('', '0', '#f'):
            self.magicWordManager = ToontownMagicWordManagerAI(self)
            self.magicWordManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)

        # Generate our party manager...
        self.partyManager = DistributedPartyManagerAI(self)
        self.partyManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)

        # Generate our code redemption manager...
        self.codeRedemptionManager = TTCodeRedemptionMgrAI(self)
        self.codeRedemptionManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        
        # Generate our friend manager...
        self.friendManager = FriendManagerAI(self)
        self.friendManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
    def generateHood(self, hoodConstructor, zoneId):
        # Bossbot HQ doesn't use DNA, so we skip over that.
        if zoneId != ToontownGlobals.BossbotHQ:
            self.dnaStoreMap[zoneId] = DNAStorage()
            self.dnaDataMap[zoneId] = loadDNAFileAI(self.dnaStoreMap[zoneId], self.genDNAFileName(zoneId))
            if zoneId in ToontownGlobals.HoodHierarchy:
                for streetId in ToontownGlobals.HoodHierarchy[zoneId]:
                    self.dnaStoreMap[streetId] = DNAStorage()
                    self.dnaDataMap[streetId] = loadDNAFileAI(self.dnaStoreMap[streetId], self.genDNAFileName(streetId))

        hood = hoodConstructor(self, zoneId)
        hood.startup()
        self.hoods.append(hood)

    def startupHood(self, hoodDataAI):
        hoodDataAI.startup()
        self.hoods.append(hoodDataAI)

    def shutdownHood(self, hoodDataAI):
        hoodDataAI.shutdown()
        self.hoods.remove(hoodDataAI)

    def createZones(self):
        # First, generate our zone2NpcDict...
        NPCToons.generateZone2NpcDict()

        # Donald's Dock
        self.zoneTable[ToontownGlobals.DonaldsDock] = (
            (ToontownGlobals.DonaldsDock, 1, 0), (ToontownGlobals.BarnacleBoulevard, 1, 1),
            (ToontownGlobals.SeaweedStreet, 1, 1), (ToontownGlobals.LighthouseLane, 1, 1)
        )
        self.generateHood(DDHoodDataAI, ToontownGlobals.DonaldsDock)

        # Toontown Central
        self.zoneTable[ToontownGlobals.ToontownCentral] = (
            (ToontownGlobals.ToontownCentral, 1, 0), (ToontownGlobals.SillyStreet, 1, 1),
            (ToontownGlobals.LoopyLane, 1, 1), (ToontownGlobals.PunchlinePlace, 1, 1)
        )
        self.generateHood(TTHoodDataAI, ToontownGlobals.ToontownCentral)

        # The Brrrgh
        self.zoneTable[ToontownGlobals.TheBrrrgh] = (
            (ToontownGlobals.TheBrrrgh, 1, 0), (ToontownGlobals.WalrusWay, 1, 1),
            (ToontownGlobals.SleetStreet, 1, 1), (ToontownGlobals.PolarPlace, 1, 1)
        )
        self.generateHood(BRHoodDataAI, ToontownGlobals.TheBrrrgh)

        # Minnie's Melodyland
        self.zoneTable[ToontownGlobals.MinniesMelodyland] = (
            (ToontownGlobals.MinniesMelodyland, 1, 0), (ToontownGlobals.AltoAvenue, 1, 1),
            (ToontownGlobals.BaritoneBoulevard, 1, 1), (ToontownGlobals.TenorTerrace, 1, 1)
        )
        self.generateHood(MMHoodDataAI, ToontownGlobals.MinniesMelodyland)

        # Daisy Gardens
        self.zoneTable[ToontownGlobals.DaisyGardens] = (
            (ToontownGlobals.DaisyGardens, 1, 0), (ToontownGlobals.ElmStreet, 1, 1),
            (ToontownGlobals.MapleStreet, 1, 1), (ToontownGlobals.OakStreet, 1, 1)
        )
        self.generateHood(DGHoodDataAI, ToontownGlobals.DaisyGardens)

        # Chip 'n Dale's Acorn Acres
        self.zoneTable[ToontownGlobals.OutdoorZone] = (
            (ToontownGlobals.OutdoorZone, 1, 0),
        )
        self.generateHood(OZHoodDataAI, ToontownGlobals.OutdoorZone)

        # Goofy Speedway
        self.zoneTable[ToontownGlobals.GoofySpeedway] = (
            (ToontownGlobals.GoofySpeedway, 1, 0),
        )
        self.generateHood(GSHoodDataAI, ToontownGlobals.GoofySpeedway)

        # Donald's Dreamland
        self.zoneTable[ToontownGlobals.DonaldsDreamland] = (
            (ToontownGlobals.DonaldsDreamland, 1, 0), (ToontownGlobals.LullabyLane, 1, 1),
            (ToontownGlobals.PajamaPlace, 1, 1)
        )
        self.generateHood(DLHoodDataAI, ToontownGlobals.DonaldsDreamland)

        # Bossbot HQ
        self.zoneTable[ToontownGlobals.BossbotHQ] = (
            (ToontownGlobals.BossbotHQ, 0, 0),
        )
        self.generateHood(BossbotHQDataAI, ToontownGlobals.BossbotHQ)

        # Sellbot HQ
        self.zoneTable[ToontownGlobals.SellbotHQ] = (
            (ToontownGlobals.SellbotHQ, 0, 1), (ToontownGlobals.SellbotFactoryExt, 0, 1)
        )
        self.generateHood(CSHoodDataAI, ToontownGlobals.SellbotHQ)

        # Cashbot HQ
        self.zoneTable[ToontownGlobals.CashbotHQ] = (
            (ToontownGlobals.CashbotHQ, 0, 1),
        )
        self.generateHood(CashbotHQDataAI, ToontownGlobals.CashbotHQ)

        # Lawbot HQ
        self.zoneTable[ToontownGlobals.LawbotHQ] = (
            (ToontownGlobals.LawbotHQ, 0, 1),
        )
        self.generateHood(LawbotHQDataAI, ToontownGlobals.LawbotHQ)

        # Chip 'n Dale's MiniGolf
        self.zoneTable[ToontownGlobals.GolfZone] = (
            (ToontownGlobals.GolfZone, 1, 0),
        )
        self.generateHood(GZHoodDataAI, ToontownGlobals.GolfZone)

        # Assign the initial suit buildings.
        for suitPlanner in list(self.suitPlanners.values()):
            suitPlanner.assignInitialSuitBuildings()

    def genDNAFileName(self, zoneId):
        canonicalZoneId = ZoneUtil.getCanonicalZoneId(zoneId)
        canonicalHoodId = ZoneUtil.getCanonicalHoodId(canonicalZoneId)
        hood = ToontownGlobals.dnaMap[canonicalHoodId]
        if canonicalHoodId == canonicalZoneId:
            canonicalZoneId = 'sz'
            phase = ToontownGlobals.phaseMap[canonicalHoodId]
        else:
            phase = ToontownGlobals.streetPhaseMap[canonicalHoodId]

        if 'outdoor_zone' in hood or 'golf_zone' in hood:
            phase = '6'

        return 'phase_%s/dna/%s_%s.dna' % (phase, hood, canonicalZoneId)

    def lookupDNAFileName(self, dnaFileName):
        searchPath = DSearchPath()
        searchPath.appendDirectory(Filename('resources/phase_3.5/dna'))
        searchPath.appendDirectory(Filename('resources/phase_4/dna'))
        searchPath.appendDirectory(Filename('resources/phase_5/dna'))
        searchPath.appendDirectory(Filename('resources/phase_5.5/dna'))
        searchPath.appendDirectory(Filename('resources/phase_6/dna'))
        searchPath.appendDirectory(Filename('resources/phase_8/dna'))
        searchPath.appendDirectory(Filename('resources/phase_9/dna'))
        searchPath.appendDirectory(Filename('resources/phase_10/dna'))
        searchPath.appendDirectory(Filename('resources/phase_11/dna'))
        searchPath.appendDirectory(Filename('resources/phase_12/dna'))
        searchPath.appendDirectory(Filename('resources/phase_13/dna'))
        filename = Filename(dnaFileName)
        found = vfs.resolveFilename(filename, searchPath)
        if not found:
            self.notify.warning('lookupDNAFileName - %s not found on:' % dnaFileName)
            print(searchPath)
        else:
            return filename.getFullpath()

    def loadDNAFileAI(self, dnaStore, dnaFileName):
        return loadDNAFileAI(dnaStore, dnaFileName)

    def findFishingPonds(self, dnaGroup, zoneId, area, overrideDNAZone = 0):
        """
        Recursively scans the given DNA tree for fishing ponds.  These
        are defined as all the groups whose code includes the string
        "fishing_pond".  For each such group, creates a
        DistributedFishingPondAI.  Returns the list of distributed
        objects and a list of the DNAGroups so we can search them for
        spots and targets.
        """
        fishingPonds = []
        fishingPondGroups = []

        if ((isinstance(dnaGroup, DNAGroup)) and
            # If it is a DNAGroup, and the name starts with fishing_pond, count it
            (str.find(dnaGroup.getName(), 'fishing_pond') >= 0)):
            # Here's a fishing pond!
            fishingPondGroups.append(dnaGroup)
            fp = DistributedFishingPondAI.DistributedFishingPondAI(self, area)
            fp.generateWithRequired(zoneId)
            fishingPonds.append(fp)
        else:
            # Now look in the children
            # Fishing ponds cannot have other ponds in them,
            # so do not search the one we just found:
            # If we come across a visgroup, note the zoneId and then recurse
            if (isinstance(dnaGroup, DNAVisGroup) and not overrideDNAZone):
                # Make sure we get the real zone id, in case we are in welcome valley
                zoneId = ZoneUtil.getTrueZoneId(
                        int(dnaGroup.getName().split(':')[0]), zoneId)
            for i in range(dnaGroup.getNumChildren()):
                childFishingPonds, childFishingPondGroups = self.findFishingPonds(
                        dnaGroup.at(i), zoneId, area, overrideDNAZone)
                fishingPonds += childFishingPonds
                fishingPondGroups += childFishingPondGroups
        return fishingPonds, fishingPondGroups

    def findFishingSpots(self, dnaPondGroup, distPond):
        """
        Scans the given DNAGroup pond for fishing spots.  These
        are defined as all the props whose code includes the string
        "fishing_spot".  Fishing spots should be the only thing under a pond
        node. For each such prop, creates a DistributedFishingSpotAI.
        Returns the list of distributed objects created.
        """
        fishingSpots = []
        # Search the children of the pond
        for i in range(dnaPondGroup.getNumChildren()):
            dnaGroup = dnaPondGroup.at(i)
            if ((isinstance(dnaGroup, DNAProp)) and
                (str.find(dnaGroup.getCode(), 'fishing_spot') >= 0)):
                # Here's a fishing spot!
                pos = dnaGroup.getPos()
                hpr = dnaGroup.getHpr()
                fs = DistributedFishingSpotAI.DistributedFishingSpotAI(
                     self, distPond, pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
                fs.generateWithRequired(distPond.zoneId)
                fishingSpots.append(fs)
            else:
                self.notify.debug("Found dnaGroup that is not a fishing_spot under a pond group")
        return fishingSpots

    def findPartyHats(self, dnaGroup, zoneId, overrideDNAZone = 0):
        """
        Recursively scans the given DNA tree for party hats.  These
        are defined as all the groups whose code includes the string
        "party_gate".  For each such group, creates a
        DistributedPartyGateAI.  Returns the list of distributed
        objects.
        """
        partyHats = []

        if ((isinstance(dnaGroup, DNAGroup)) and
            # If it is a DNAGroup, and the name has party_gate, count it
            (str.find(dnaGroup.getName(), 'party_gate') >= 0)):
            # Here's a party hat!
            ph = DistributedPartyGateAI.DistributedPartyGateAI(self)
            ph.generateWithRequired(zoneId)
            partyHats.append(ph)
        else:
            # Now look in the children
            # Party hats cannot have other party hats in them,
            # so do not search the one we just found:
            # If we come across a visgroup, note the zoneId and then recurse
            if (isinstance(dnaGroup, DNAVisGroup) and not overrideDNAZone):
                # Make sure we get the real zone id, in case we are in welcome valley
                zoneId = ZoneUtil.getTrueZoneId(
                        int(dnaGroup.getName().split(':')[0]), zoneId)
            for i in range(dnaGroup.getNumChildren()):
                childPartyHats = self.findPartyHats(dnaGroup.at(i), zoneId, overrideDNAZone)
                partyHats += childPartyHats

        return partyHats

    def findRacingPads(self, dnaGroup, zoneId, area, overrideDNAZone = 0, type = 'racing_pad'):
        racingPads = []
        racingPadGroups = []
        if ((isinstance(dnaGroup, DNAGroup)) and (str.find(dnaGroup.getName(), type) >= 0)):
            racingPadGroups.append(dnaGroup)
            if (type == 'racing_pad'):
                nameInfo = dnaGroup.getName().split('_')
                #pdb.set_trace()
                #print "Name Info: ", nameInfo
                #print "Race Info: ", raceInfo
                racingPad = DistributedRacePadAI(self, area, nameInfo[3], int(nameInfo[2]))
            else:
                racingPad = DistributedViewPadAI(self, area)
            racingPad.generateWithRequired(zoneId)
            racingPads.append(racingPad)
        else:
            if (isinstance(dnaGroup, DNAVisGroup) and not overrideDNAZone):
                zoneId = ZoneUtil.getTrueZoneId(int(dnaGroup.getName().split(':')[0]), zoneId)
            for i in range(dnaGroup.getNumChildren()):
                childRacingPads, childRacingPadGroups = self.findRacingPads(dnaGroup.at(i), zoneId, area, overrideDNAZone, type)
                racingPads += childRacingPads
                racingPadGroups += childRacingPadGroups
        return racingPads, racingPadGroups

    def findStartingBlocks(self, dnaData, kartPad):
        startingBlocks = []
        for i in range(dnaData.getNumChildren()):
            groupName = dnaData.getName()
            block = dnaData.at(i)
            blockName = block.getName()
            if 'starting_block' in blockName:
                cls = DistributedStartingBlockAI if 'racing_pad' in groupName else DistributedViewingBlockAI
                x, y, z = block.getPos()
                h, p, r = block.getHpr()
                padLocationId = int(blockName[-1])
                startingBlock = cls(self, kartPad, x, y, z, h, p, r, padLocationId)
                startingBlock.generateWithRequired(kartPad.zoneId)
                startingBlocks.append(startingBlock)

        return startingBlocks

    def findLeaderBoards(self, dnaPool, zoneID):
        '''
        Find and return leader boards
        '''
        leaderBoards = []
        if (str.find(dnaPool.getName(), 'leaderBoard') >= 0):
            #found a leader board
            pos = dnaPool.getPos()
            hpr = dnaPool.getHpr()

            lb = DistributedLeaderBoardAI(self, dnaPool.getName(), zoneID, [], pos, hpr)
            lb.generateWithRequired(zoneID)
            leaderBoards.append(lb)
        else:
            for i in range(dnaPool.getNumChildren()):
                result = self.findLeaderBoards(dnaPool.at(i), zoneID)
                if result:
                    leaderBoards += result

        return leaderBoards

    def loadDNAFileAI(self, dnaStore, dnaFile):
        return loadDNAFileAI(dnaStore, dnaFile, CSDefault)

    #AIGEOM
    def loadDNAFile(self, dnaStore, dnaFile, cs=CSDefault):
        """
        load everything, including geometry
        """
        return loadDNAFile(dnaStore, dnaFile, cs)

    def loadDNA(self):
        """
        Return a dictionary of zoneId to DNAStorage objects
        """
        self.dnaStoreMap = {}
        self.dnaDataMap = {}
        for zones in self.zoneTable.values():
            for zone in zones:
                zoneId=zone[0]
                dnaStore = DNAStorage()
                dnaFileName = self.genDNAFileName(zoneId)
                dnaData = self.loadDNAFileAI(dnaStore, dnaFileName)
                self.dnaStoreMap[zoneId] = dnaStore
                self.dnaDataMap[zoneId] = dnaData
    def getTrackClsends(self):
        return False

    def getAvatarExitEvent(self, avId):
        return 'distObjDelete-%d' % avId

    def setAvatarDisconnectReason(self, avId, disconnectReason):
        # This is told us by the client just before he disconnects.
        self._avatarDisconnectReasons[avId] = disconnectReason

    def getAvatarDisconnectReason(self, avId):
        # Returns the reason (as reported by the client) for an
        # avatar's unexpected exit, or 0 if the reason is unknown.  It
        # is only valid to query this during the handler for the
        # avatar's unexpected-exit event.
        return self._avatarDisconnectReasons.get(avId, 0)

    def getZoneDataStore(self):
        return self.zoneDataStore

    def incrementPopulation(self):
        self._population += 1

    def decrementPopulation(self):
        if __dev__:
            assert self._population > 0
        self._population = max(0, self._population - 1)

    def allocateZone(self, owner=None):
        zoneId = self.zoneAllocator.allocate()
        if owner:
            self.zoneId2owner[zoneId] = owner

        return zoneId

    def deallocateZone(self, zone):
        if self.zoneId2owner.get(zone):
            del self.zoneId2owner[zone]

        self.zoneAllocator.free(zone)

    def trueUniqueName(self, idString):
        return self.uniqueName(idString)

    def sendQueryToonMaxHp(self, avId, callback):
        pass  # TODO?

    def getPopulation(self):
        if simbase.fakeDistrictPopulations:
            if not hasattr(self, '_fakePopulation'):
                import random
                self._fakePopulation = random.randrange(1000)
            return self._fakePopulation
        return self._population

    def writeServerStatus(self, who, avatar_count, object_count):
        pass

    def getWelcomeValleyCount(self):
        # avatars in Welcom Vally
        return self.welcomeValleyManager.getAvatarCount();

    def createPondBingoMgrAI(self, estate):
        """
        estate - the estate for which the PBMgrAI should
                be created.
        returns: None

        This method instructs the BingoManagerAI to
        create a new PBMgrAI for a newly generated
        estate.
        """
        # Guard for publish
        if simbase.wantBingo:
            if self.bingoMgr:
                self.notify.info('createPondBingoMgrAI: Creating a DPBMAI for Dynamic Estate')
                self.bingoMgr.createPondBingoMgrAI(estate, 1)

    def getEstate(self, avId, zone, callback):
        """
        Asks the database to fill in details about this avatars
        estate.
        We make a request to the server and wait for its response.
        """
        context = self.__queryEstateContext
        self.__queryEstateContext += 1
        self.__queryEstateFuncMap[context] = callback
        self.__sendGetEstate(avId, context)

    def __sendGetEstate(self, avId, context):
        """
        Sends the query-object message to the server.  The return
        message will be handled by __handleGetEstateResp().
        See getEstate().
        """
        datagram = PyDatagram()
        datagram.addServerHeader(
            DBSERVER_ID, self.ourChannel, DBSERVER_GET_ESTATE)
        datagram.addUint32(context)
        # The avId we are querying.
        datagram.addUint32(avId)
        self.send(datagram)

    def __handleGetEstateResp(self, di):
        # Use the context to retrieve the callback parameter passed in
        # to getEstate().
        context = di.getUint32()
        callback = self.__queryEstateFuncMap.get(context)
        if callback == None:
            self.notify.warning("Got unexpected estate context: %s" % (context))
            return
        del self.__queryEstateFuncMap[context]

        # return code = 0 if estate was returned without problems
        retCode = di.getUint8()

        estateVal = {}
        if (retCode == 0):
            estateId = di.getUint32()
            numFields = di.getUint16()
            
            for i in range(numFields):
                key = di.getString()
                #key = key[2:]
                #right why to do this???? ask Roger and/or Dave
                value = di.getString()
                found = di.getUint8()
                
                #print key;
                #print value;
                #print found;

                if found:
                    # create another datagram for this value
                    #vdg = PyDatagram(estateVal[i])
                    #vdgi = PyDatagramIterator(vdg)
                    # do something with this data
                    estateVal[key] = value
                
                    
            numHouses = di.getUint16()
            self.notify.debug("numHouses = %s" % numHouses)
            houseId = [None] * numHouses
            for i in range(numHouses):
                houseId[i] = di.getUint32()
                self.notify.debug("houseId = %s" % houseId[i])
                
            numHouseKeys = di.getUint16()
            self.notify.debug("numHouseKeys = %s" % numHouseKeys)
            houseKey = [None] * numHouseKeys
            for i in range(numHouseKeys):
                houseKey[i] = di.getString()

            numHouseVal = di.getUint16()
            assert (numHouseVal == numHouseKeys)
            tempHouseVal = [None] * numHouseVal
            for i in range(numHouseVal):
                numHouses2 = di.getUint16()
                assert(numHouses2 == numHouses)
                tempHouseVal[i] = [None] * numHouses
                for j in range(numHouses):
                    tempHouseVal[i][j] = di.getString()
                    # do we need a check for "value found" here?

            #print houseKey
            #print tempHouseVal

            numHouseFound = di.getUint16()


            # keep track of which attributes are found
            foundVal = [None] * numHouses
            for i in range(numHouses):
                foundVal[i] = [None] * numHouseVal
                
            # create empty dictionaries for each house
            houseVal = []
            for i in range(numHouses):
                houseVal.append({})
                
            for i in range(numHouseVal):
                hvLen = di.getUint16()
                for j in range(numHouses):
                    found = di.getUint8()
                    if found:
                        houseVal[j][houseKey[i]] = tempHouseVal[i][j]
                        foundVal[j][i] = 1
                    else:
                        foundVal[j][i] = 0

            numPets = di.getUint16()
            petIds = []
            for i in xrange(numPets):
                petIds.append(di.getUint32())

            # create estate with houses
            # and call DistributedEstateAI's initEstateData func

            # call function originally passed to getEstate
            callback(estateId, estateVal, numHouses, houseId, houseVal,
                     petIds, estateVal)
        else:
            print("ret code != 0, something went wrong with estate creation")

    def handleAvCatch(self, avId, zoneId, catch):
        """
        avId - ID of avatar to update
        zoneId - zoneId of the pond the catch was made in.
                This is used by the BingoManagerAI to
                determine which PBMgrAI needs to update
                the catch.
        catch - a fish tuple of (genus, species)
        returns: None
        
        This method instructs the BingoManagerAI to
        tell the appropriate PBMgrAI to update the
        catch of an avatar at the particular pond. This
        method is called in the FishManagerAI's
        RecordCatch method.
        """
        # Guard for publish
        if simbase.wantBingo:
            if self.bingoMgr:
                self.bingoMgr.setAvCatchForPondMgr(avId, zoneId, catch)
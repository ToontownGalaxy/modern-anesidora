""" SuitPlannerBase module:  contains common code that both the server
    and client use when managing a collection of suits."""

# AI code should not import ShowBaseGlobal because it creates a graphics window
# If you need panda classes use PandaModules instead
# from ShowBaseGlobal import *
from panda3d.core import *

import random
import string
from direct.directnotify import DirectNotifyGlobal
from toontown.hood import ZoneUtil

from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.hood import HoodUtil
from libpandadna import DNAStorage, DNAInteractiveProp, DNASuitPoint
from toontown.building import SuitBuildingGlobals

class SuitPlannerBase:
    """
    /////////////////////////////////////////////////////////////////////////
    //
    // SuitPlannerBase class:  manages all suits which exist within a single
    //  neighborhood (or street), this base version contains general code
    //  that both the server and client can use, such as path generation
    //  code, dna storage, path point type storage
    //
    /////////////////////////////////////////////////////////////////////////
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('SuitPlannerBase')
    SuitHoodInfo = [
        # TT is heavy on l, light on c
        # Street 2100 is a particularly long street.  Lots of room for cogs.
        [ 2100,                         # ZONE
          5,                            # MIN
          15,                           # MAX
          0,                            # BMIN
          5,                            # BMAX
          20,                           # BWEIGHT
          3,                            # SMAX
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 25, 25, 25, 25 ),           # TRACK
          ( 1, 2, 3 ),                  # LVL
          [],
          ],
        [ 2200,
          3,
          10,
          0,
          5,
          15,                           # BWEIGHT
          3,
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 10, 70, 10, 10 ),
          ( 1, 2, 3 ),
          [],
          ],
        [ 2300,
          3,
          10,
          0,
          5,
          15,                           # BWEIGHT
          3,
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 10, 10, 40, 40 ),
          ( 1, 2, 3 ),
          [],
          ],

        # Donalds dock
        # DD is heavy on c (2..4), m (3..6), light on l, s
        [ 1100,                         # ZONE
          1,                            # MIN
          5,                            # MAX
          0,                            # BMIN
          99,                           # BMAX
          100,                          # BWEIGHT
          4,                            # SMAX
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 90, 10, 0, 0 ),             # TRACK
          ( 2, 3, 4 ),                  # LVL
          [],
          ],
        [ 1200,
          1,
          5,
          0,
          99,
          100,                          # BWEIGHT
          4,
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 0, 0, 90, 10 ),
          ( 3, 4, 5, 6 ),
          [],
          ],
        [ 1300,
          1,
          5,
          0,
          99,
          100,                          # BWEIGHT
          4,
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 40, 40, 10, 10 ),
          ( 3, 4, 5, 6 ),
          [],
          ],

        # The Brrrgh
        # TB is heavy on c, light on l
        [ 3100,                         # ZONE
          1,                            # MIN
          5,                            # MAX
          0,                            # BMIN
          99,                           # BMAX
          100,                          # BWEIGHT
          4,                            # SMAX
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 90, 10, 0, 0 ),             # TRACK
          ( 5, 6, 7 ),                  # LVL
          [],
          ],
        [ 3200,
          1,
          5,
          0,
          99,
          100,                          # BWEIGHT
          4,
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 10, 20, 30, 40 ),
          ( 5, 6, 7 ),
          [],
          ],
        [ 3300,
          1,
          5,
          0,
          99,
          100,                          # BWEIGHT
          4,
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 5, 85, 5, 5 ),
          ( 7, 8, 9 ),
          [],
          ],

        # Minnies Melodyland
        # MM is heavy on m
        [ 4100,                         # ZONE
          1,                            # MIN
          5,                            # MAX
          0,                            # BMIN
          99,                           # BMAX
          100,                          # BWEIGHT
          4,                            # SMAX
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 0, 0, 50, 50 ),             # TRACK
          ( 2, 3, 4 ),                  # LVL
          [],
          ],
        [ 4200,
          1,
          5,
          0,
          99,
          100,                          # BWEIGHT
          4,
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 0, 0, 90, 10 ),
          ( 3, 4, 5, 6 ),
          [],
          ],
        [ 4300,
          1,
          5,
          0,
          99,
          100,                          # BWEIGHT
          4,
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 50, 50, 0, 0 ),
          ( 3, 4, 5, 6 ),
          [],
          ],

        # Daisy Gardens
        # DG is heavy on s (2..4), l (3..6)
        [ 5100,                         # ZONE
          1,                            # MIN
          5,                            # MAX
          0,                            # BMIN
          99,                           # BMAX
          100,                          # BWEIGHT
          4,                            # SMAX
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 0, 20, 10, 70 ),            # TRACK
          ( 2, 3, 4 ),                  # LVL
          [],
          ],
        [ 5200,                         # ZONE
          1,                            # MIN
          5,                            # MAX
          0,                            # BMIN
          99,                           # BMAX
          100,                          # BWEIGHT
          4,                            # SMAX
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 10, 70, 0, 20 ),            # TRACK
          ( 3, 4, 5, 6 ),               # LVL
          [],
          ],
        [ 5300,                         # ZONE
          1,                            # MIN
          5,                            # MAX
          0,                            # BMIN
          99,                           # BMAX
          100,                          # BWEIGHT
          4,                            # SMAX
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          # Mostly sellbot since it is connected to Sellbot HQ
          ( 5, 5, 5, 85 ),              # TRACK
          ( 3, 4, 5, 6 ),               # LVL
          [],
          ],

        # Dreamland
        [ 9100,                         # ZONE
          1,                            # MIN
          5,                            # MAX
          0,                            # BMIN
          99,                           # BMAX
          100,                          # BWEIGHT
          4,                            # SMAX
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 25, 25, 25, 25 ),           # TRACK
          ( 6, 7, 8, 9 ),               # LVL
          [],
          ],

        [ 9200,                         # ZONE
          1,                            # MIN
          5,                            # MAX
          0,                            # BMIN
          99,                           # BMAX
          100,                          # BWEIGHT
          4,                            # SMAX
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          # Mostly cashbot since it is connected to Cashbot HQ
          ( 5, 5, 85, 5 ),              # TRACK
          ( 6, 7, 8, 9 ),               # LVL
          [],
          ],

        # Sellbot HQ Exterior
        [ 11000,                        # ZONE
          3,                            # MIN
          15,                           # MAX
          0,                            # BMIN
          0,                            # BMAX
          0,                            # BWEIGHT
          4,                            # SMAX
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 0, 0, 0, 100 ),             # TRACK
          ( 4, 5, 6 ),                  # LVL
          [],
          ],
        [ 11200,                        # ZONE
          10,                           # MIN
          20,                           # MAX
          0,                            # BMIN
          0,                            # BMAX
          0,                            # BWEIGHT
          4,                            # SMAX
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 0, 0, 0, 100 ),             # TRACK
          ( 4, 5, 6 ),                  # LVL
          [],
          ],

        # Cash HQ Exterior
        [ 12000,                        # ZONE
          10,                           # MIN
          20,                           # MAX
          0,                            # BMIN
          0,                            # BMAX
          0,                            # BWEIGHT
          4,                            # SMAX
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 0, 0, 100, 0 ),             # TRACK
          ( 7, 8, 9 ),                  # LVL
          [],
          ],

        # Law HQ Exterior
        [ 13000,                        # ZONE
          10,                           # MIN
          20,                           # MAX
          0,                            # BMIN
          0,                            # BMAX
          0,                            # BWEIGHT
          4,                            # SMAX
          ( 1, 5, 10, 40, 60, 80 ),     # JCHANCE
          ( 0, 100, 0, 0 ),             # TRACK
          ( 8, 9, 10 ),                 # LVL
          [],
          ],

        ]
   # index values into the SuitHoodInfo struct above for each type of value
    #
    SUIT_HOOD_INFO_ZONE    = 0
    SUIT_HOOD_INFO_MIN     = 1
    SUIT_HOOD_INFO_MAX     = 2
    SUIT_HOOD_INFO_BMIN    = 3
    SUIT_HOOD_INFO_BMAX    = 4
    SUIT_HOOD_INFO_BWEIGHT = 5
    SUIT_HOOD_INFO_SMAX    = 6
    SUIT_HOOD_INFO_JCHANCE = 7
    SUIT_HOOD_INFO_TRACK   = 8
    SUIT_HOOD_INFO_LVL     = 9
    SUIT_HOOD_INFO_HEIGHTS = 10





    # We need the total of all BWEIGHT values so we can compute
    # weighted chances properly.  And, we keep the total weights as
    # modified per track, for cases when we want to choose a street to
    # prefer a particular kind of suit building over any other kind.
    TOTAL_BWEIGHT = 0

    # We also need the same count, weighted by the chance of a suit of
    # a particular track appearing in that zone.  This enables us to
    # choose a suitable street to hold a building of a particular
    # track.
    TOTAL_BWEIGHT_PER_TRACK = [0, 0, 0, 0]

    # And again, weighted by the chance of a suit of an appropriate
    # level to create a building of a particular height.
    TOTAL_BWEIGHT_PER_HEIGHT = [0, 0, 0, 0, 0]

    for currHoodInfo in SuitHoodInfo:
        weight = currHoodInfo[SUIT_HOOD_INFO_BWEIGHT]
        tracks = currHoodInfo[SUIT_HOOD_INFO_TRACK]
        levels = currHoodInfo[SUIT_HOOD_INFO_LVL]

        # levels is the list of suit levels that may be encountered in
        # this zone.  There's an equal weight chance of each level
        # suit appearing, and each level suit makes a building of the
        # corresponding level, which has a particular chance of being
        # any of a specified number of floors.  Crunch these numbers
        # down into the overall chance of a particular building height
        # on this streeet.
        heights = [0, 0, 0, 0, 0]
        for level in levels:
            minFloors, maxFloors = SuitBuildingGlobals.SuitBuildingInfo[level - 1][0]
            # Remember that buildingHeight is numFloors - 1
            for i in range(minFloors - 1, maxFloors):
                heights[i] += 1

        # Now that we've computed this heights list, store it back on
        # the global structure for future reference.
        currHoodInfo[SUIT_HOOD_INFO_HEIGHTS] = heights

        TOTAL_BWEIGHT += weight
        TOTAL_BWEIGHT_PER_TRACK[0] += weight * tracks[0]
        TOTAL_BWEIGHT_PER_TRACK[1] += weight * tracks[1]
        TOTAL_BWEIGHT_PER_TRACK[2] += weight * tracks[2]
        TOTAL_BWEIGHT_PER_TRACK[3] += weight * tracks[3]

        TOTAL_BWEIGHT_PER_HEIGHT[0] += weight * heights[0]
        TOTAL_BWEIGHT_PER_HEIGHT[1] += weight * heights[1]
        TOTAL_BWEIGHT_PER_HEIGHT[2] += weight * heights[2]
        TOTAL_BWEIGHT_PER_HEIGHT[3] += weight * heights[3]
        TOTAL_BWEIGHT_PER_HEIGHT[4] += weight * heights[4]
    def __init__( self ):

        # initialize some values that we will be using
        #
        self.suitWalkSpeed = ToontownGlobals.SuitWalkSpeed

        # now load up the dna file for the neighborhood that this suit
        # planner is created for
        #
        self.dnaStore = None

        # keep a map of point indexes and the actual point so when
        # suits need to look up information from a point's index, they
        # can do it quickly without having to ask the dnaStore
        #
        self.pointIndexes = {}

        return None

    def setupDNA( self ):
        """
        ////////////////////////////////////////////////////////////////////
        // Function:    load up DNA information for the neighborhood that
        //              this suit planner is in control of.  the DNA
        //              contains suit path information as well as vis
        //              group (zone) informations
        // Parameters:  none
        // Changes:
        ////////////////////////////////////////////////////////////////////
        """

        if self.dnaStore:
            return None

        self.dnaStore = DNAStorage()
        dnaFileName = self.genDNAFileName()
        try:
            simbase.air.loadDNAFileAI( self.dnaStore, dnaFileName)
        except:
            loader.loadDNAFileAI( self.dnaStore, dnaFileName)


        # now create vis group (zone) information
        self.initDNAInfo()

    def genDNAFileName( self ):
        """
        ////////////////////////////////////////////////////////////////////
        // Function:    determines the name of the DNA file that should
        //              be loaded for the neighborhood that this suit
        //              planner manages
        // Parameters:  none
        // Changes:     none
        ////////////////////////////////////////////////////////////////////
        """
        # This code might run on the AI or on the client.
        try:
            return simbase.air.genDNAFileName(self.getZoneId())

        except:
            # do some number manipulation of my zone id already given
            # to me and figure out which dna file to load

            zoneId = ZoneUtil.getCanonicalZoneId(self.getZoneId())
            hoodId = ZoneUtil.getCanonicalHoodId(zoneId)
            hood = ToontownGlobals.dnaMap[hoodId]
            phase = ToontownGlobals.streetPhaseMap[hoodId]
            if hoodId == zoneId:
                zoneId = "sz"

            return "phase_%s/dna/%s_%s.dna" % (phase, hood, zoneId)


    def getZoneId( self ):
        """
        ////////////////////////////////////////////////////////////////////
        // Function:    intended to be overridden by any inheriting suit
        //              planner class, and that class should be a
        //              distributed object or at least have an attribute
        //              named 'zoneId'
        // Parameters:  none
        // Changes:
        ////////////////////////////////////////////////////////////////////
        """
        return self.zoneId

    def setZoneId( self, zoneId ):
        self.notify.debug( "setting zone id for suit planner" )
        self.zoneId = zoneId
        self.setupDNA()

    def extractGroupName(self, groupFullName):
        # The Idea here is that group names may have extra flags associated
        # with them that tell more information about what is special about
        # the particular vis zone. A normal vis zone might just be "13001",
        # but a special one might be "14356:safe_zone" or
        # "345:safe_zone:exit_zone"... These are hypotheticals. The main
        # idea is that there are colon separated flags after the initial
        # zone name.
        return groupFullName

    def initDNAInfo( self ):
        """
        ////////////////////////////////////////////////////////////////////
        // Function:    load up vis group information into a dictionary
        //              copied from HoodMgr.py
        // Parameters:  dnaStore, the dna storage structure to use
        // Changes:
        ////////////////////////////////////////////////////////////////////
        """
        numGraphs = self.dnaStore.discoverContinuity()
        if numGraphs != 1:
            self.notify.info("zone %s has %s disconnected suit paths." % (self.zoneId, numGraphs))

        # Construct a dictionary of zone ids to battle cell center points
        self.battlePosDict = {}
        self.cellToGagBonusDict = {}
        #self.dnaStore.printSuitPointStorage()
        for i in range(self.dnaStore.getNumDNAVisGroupsAI()):
            vg = self.dnaStore.getDNAVisGroupAI(i)
            zoneId = int(self.extractGroupName(vg.getName()))
            # There is only 1 battle cell per zone
            if (vg.getNumBattleCells() == 1):
                battleCell = vg.getBattleCell(0)
                self.battlePosDict[zoneId] = vg.getBattleCell(0).getPos()
            elif (vg.getNumBattleCells() > 1):
                self.notify.warning('multiple battle cells for zone: %d' % zoneId)
                # Just pick the first one
                self.battlePosDict[zoneId] = vg.getBattleCell(0).getPos()
            if True:
                # lets find the interactive props connected to this battle cell
                for i in range(vg.getNumChildren()):
                    childDnaGroup = vg.at(i)
                    if (isinstance(childDnaGroup, DNAInteractiveProp)):
                        self.notify.debug("got interactive prop %s" % childDnaGroup)
                        battleCellId = childDnaGroup.getCellId()
                        if battleCellId == -1:
                            self.notify.warning(
                                "interactive prop %s  at %s not associated with a a battle" %
                                (childDnaGroup, zoneId))
                        elif battleCellId == 0:
                            if zoneId in self.cellToGagBonusDict:
                                self.notify.error(
                                    "FIXME battle cell at zone %s has two props %s %s linked to it" %
                                    (zoneId, self.cellToGagBonusDict[zoneId], childDnaGroup))
                            else:
                                # based on the name of the prop, figure out which gag track bonus
                                name = childDnaGroup.getName()
                                propType = HoodUtil.calcPropType(name)
                                if propType in ToontownBattleGlobals.PropTypeToTrackBonus:
                                    trackBonus = ToontownBattleGlobals.PropTypeToTrackBonus[propType]
                                    self.cellToGagBonusDict[zoneId] = trackBonus

        # Now that we have extracted the vis groups we do not need
        # the dnaStore to keep them around
        self.dnaStore.resetDNAGroups()
        self.dnaStore.resetDNAVisGroups()
        self.dnaStore.resetDNAVisGroupsAI()

        # now load up the suit path points, separate them into types
        #
        self.streetPointList = []
        self.frontdoorPointList = []
        self.sidedoorPointList = []
        self.cogHQDoorPointList = []

        numPoints = self.dnaStore.getNumSuitPoints()
        for i in range(numPoints):
            point = self.dnaStore.getSuitPointAtIndex(i)
            if (point.getPointType() == DNASuitPoint.FRONTDOORPOINT):
                self.frontdoorPointList.append(point)
            elif (point.getPointType() == DNASuitPoint.SIDEDOORPOINT):
                self.sidedoorPointList.append(point)
            elif (point.getPointType() == DNASuitPoint.COGHQINPOINT or \
                  point.getPointType() == DNASuitPoint.COGHQOUTPOINT):
                self.cogHQDoorPointList.append(point)
            else:
                self.streetPointList.append(point)

            self.pointIndexes[ point.getIndex() ] = point

        # perform a simple path test to make sure we can properly
        # generate a path from two points given to us by the DNAStorage
        #
#        self.performPathTest()

        return None


    def performPathTest( self ):
        """
        ////////////////////////////////////////////////////////////////////
        // Function:    test out path generation as well as travel time
        //              calculation for the current dnaStore information
        // Parameters:  none
        // Changes:
        ////////////////////////////////////////////////////////////////////
        """

        if not self.notify.getDebug():
            return None

        #self.notify.debug( 'street points: ' + str( self.streetPointList ) )
        #self.notify.debug( 'front door points: ' +
        #                   str( self.frontdoorPointList ) )
        #self.notify.debug( 'side door points: ' +
        #                   str( self.sidedoorPointList ) )

        # create a simple path which will be only used for
        # testing the getSuitPath function of the dnaStorage
        #
        startAndEnd = self.pickPath()
        if not startAndEnd:
            return None

        startPoint = startAndEnd[ 0 ]
        endPoint = startAndEnd[ 1 ]

        path = self.dnaStore.getSuitPath( startPoint, endPoint )

#        print path

        # now print out travel time for each edge in the resulting path
        # as well as which zone each edge is in
        #
        numPathPoints = path.getNumPoints()
        for i in range( numPathPoints - 1 ):
            zone = self.dnaStore.getSuitEdgeZone(
                                   path.getPointIndex(i),
                                   path.getPointIndex(i+1) )
            travelTime = self.dnaStore.getSuitEdgeTravelTime(
                                   path.getPointIndex(i),
                                   path.getPointIndex(i+1),
                                   self.suitWalkSpeed )
            self.notify.debug(
                'edge from point ' + repr(i) +
                ' to point ' + repr(i+1) +
                ' is in zone: ' + repr(zone) +
                ' and will take ' + repr(travelTime) +
                ' seconds to walk.' )

        return None


    def genPath(self, startPoint, endPoint, minPathLen, maxPathLen):
        """
        ////////////////////////////////////////////////////////////////////
        // Function:    generate a path using the local dnaStorage given
        //              the start and end points
        // Parameters:  none
        // Changes:
        ////////////////////////////////////////////////////////////////////
        """
        return self.dnaStore.getSuitPath(startPoint, endPoint, minPathLen, maxPathLen)

    def getDnaStore( self ):
        """
        ////////////////////////////////////////////////////////////////////
        // Function:    get the dnaStore from the suit planner, create the
        //              dnaStore if it has not already been loaded
        // Parameters:  none
        // Changes:
        ////////////////////////////////////////////////////////////////////
        """
#        if self.dnaStore == None:
#            self.setupDNA()
        return self.dnaStore

# history
#
# 12Feb01    jlbutler    created.
#



































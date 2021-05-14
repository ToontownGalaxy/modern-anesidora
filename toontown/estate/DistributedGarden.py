from panda3d.core import *
from toontown.toonbase.ToonBaseGlobal import *
from direct.gui.DirectGui import *
from panda3d.core import *
from direct.distributed.ClockDelta import *
from toontown.toonbase import ToontownGlobals
from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM
from direct.fsm import State
from toontown.toon import Toon
from direct.showbase import RandomNumGen
from toontown.toonbase import TTLocalizer
import random
import random
import pickle
from direct.showbase import PythonUtil
from toontown.hood import Place
from . import Estate
from . import HouseGlobals

class DistributedGarden(DistributedObject.DistributedObject):
    """
    This is the garden object on the client
    """
    notify = directNotify.newCategory("DistributedGarden")

    def __init__(self, cr):
        self.notify.debug("init")
        DistributedObject.DistributedObject.__init__(self, cr)
        self.lt = base.localAvatar

        self.props = []
        self.pos = None
        self.radius = 0
        self.gridCells = 20
        # initialize a 2d array that indicates whether a
        # i,j slot in the garden is taken
        self.propTable = [None] * self.gridCells
        for i in range(len(self.propTable)):
            self.propTable[i] = [None] * self.gridCells
        self.dx = 1.0/self.gridCells
        self.occupied = []
        
    def generate(self):
        DistributedObject.DistributedObject.generate(self)

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)

    def disable(self):
        DistributedObject.DistributedObject.disable(self)

    def unload(self):
        pass
    
    def delete(self):
        for prop in self.props:
            prop[0].removeNode()
            del prop[0]
            del prop
        del self.props
        self.props = None
        
        self.unload()

    def sendNewProp(self, prop, x, y, z):
        self.notify.debug("sendNewProp")
        print(("new prop (%d) = %s,%s,%s" % (prop,x,y,z)))
        if prop == HouseGlobals.PROP_ICECUBE:
            model = loader.loadModel("phase_8/models/props/icecube.bam")
        elif prop == HouseGlobals.PROP_FLOWER:
            model = loader.loadModel("phase_8/models/props/flower_treasure.bam")
        elif prop == HouseGlobals.PROP_SNOWFLAKE:
            model = loader.loadModel("phase_8/models/props/snowflake_treasure.bam")

        model.reparentTo(hidden)
        model.setPos(x,y,z)
        model.setScale(.2)
        model.setBillboardPointEye()
        model.reparentTo(render)
        self.props.append([model,x,y,z])

    def getPropPos(self, i, j):
        pos = [(self.pos[0] - self.radius + 2*self.radius*i),
               (self.pos[1] - self.radius + 2*self.radius*j),
               self.pos[2]]
        return pos

    def loadProp(self, prop, i, j):
        pos = self.getPropPos(i,j)
        if prop == HouseGlobals.PROP_ICECUBE:
            model = loader.loadModel("phase_8/models/props/icecube.bam")
        elif prop == HouseGlobals.PROP_FLOWER:
            model = loader.loadModel("phase_8/models/props/flower_treasure.bam")
        elif prop == HouseGlobals.PROP_SNOWFLAKE:
            model = loader.loadModel("phase_8/models/props/snowflake_treasure.bam")
        else:
            self.notify.error("cant find prop: %s" % prop)

        model.reparentTo(hidden)
        model.setPos(pos[0],pos[1],pos[2])
        model.setScale(.2)
        model.setBillboardPointEye()
        model.reparentTo(render)

    # the client should call this function to add a prop
    # to the garden.
    def setAddProp(self, prop, i, j):
        self.notify.debug("addProp")
        self.props.append([prop, i, j])
        self.loadProp(prop, i, j)
        
        # update the client and server
        self.b_setProps(self, props)

    def b_setProps(self, props):
        self.notify.debug("b_setProps")
        # local
        self.setProps(props)
        # distributed
        self.d_setProps(props)

    def d_setProps(self, props):
        self.notify.debug("d_setProps")
        # flatten the array to look like
        # [type1, i1, j1, type2, i2, j2, ....typeN, iN, jN]
        aProps = []
        for prop in props:
            aProps = aProps + prop
        self.sendUpdate("setProps", [aProps])
        
    def setProps(self, props):
        self.notify.debug("setProps")
        self.props = props
        # fill table
        for prop in self.props:
            pInd,i,j = prop
            self.propTable[i,j] = pInd
        
    
        
        
        

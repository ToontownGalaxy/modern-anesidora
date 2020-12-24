

from direct.directnotify import DirectNotifyGlobal
from direct.task import Task
from . import DistributedSwitchBase
from . import DistributedSwitchAI


class DistributedButtonAI(DistributedSwitchAI.DistributedSwitchAI):
    """
    DistributedButtonAI class:  The server side representation
    of a Cog HQ button.  This is the object that remembers what the
    button is doing.  The DistributedButton, is the client side
    version.
    """
        
    # These stubbed out functions are not used on the AI (Client Only):
    setColor = DistributedSwitchBase.stubFunction
    setModel = DistributedSwitchBase.stubFunction

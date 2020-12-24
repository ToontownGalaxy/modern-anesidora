
from direct.directnotify import DirectNotifyGlobal
from toontown.building.SuitPlannerInteriorAI import SuitPlannerInteriorAI


class SuitPlannerCogdoInteriorAI(SuitPlannerInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SuitPlannerCogdoInteriorAI')

    def __init__(self, layout, difficulty, track, zoneId):
        self._cogdoLayout = layout
        SuitPlannerInteriorAI.__init__(self, self._cogdoLayout.getNumGameFloors() , difficulty, track, zoneId, 1)

    def _genSuitInfos(self, floors, difficulty, track):
        SuitPlannerInteriorAI._genSuitInfos(self, self._cogdoLayout.getNumFloors(), difficulty, track)


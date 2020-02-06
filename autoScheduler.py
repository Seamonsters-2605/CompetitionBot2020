import seamonsters as sea 

class Action(sea.State):

    def __init__(self, name, function, key, coord=None):
        self.name = name
        self.function = function
        # key is the action type as a string
        self.key = key
        self.coord = coord

class AutoScheduler:

    def __init__(self):
        self.actionList = []
        self.runningAction = None
        self.updateCallback = lambda: None
        self.idleFunction = lambda: None

    def runSchedule(self):
        try:
            while True:
                if len(self.actionList) == 0:
                    self.runningAction = None
                    self.updateCallback()
                    while len(self.actionList) == 0:
                        self.idleFunction()
                        yield
                        continue
                self.runningAction = self.actionList[0]
                self.updateCallback()
                yield from self.runningAction.function()
                if self.runningAction in self.actionList:
                    self.actionList.remove(self.runningAction)
        finally:
            self.runningAction = None

    # converts the schedule into something that can be saved in a json file
    def saveSchedule(self):
        schedulePresets = []
        for action in self.actionList:
            newAction = {
                    "key" : action.key,
                    "coord" : []
                }
            if action.coord is not None:
                newAction["coord"] = [action.name, action.coord.x, action.coord.y, action.coord.angle]
            schedulePresets.append(newAction)
        return schedulePresets
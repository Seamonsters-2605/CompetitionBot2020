import remi.gui as gui
import math
import coordinates
import seamonsters as sea
import drivetrain
import autoActions

FIELD_WIDTH = 520
FIELD_HEIGHT = 260
FIELD_PIXELS_PER_FOOT = 10

class CompetitionDashboard(sea.Dashboard):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, css=True, **kwargs)

    def sectionBox(self):
        vbox = gui.VBox()
        vbox.style['border'] = '2px solid gray'
        vbox.style['border-radius'] = '0.5em'
        vbox.style['margin'] = '0.5em'
        vbox.style['padding'] = '0.2em'
        return vbox

    def main(self, robot, appCallback):
        self.robot = robot

        root = gui.HBox(width = 1000, margin = "0px auto")
        root.style['align-items'] = 'stretch'

        leftSide = gui.VBox()
        leftSide.style['align-items'] = 'stretch'

        middle = gui.VBox()

        rightSide = gui.VBox()
        rightSide.style['align-items'] = 'flex-start'

        self.motorDataDict = { \
            "ampRow" : None,
            "tempRow" : None,
            "maxAmpRow" : None,
            "maxTempRow" : None,
            "amp" : [],
            "temp" : [],
            "maxAmp" : [],
            "maxTemp" : []
            }

        self.updateSchedulerFlag = False

        leftSide.append(self.initStats(robot))
        leftSide.append(self.initLedControl(robot))
        leftSide.append(self.initScheduler(robot))

        middle.append(self.initCamera(robot))
        middle.append(self.initFieldMap(robot))

        rightSide.append(self.initManual(robot))
        rightSide.append(self.initTest(robot))

        root.append(leftSide)
        root.append(middle)
        root.append(rightSide)

        appCallback(self)
        return root

    # runs every time the dashboard is updated
    def idle(self):
        pf = self.robot.pathFollower
        self.updateRobotPosition(
            pf.robotX, pf.robotY, pf.robotAngle)

        if self.updateSchedulerFlag:
            self.updateScheduler()
            self.updateSchedulerFlag = False

        # updates the values in self.motorDataTable
        for motorNum in range(6):

            ampRow = self.motorDataTable.children[self.motorDataDict["ampRow"]]
            ampItem = ampRow.children[self.motorDataDict["amp"][motorNum]]
            ampItem.set_text(str(self.robot.motorData[motorNum]["amps"]))

            tempRow = self.motorDataTable.children[self.motorDataDict["tempRow"]]
            tempItem = tempRow.children[self.motorDataDict["temp"][motorNum]]
            tempItem.set_text(str(self.robot.motorData[motorNum]["temp"]))

            maxAmpRow = self.motorDataTable.children[self.motorDataDict["maxAmpRow"]]
            maxAmpItem = maxAmpRow.children[self.motorDataDict["maxAmp"][motorNum]]
            maxAmpItem.set_text(str(self.robot.motorData[motorNum]["maxAmp"]))

            maxTempRow = self.motorDataTable.children[self.motorDataDict["maxTempRow"]]
            maxTempItem = maxTempRow.children[self.motorDataDict["maxTemp"][motorNum]]
            maxTempItem.set_text(str(self.robot.motorData[motorNum]["maxTemp"]))

    def initManual(self, robot):
        manualBox = self.sectionBox()

        driveControlBox = gui.VBox(gui.Label("Drive controls"))
        gearButtons = []
        speedButtons = []
        compressorButtons = []
        
        self.gearGroup = sea.ToggleButtonGroup()
        for mode in robot.driveGears.keys():
            button = gui.Button(mode)
            button.set_on_click_listener(robot.c_changeGear)
            gearButtons.append(button)
            self.gearGroup.addButton(button)
        
        self.speedGroup = sea.ToggleButtonGroup()
        for speed in robot.driveGears[robot.driveMode].keys():
            button = gui.Button(speed)
            button.set_on_click_listener(robot.c_changeSpeed)
            speedButtons.append(button)
            self.speedGroup.addButton(button)

        self.compressorGroup = sea.ToggleButtonGroup()
        for mode in ["start","stop"]:
            button = gui.Button(mode)
            button.set_on_click_listener(robot.c_compressor)
            compressorButtons.append(button)
            self.compressorGroup.addButton(button)
        
        gearBox = sea.hBoxWith(gui.Label("Gears:"), gearButtons)
        speedBox = sea.hBoxWith(gui.Label("Speed:"), speedButtons)
        compressorBox = sea.hBoxWith(gui.Label("Compressor:"), compressorButtons)

        driveControlBox.append(gearBox)
        driveControlBox.append(speedBox)
        driveControlBox.append(compressorBox)

        manualBox.append(driveControlBox)
        return manualBox

    def initCamera(self, robot):
        cameraBox = self.sectionBox()

        videoFeedBox = gui.HBox()
        videoFeed = gui.Image('http://10.26.5.6:5800/')
        videoFeedBox.append(videoFeed)

        cameraBox.append(videoFeedBox)
        return cameraBox

    def initTest(self, robot):
        testBox = self.sectionBox()

        motorNumberIn = gui.Input()
        motorSelectionBox = sea.hBoxWith(gui.Label("Motor Number:"), motorNumberIn)

        motorSpeedSlider = gui.Slider(default_value=0, min= -1.0, max= 1.0, step= 0.05)
        testButton = gui.Button("Test")
        motorSpeedBox = sea.hBoxWith(testButton, gui.Label("Speed:"), motorSpeedSlider)

        def testMotor(button):
            robot.superDrive.disable()
            try:
                motorNum = int(motorNumberIn.get_value()) - 1
            except:
                print("Motor number incorrect")
                return

            wheelNum = 0
            if motorNum >= 3:
                wheelNum = 1
                motorNum -= 3

            if motorNum < 0 or motorNum >= 3:
                print("Motor number incorrect")
                return
        
            robot.testSettings["wheelNum"] = wheelNum
            robot.testSettings["motorNum"] = motorNum
            robot.testSettings["speed"] = float(motorSpeedSlider.get_value())
            
        testButton.set_on_click_listener(testMotor)

        testBox.append(gui.Label("Test"))
        testBox.append(motorSelectionBox)
        testBox.append(motorSpeedBox)
        return testBox

    def initFieldMap(self, robot):
        fieldBox = self.sectionBox()

        robotBox = gui.HBox()
        fieldBox.append(robotBox)

        setPositionBtn = gui.Button("Set Robot to Cursor")
        setPositionBtn.set_on_click_listener(self.c_setRobotPosition)
        robotBox.append(setPositionBtn)

        def setCursorAngle(button, angle):
            self.selectedCoord.angle = angle
            self.updateCursorPosition()

        leftBtn = gui.Button('<')
        leftBtn.set_on_click_listener(setCursorAngle, math.radians(90))
        robotBox.append(leftBtn)
        rightBtn = gui.Button('>')
        rightBtn.set_on_click_listener(setCursorAngle, math.radians(-90))
        robotBox.append(rightBtn)
        upBtn = gui.Button('^')
        upBtn.set_on_click_listener(setCursorAngle, 0)
        robotBox.append(upBtn)
        downBtn = gui.Button('v')
        downBtn.set_on_click_listener(setCursorAngle, math.radians(180))
        robotBox.append(downBtn)

        self.fieldSvg = gui.Svg(FIELD_WIDTH, FIELD_HEIGHT)
        self.fieldSvg.set_on_mousedown_listener(self.mouse_down_listener)
        fieldBox.append(self.fieldSvg)

        self.image = gui.SvgShape(0, 0)
        self.image.type = 'image'
        self.image.attributes['width'] = FIELD_WIDTH
        self.image.attributes['height'] = FIELD_HEIGHT
        self.image.attributes['xlink:href'] = '/res:field.PNG'
        self.fieldSvg.append(self.image)

        self.targetPoints = coordinates.targetPoints
        for point in self.targetPoints:
            point = fieldToSvgCoordinates(point.x,point.y)
            wp_dot = gui.SvgCircle(point[0], point[1], 5)
            wp_dot.attributes['fill'] = 'green'
            self.fieldSvg.append(wp_dot)

        self.cursorArrow = Arrow('red')
        self.fieldSvg.append(self.cursorArrow)

        self.robotArrow = Arrow('green')
        self.fieldSvg.append(self.robotArrow)

        self.robotPathLines = []

        self.selectedCoord = coordinates.FieldCoordinate("Center", 0, 0, math.radians(-90))
        self.updateCursorPosition()

        return fieldBox

    def initScheduler(self, robot):
        schedulerBox = self.sectionBox()

        controlBox = gui.HBox()
        schedulerBox.append(controlBox)
        manualModeBtn = gui.Button("Manual")
        manualModeBtn.set_on_click_listener(robot.c_manualMode)
        controlBox.append(manualModeBtn)
        autoModeBtn = gui.Button("Auto")
        autoModeBtn.set_on_click_listener(robot.c_autoMode)
        controlBox.append(autoModeBtn)

        self.controlModeGroup = sea.ToggleButtonGroup()
        self.controlModeGroup.addButton(manualModeBtn, "manual")
        self.controlModeGroup.addButton(autoModeBtn, "auto")

        hbox = gui.HBox()
        hbox.style['align-items'] = 'flex-start'
        schedulerBox.append(hbox)

        addActionBox = gui.VBox()
        hbox.append(addActionBox)

        self.autoSpeed = 6
        def slowSpeed():
            self.autoSpeed = 3
        def mediumSpeed():
            self.autoSpeed = 6
        def fastSpeed():
            self.autoSpeed = 8

        speedTabBox = gui.TabBox()
        speedTabBox.add_tab(gui.Widget(), "Slow", slowSpeed)
        speedTabBox.add_tab(gui.Widget(), "Med", mediumSpeed)
        speedTabBox.add_tab(gui.Widget(), "Fast", fastSpeed)
        speedTabBox.select_by_index(1)
        addActionBox.append(speedTabBox)

        addActionBox.append(gui.Label("Auto actions:"))

        self.genericActionList = gui.ListView()
        self.genericActionList.append("Drive to Point", "drivetopoint")
        self.genericActionList.append("Rotate in place", "rotate")
        index = 0
        for action in robot.genericAutoActions:
            self.genericActionList.append(gui.ListItem(action.name), str(index))
            index += 1
        self.genericActionList.set_on_selection_listener(self.c_addGenericAction)
        addActionBox.append(self.genericActionList)

        hbox.append(gui.HBox(width=10))

        scheduleListBox = gui.VBox()
        hbox.append(scheduleListBox)
        clearScheduleBox = gui.HBox()
        clearScheduleBox.style['align-items'] = 'flex-end'
        scheduleListBox.append(clearScheduleBox)
        clearScheduleBox.append(gui.Label("Schedule:"))
        clearScheduleBtn = gui.Button("Clear")
        clearScheduleBtn.set_on_click_listener(self.c_clearSchedule)
        clearScheduleBox.append(clearScheduleBtn)

        self.schedulerList = gui.ListView()
        self.schedulerList.set_on_selection_listener(self.c_removeAction)
        scheduleListBox.append(self.schedulerList)
        
        return schedulerBox


    def initLedControl(self, robot):
        ledBox = self.sectionBox()

        ledInputBox = sea.hBoxWith(gui.Label("LED Control"))
        ledSet = gui.Button("Set")
        ledIn = gui.Input()

        def ledSetValue(button):
            robot.ledInput = float(ledIn.get_value())

        ledSet.set_on_click_listener(ledSetValue)

        ledInputBox.append(ledSet)
        ledInputBox.append(ledIn)

        ledBox.append(ledInputBox)

        return ledBox

    def initStats(self, robot):
        statsBox = self.sectionBox()

        motorDataBox = sea.vBoxWith(gui.Label("Motor Data"))
        self.motorDataTable = gui.Table()
        motorNumRow = gui.TableRow(gui.TableItem("Motor Number:"))
        motorAmpRow = gui.TableRow(gui.TableItem("Amp Draw:"))
        motorTempRow = gui.TableRow(gui.TableItem("Temp:"))
        motorMaxAmpRow = gui.TableRow(gui.TableItem("Max Amp Draw:"))
        motorMaxTempRow = gui.TableRow(gui.TableItem("Max Temp:"))

        self.motorDataTable.append(motorNumRow)
        self.motorDataDict["ampRow"] = self.motorDataTable.append(motorAmpRow)
        self.motorDataDict["tempRow"] = self.motorDataTable.append(motorTempRow)
        self.motorDataDict["maxAmpRow"] = self.motorDataTable.append(motorMaxAmpRow)
        self.motorDataDict["maxTempRow"] = self.motorDataTable.append(motorMaxTempRow)

        for motorNum in range(6):
            motorNumRow.append(gui.TableItem(str(motorNum + 1)))
            self.motorDataDict["amp"].append(motorAmpRow.append(gui.TableItem("")))
            self.motorDataDict["temp"].append(motorTempRow.append(gui.TableItem("")))
            self.motorDataDict["maxAmp"].append(motorMaxAmpRow.append(gui.TableItem("")))
            self.motorDataDict["maxTemp"].append(motorMaxTempRow.append(gui.TableItem("")))
        
        motorDataBox.append(self.motorDataTable)

        statsBox.append(motorDataBox)
        return statsBox

    def updateRobotPosition(self, robotX, robotY, robotAngle):
        self.robotArrow.setPosition(robotX, robotY, robotAngle)

    def updateCursorPosition(self):
        coord = self.selectedCoord
        self.cursorArrow.setPosition(
            coord.x, coord.y, coord.angle)

    def updateScheduler(self):
        scheduler = self.robot.autoScheduler
        self.schedulerList.empty()

        for line in self.robotPathLines:
            self.fieldSvg.remove_child(line)
        self.robotPathLines.clear()
        lineX, lineY = fieldToSvgCoordinates(self.robotArrow.x, self.robotArrow.y)

        index = 0
        for action in scheduler.actionList:
            name = action.name
            if action == scheduler.runningAction:
                name = "* " + name
            listItem = gui.ListItem(name)
            self.schedulerList.append(listItem, str(index))
            lineX, lineY = self.actionLines(lineX, lineY, action)
            index += 1

    def actionLines(self, lineX, lineY, action):
        if action.coord is not None:
            x1, y1 = fieldToSvgCoordinates(action.coord.x, action.coord.y)
            line = gui.SvgLine(lineX, lineY, x1, y1)
            line.set_stroke(width=3)
            self.robotPathLines.append(line)
            self.fieldSvg.append(line)
            lineX, lineY = x1, y1
        return lineX, lineY

    # Callbacks

    def c_setRobotPosition(self, button):
        coord = self.selectedCoord
        self.robot.pathFollower.setPosition(
            coord.x, coord.y, coord.angle)

    def mouse_down_listener(self,widget,x,y):
        x, y = svgToFieldCoordinates(x, y)
        self.selectedCoord = coordinates.FieldCoordinate("Selected",
            x, y, self.selectedCoord.angle)
        for point in self.targetPoints:
            if math.hypot(x - point.x, y - point.y) < 1:
                self.selectedCoord = point
        self.updateCursorPosition()
    
    def c_addGenericAction(self, listview, key, driveCoordinate=None):
        if driveCoordinate is None:
            driveCoordinate = self.selectedCoord
        if key == "drivetopoint":
            action = autoActions.createDriveToPointAction(
                self.robot.pathFollower, driveCoordinate, self.autoSpeed)
        elif key == "rotate":
            action = autoActions.createRotateInPlaceAction(
                self.robot.pathFollower, driveCoordinate.angle)
        else:
            action = self.robot.genericAutoActions[int(key)]
        self.robot.autoScheduler.actionList.append(action)
        self.updateScheduler()

    def c_clearSchedule(self, button):
        self.robot.autoScheduler.actionList.clear()
        self.updateScheduler()

    def c_removeAction(self, listview, key):
        index = int(key)
        actionList = self.robot.autoScheduler.actionList
        if index < len(actionList):
            del actionList[index]
        self.updateScheduler()

def svgToFieldCoordinates(x, y):
    return ( (float(x) - FIELD_WIDTH  / 2) / FIELD_PIXELS_PER_FOOT,
            (-float(y) + FIELD_HEIGHT / 2) / FIELD_PIXELS_PER_FOOT)

def fieldToSvgCoordinates(x, y):
    return (FIELD_WIDTH  / 2 + x * FIELD_PIXELS_PER_FOOT,
            FIELD_HEIGHT / 2 - y * FIELD_PIXELS_PER_FOOT)

# is used to represent the robot and cursor
class Arrow(gui.SvgPolyline):

    def __init__(self, color):
        super().__init__()
        halfWidth = drivetrain.ROBOT_WIDTH * FIELD_PIXELS_PER_FOOT / 2
        halfLength = drivetrain.ROBOT_LENGTH * FIELD_PIXELS_PER_FOOT / 2
        self.add_coord(0, -halfLength)
        self.add_coord(halfWidth, halfLength)
        self.add_coord(-halfWidth, halfLength)
        self.style['fill'] = color
        self.setPosition(0, 0, 0)

    def setPosition(self, x, y, angle=None):
        self.x = x
        self.y = y
        if angle is not None:
            self.angle = angle
        else:
            angle = self.angle

        svgX, svgY = fieldToSvgCoordinates(x, y)
        svgAngle = -math.degrees(angle)
        self.attributes['transform'] = "translate(%s,%s) rotate(%s)" \
            % (svgX, svgY, svgAngle)
import remi.gui as gui
from remi.server import start
import seamonsters as sea
import json, os, autoActions, drivetrain, coordinates, math, glob

fieldWidth = 520
fieldHeight = 260
fieldPixelsPerFoot = 10

GREEN = "rgb(21, 130, 21)"
RED = "rgb(130, 21, 21)"
GREY = "rgb(100, 100, 100)"

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

    def presetPath(self):
        return sea.getRobotPath('autoPresets')

    def main(self, robot, appCallback):
        self.robot = robot

        root = gui.HBox()
        root.style['align-items'] = 'stretch'

        leftSide = gui.VBox()
        leftSide.style['align-items'] = 'stretch'

        middle = gui.VBox()

        rightSide = gui.VBox()
        rightSide.style['align-items'] = 'stretch'

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

        leftSide.append(self.initStats(robot))
        leftSide.append(self.initLedControl(robot))
        leftSide.append(self.initScheduler(robot))
        leftSide.append(self.initBezier(robot))

        middle.append(self.initCamera(robot))
        middle.append(self.initFieldMap(robot))
        middle.append(self.initFieldSwitcher(robot))

        rightSide.append(self.initManual(robot))
        self.autoSpeedGroup.highlight("medium")
        rightSide.append(self.initPidControlsBox(robot))
        rightSide.append(self.initTest(robot))
        rightSide.append(self.initSubsystemsInfo(robot))

        root.append(leftSide)
        root.append(middle)
        root.append(rightSide)

        self.updateSchedulerFlag = False

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

        # updates the subsystem indicators

        color = GREY

        # intake color adjustment
        if self.robot.intake.running:
            color = RED if self.robot.intake.reversed else GREEN
        self.intakeIndicator.style["background"] = color

        color = GREY

        # indexer color adjustment
        if self.robot.indexer.running:
            color = RED if self.robot.indexer.reversed else GREEN
        self.indexerIndicator.style["background"] = color

        # auto indexer color adjustment
        color = GREEN if self.robot.indexer.autoIndexEnabled else RED
        self.autoIndexIndicator.style["background"] = color

        # shooter color adjustment
        color = GREEN if self.robot.shooter.running else GREY
        self.shooterIndicator.style["background"] = color

    def initManual(self, robot):
        manualBox = self.sectionBox()

        driveControlBox = gui.VBox(gui.Label("Drive controls"))
        gearButtons = []
        speedButtons = []
        compressorButtons = []
        autoSpeedButtons = []
        
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

        self.autoSpeedGroup = sea.ToggleButtonGroup()

        # auto speed controls
        self.autoSpeed = 0.5
        def slowSpeed(button):
            self.autoSpeed = 0.25
            self.autoSpeedGroup.highlight("slow")
        def mediumSpeed(button):
            self.autoSpeed = 0.5
            self.autoSpeedGroup.highlight("medium")
        def fastSpeed(button):
            self.autoSpeed = 1
            self.autoSpeedGroup.highlight("fast")

        slowBtn = gui.Button("slow")
        slowBtn.set_on_click_listener(slowSpeed)
        medBtn = gui.Button("medium")
        medBtn.set_on_click_listener(mediumSpeed)
        fastBtn = gui.Button("fast")
        fastBtn.set_on_click_listener(fastSpeed)

        for button in [slowBtn, medBtn, fastBtn]:
            autoSpeedButtons.append(button)
            self.autoSpeedGroup.addButton(button)

        gearBox = sea.hBoxWith(gui.Label("Gears:"), gearButtons)
        speedBox = sea.hBoxWith(gui.Label("Speed:"), speedButtons)
        compressorBox = sea.hBoxWith(gui.Label("Compressor:"), compressorButtons)
        autoSpeedBox = sea.hBoxWith(gui.Label("Auto Speed:"), autoSpeedButtons)

        driveControlBox.append(gearBox)
        driveControlBox.append(speedBox)
        driveControlBox.append(autoSpeedBox)
        driveControlBox.append(compressorBox)

        manualBox.append(driveControlBox)
        return manualBox

    def initCamera(self, robot):
        cameraBox = self.sectionBox()

        videoFeedBox = gui.HBox()
        limelightFeed = gui.Image('http://10.26.5.11:5800/')
        videoFeedBox.append(limelightFeed)

        videoFeed = gui.Image('http://10.26.5.6:5800/')
        videoFeedBox.append(videoFeed)

        cameraBox.append(videoFeedBox)
        return cameraBox

    def initPidControlsBox(self, robot):
        pidControlsBox = self.sectionBox()

        # This changes pid values on the robot depending on the button pressed.
        def changePidValue(button):
            term = button.get_text()[-1]
            parentHbox = button.get_parent()
            peerTextArea = parentHbox.children[term + "textarea"]

            try:
                newPidValue = float(peerTextArea.get_value())
            except:
                print(term + " value incorrect")
                return

            if (term == "P"):
                robot.driveGear.p = newPidValue
            elif (term == "I"):
                robot.driveGear.i = newPidValue
            elif (term == "D"):
                robot.driveGear.d = newPidValue

            robot.driveGear.applyGear(robot.superDrive)

        # P, I, and D each have their own label, text area, and update button
        for term in ["P", "I", "D"]:
            controlBox = gui.HBox()
            # Adds a label to the hBox with the key <term>label
            controlBox.append(gui.Label(term + ": "), term + "label")
            # Adds a text area to the hBox with the key <term>textarea
            controlBox.append(gui.Input(), term + "textarea")
            # Adds an update button to the hBox with the key <term>updatebutton
            button = gui.Button("Update " + term)
            button.set_on_click_listener(changePidValue)
            controlBox.append(button, term + "updatebutton")
            # Adds the control box for this term to the pidControlsBox with the key <term>
            pidControlsBox.append(controlBox, term)

        return pidControlsBox


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

        setRotationBtn = gui.Button("Point Robot at Cursor")
        setRotationBtn.set_on_click_listener(self.c_pointAtCursor)
        robotBox.append(setRotationBtn)

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

        self.fieldSvg = gui.Svg()
        self.makeField('/res:field.png', True)
        fieldBox.append(self.fieldSvg)

        self.robotPathLines = []

        self.selectedCoord = coordinates.FieldCoordinate("Center", 0, 0, math.radians(-90))
        self.updateCursorPosition()

        return fieldBox

    def makeField(self, imageURL, drawPoints):
        self.fieldSvg.set_viewbox(0, 0, fieldWidth, fieldHeight)
        self.fieldSvg.set_size(fieldWidth, fieldHeight)
        self.fieldSvg.set_on_mousedown_listener(self.mouse_down_listener)

        self.image = gui.SvgImage(imageURL, 0, 0, fieldWidth, fieldHeight)
        self.fieldSvg.append(self.image)

        if drawPoints:
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

    def initFieldSwitcher(self, robot):

        fieldSwitcherBox = self.sectionBox()
        buttonsBox = gui.HBox()
        fieldSwitcherBox.append(gui.Label("Field Switcher"))
        fieldSwitcherBox.append(buttonsBox)

        def changeFieldImage(button, imageURL, isNormalField):
            
            if isNormalField:
                fieldWidth = 520
                fieldHeight = 260
                fieldPixelsPerFoot = 10
            else:
                fieldWidth = 1980
                fieldHeight = 990
                fieldPixelsPerFoot = 66

            self.fieldSvg.empty()
            self.makeField(imageURL, isNormalField)
            self.updateSchedulerFlag = True

        fieldButton = gui.Button('Field')
        fieldButton.set_on_click_listener(changeFieldImage, '/res:field.png', True)
        autoNav1Button = gui.Button('Auto Nav 1')
        autoNav1Button.set_on_click_listener(changeFieldImage, '/res:AutoNav1.png', False)
        autoNav2Button = gui.Button('Auto Nav 2')
        autoNav2Button.set_on_click_listener(changeFieldImage, '/res:AutoNav2.png', False)
        autoNav3Button = gui.Button('Auto Nav 3')
        autoNav3Button.set_on_click_listener(changeFieldImage, '/res:AutoNav3.png', False)

        for button in [fieldButton, autoNav1Button, autoNav2Button, autoNav3Button]:
            buttonsBox.append(button)

        return fieldSwitcherBox

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

        addActionBox.append(gui.Label("Auto actions:"))

        self.genericActionList = gui.ListView()
        self.genericActionList.append("Drive to Point", "drive")
        self.genericActionList.append("Rotate in Place", "rotate")
        self.genericActionList.append("Rotate towards Point", "face")
        self.genericActionList.append("Shoot", "shoot")
        self.genericActionList.append("Toggle Intake", "intake")
        self.genericActionList.append("Set Starting Positon", "set")
        self.genericActionList.append("Set Robot Starting Angle", "angle")
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

        schedulePresetLbl = gui.Label("Auto Sequence Presets")
        schedulerBox.append(schedulePresetLbl)
        presetIn = gui.Input(default_value="file name")
        schedulerBox.append(presetIn)
        schedulePresets = gui.HBox()
        schedulerBox.append(schedulePresets)
        self.presetDropdown = gui.DropDown()
        self.updatePresetFileDropdown()
        schedulerBox.append(self.presetDropdown)
        openPresetBtn = gui.Button("Open")
        schedulePresets.append(openPresetBtn)
        openPresetBtn.set_on_click_listener(self.c_openAutoPreset, self.presetDropdown)
        newPresetBtn = gui.Button("New")
        schedulePresets.append(newPresetBtn)
        newPresetBtn.set_on_click_listener(self.c_saveAutoPresetFromText, presetIn)
        schedulePresets.append(newPresetBtn)
        savePresetBtn = gui.Button("Save")
        schedulePresets.append(savePresetBtn)
        savePresetBtn.set_on_click_listener(self.c_saveAutoPresetFromDropdown, self.presetDropdown)
        schedulePresets.append(savePresetBtn)
        deletePresetBtn = gui.Button("Delete")
        schedulePresets.append(deletePresetBtn)
        deletePresetBtn.set_on_click_listener(self.c_deleteAutoPreset, self.presetDropdown)
        schedulePresets.append(deletePresetBtn)
        
        return schedulerBox

    def initBezier(self, robot):
        bezierBox = self.sectionBox()
        bezierBox.append(gui.Label("Bezier Path Following"))

        bezierButtons = gui.HBox()
        bezierBox.append(bezierButtons)

        self.bezierPathLines = []

        def addPoint(button):
            self.bezierPathLines.append(self.selectedCoord)
            self.updateSchedulerFlag = True

        addBtn = gui.Button("Add Point")
        bezierButtons.append(addBtn)
        addBtn.set_on_click_listener(addPoint)

        def endPath(button):
            self.bezierPathLines.append(self.selectedCoord)
            self.c_addGenericAction(None, "bezier", self.bezierPathLines)
            self.bezierPathLines = []

        endBtn = gui.Button("End Path")
        bezierButtons.append(endBtn)
        endBtn.set_on_click_listener(endPath)

        def resetPath(button):
            self.bezierPathLines = []
            self.updateSchedulerFlag = True

        resetBtn = gui.Button("Reset Path")
        bezierButtons.append(resetBtn)
        resetBtn.set_on_click_listener(resetPath)

        return bezierBox

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

    def initSubsystemsInfo(self, robot):
        subsystemBox = self.sectionBox()

        subsystemInfoBox = sea.hBoxWith(gui.Label("Subsystems:"))
        self.intakeIndicator = gui.Button("Intake")
        self.indexerIndicator = gui.Button("Indexer")
        self.autoIndexIndicator = gui.Button("Auto Indexer")
        self.shooterIndicator = gui.Button("Shooter")

        for indicator in [self.intakeIndicator, self.indexerIndicator, self.autoIndexIndicator, self.shooterIndicator]:
            subsystemInfoBox.append(indicator)

        subsystemBox.append(subsystemInfoBox)
        return subsystemBox

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
        # the higher the line number, the older it is
        lineX, lineY = fieldToSvgCoordinates(self.robotArrow.x, self.robotArrow.y)
        lineX2, lineY2 = lineX, lineY
        lineX3, lineY3 = lineX2, lineY2

        index = 0
        for action in scheduler.actionList:
            name = action.name
            if action == scheduler.runningAction:
                name = "* " + name
            listItem = gui.ListItem(name)
            self.schedulerList.append(listItem, str(index))

            if action.coord is not None:

                if action.key == "drive":
                    lineX3, lineY3 = lineX2, lineY2
                    lineX2, lineY2 = lineX, lineY
                    lineX, lineY = self.actionLines(lineX, lineY, action.coord)

                elif action.key == "bezier":
                    for coord in action.coord:
                        lineX3, lineY3 = lineX2, lineY2
                        lineX2, lineY2 = lineX, lineY
                        lineX, lineY = self.actionLines(lineX, lineY, coord)
                        self.bezierCurve(lineX, lineX2, lineX3, lineY, lineY2, lineY3)
                    # finishes the last point on the curve
                    self.bezierCurve(lineX, lineX, lineX2, lineY, lineY, lineY2)
            index += 1

        for coord in self.bezierPathLines:
            lineX, lineY = self.actionLines(lineX, lineY, coord)

    def actionLines(self, lineX, lineY, coord):
        x1, y1 = fieldToSvgCoordinates(coord.x, coord.y)
        line = gui.SvgLine(lineX, lineY, x1, y1)
        line.set_stroke(width=3)
        self.robotPathLines.append(line)
        self.fieldSvg.append(line)
        lineX, lineY = x1, y1
        return lineX, lineY

    # stuff for displaying a bezier curve of the action lines

    def bezierCurve(self, lineX1, lineX2, lineX3, lineY1, lineY2, lineY3):
        curve = self._curve(5, (lineX1, lineY1), (lineX2, lineY2), (lineX3, lineY3))
        x1, y1 = curve[0]
        for index in range(1, len(curve)):
            x2, y2 = curve[index]
            line = gui.SvgLine(x1, y1, x2, y2)
            line.set_stroke(width=3, color='red')
            self.robotPathLines.append(line)
            self.fieldSvg.append(line)
            x1, y1 = x2, y2

    def _bezier(self, incriment, point1, point2, point3):
        x = (1 - incriment) * ((1 - incriment) * point1[0] + incriment * point2[0]) + incriment * ((1 - incriment) * point2[0] + incriment * point3[0])
        y = (1 - incriment) * ((1 - incriment) * point1[1] + incriment * point2[1]) + incriment * ((1 - incriment) * point2[1] + incriment * point3[1])
        return (x, y)

    def _midpoint(self, point1, point2):
        return ((point1[0] + point2[0]) / 2,  (point1[1] + point2[1]) / 2)

    def _curve(self, incriments, point0, point1, point2):
        midpoint1 = self._midpoint(point0, point1)
        midpoint3 = self._midpoint(point1, point2)
        out = []
        for inc in range(incriments):
            out.append(self._bezier(inc / incriments, midpoint1, point1, midpoint3))
        out.append(self._bezier(1, midpoint1, point1, midpoint3))
        return out

    def updatePresetFileDropdown(self):
        self.presetDropdown.empty()
        for file in glob.glob(os.path.join(self.presetPath(), "*.json")):
            fileName = os.path.basename(file)
            self.presetDropdown.append(fileName, file)
    
    def saveAutoPreset(self, fileLocation):
        autoPreset = self.robot.autoScheduler.saveSchedule()
        with open(fileLocation,"w") as presetFile:
            json.dump(autoPreset, presetFile)
        print("Preset saved at " + fileLocation)
        self.updatePresetFileDropdown()

    # Callbacks

    def c_setRobotPosition(self, button):
        coord = self.selectedCoord
        self.robot.pathFollower.setPosition(
            coord.x, coord.y, coord.angle)
        
    def c_pointAtCursor(self, button):
        coord = self.selectedCoord

        xdif = coord.x - self.robot.pathFollower.robotX
        ydif = coord.y - self.robot.pathFollower.robotY

        angle = -math.atan2(xdif, ydif)

        self.robot.pathFollower.setPosition(
            self.robot.pathFollower.robotX, 
            self.robot.pathFollower.robotY, 
            angle
        )

    def mouse_down_listener(self,widget,x,y):
        x, y = svgToFieldCoordinates(x, y)
        self.selectedCoord = coordinates.FieldCoordinate("Selected",
            x, y, self.selectedCoord.angle)
        for point in self.targetPoints:
            if math.hypot(x - point.x, y - point.y) < 1:
                self.selectedCoord = point
        self.updateCursorPosition()
    
    def c_addGenericAction(self, listview, key, coord=None):
        if coord is None:
            coord = self.selectedCoord
        if key == "drive":
            action = autoActions.createDriveToPointAction(
                self.robot.pathFollower, coord, self.autoSpeed)
        elif key == "bezier":
            action = autoActions.createBezierAction(
                self.robot.pathFollower, coord, self.autoSpeed)
        elif key == "rotate":
            action = autoActions.createRotateInPlaceAction(
                self.robot.pathFollower, coord)
        elif key == "face":
            action = autoActions.createRotateTowardsPointAction(
                self.robot, coord)
        elif key == "shoot":
            action = autoActions.createShootAction(self.robot)
        elif key == "set":
            action = autoActions.createSetRobotPositionAction(
                self.robot.pathFollower, coord)
        elif key == "angle":
            action = autoActions.createSetRobotAngleToCursorAction(
                self.robot.pathFollower, coord)
        elif key == "intake":
            action = autoActions.createToggleIntakeAction(self.robot)
        else:
            action = self.robot.genericAutoActions[int(key)]
        self.robot.autoScheduler.actionList.append(action)
        self.updateSchedulerFlag = True

    def c_clearSchedule(self, button):
        self.bezierPathLines = []
        self.robot.autoScheduler.actionList.clear()
        self.updateSchedulerFlag = True

    def c_removeAction(self, listview, key):
        index = int(key)
        actionList = self.robot.autoScheduler.actionList
        if index < len(actionList):
            del actionList[index]
        self.updateSchedulerFlag = True

    # Auto Presets:

    def c_openAutoPreset(self, dropDownItem, file):
        if file.get_key() is None:
            print("No file selected")
            return
        # file should be blank because it will delete everything in it when it is opened
        self.robot.autoScheduler.actionList.clear()
        with open(file.get_key(),"r") as presetFile:
            try:
                preset = json.load(presetFile)
            except:
                print("File is empty")
                return
            for action in preset:
                coord = None
                if action["coord"] != []:
                    if action["key"] != "bezier":
                        # creates a field coordinate
                        coord = coordinates.FieldCoordinate(action["coord"][0], 
                            action["coord"][1], action["coord"][2], action["coord"][3])
                    else:
                        # loops through and makes a list of coordinates
                        coord = []
                        for point in action["coord"]:
                            coord.append(coordinates.FieldCoordinate(point[0], 
                                point[1], point[2], point[3]))

                self.c_addGenericAction(self.genericActionList, action["key"], coord)
        
        self.updateSchedulerFlag = True
        self.updatePresetFileDropdown()

    def c_saveAutoPresetFromText(self, button, textInput):
        # file needs to be blank 
        self.saveAutoPreset(os.path.join(self.presetPath(), textInput.get_value() + ".json"))

    def c_saveAutoPresetFromDropdown(self, dropDownItem, file):
        #file needs to be blank
        if file.get_key() is None:
            print("No file selected")
            return
        self.saveAutoPreset(file.get_key())

    def c_deleteAutoPreset(self, dropDownItem, file):
        if file.get_key() is None:
            print("No file selected")
            return
        os.unlink(file.get_key())
        self.updatePresetFileDropdown()

def svgToFieldCoordinates(x, y):
    return ((float(x) - fieldWidth  / 2) / fieldPixelsPerFoot,
            (-float(y) + fieldHeight / 2) / fieldPixelsPerFoot)

def fieldToSvgCoordinates(x, y):
    return (fieldWidth  / 2 + x * fieldPixelsPerFoot,
            fieldHeight / 2 - y * fieldPixelsPerFoot)

# is used to represent the robot and cursor
class Arrow(gui.SvgPolyline):

    def __init__(self, color):
        super().__init__()
        halfWidth = drivetrain.ROBOT_WIDTH * fieldPixelsPerFoot / 2
        halfLength = drivetrain.ROBOT_LENGTH * fieldPixelsPerFoot / 2
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
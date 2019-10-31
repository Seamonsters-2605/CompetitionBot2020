import remi.gui as gui
import math
import seamonsters as sea

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

        rightSide = gui.VBox()
        rightSide.style['align-items'] = 'flex-start'

        self.motorDataDict = { \
            "ampRow" : None,
            "tempRow" : None,
            "amp" : [],
            "temp" : []
            }

        leftSide.append(self.initStats(robot))

        rightSide.append(self.initManual(robot))
        rightSide.append(self.initTest(robot))

        root.append(leftSide)
        root.append(rightSide)

        appCallback(self)
        return root

    # runs every time the dashboard is updated
    def idle(self):
        for motorNum in range(6):
            self.motorDataTable.children[self.motorDataDict["ampRow"]].children[self.motorDataDict["amp"][motorNum]].set_text(str(self.robot.motorData[motorNum]["amps"]))
            self.motorDataTable.children[self.motorDataDict["tempRow"]].children[self.motorDataDict["temp"][motorNum]].set_text(str(self.robot.motorData[motorNum]["temp"]))

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

    def initStats(self, robot):
        statsBox = self.sectionBox()

        motorDataBox = sea.vBoxWith(gui.Label("Motor Data"))
        self.motorDataTable = gui.Table()
        motorNumRow = gui.TableRow(gui.TableItem("Motor Number:"))
        self.motorAmpRow = gui.TableRow(gui.TableItem("Amp Draw:"))
        self.motorTempRow = gui.TableRow(gui.TableItem("Temp:"))

        self.motorDataTable.append(motorNumRow)
        self.motorDataDict["ampRow"] = self.motorDataTable.append(self.motorAmpRow)
        self.motorDataDict["tempRow"] = self.motorDataTable.append(self.motorTempRow)

        for motorNum in range(6):
            motorNumRow.append(gui.TableItem(str(motorNum + 1)))
            self.motorDataDict["amp"].append(self.motorAmpRow.append(gui.TableItem("")))
            self.motorDataDict["temp"].append(self.motorTempRow.append(gui.TableItem("")))
        
        motorDataBox.append(self.motorDataTable)

        statsBox.append(motorDataBox)
        return statsBox
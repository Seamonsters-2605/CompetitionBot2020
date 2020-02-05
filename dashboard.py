import remi.gui as gui
import math
import seamonsters as sea

class RevDashboard(sea.Dashboard):

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

        root = gui.VBox(width = 300, margin = "0px auto")
        root.style['align-items'] = 'stretch'

        root.append(self.initTest(robot, 1))
        root.append(self.initTest(robot, 2))

        appCallback(self)
        return root

    def initTest(self, robot, testNum):
        testBox = self.sectionBox()

        motorNumberIn = gui.Input()
        motorSelectionBox = sea.hBoxWith(gui.Label("Motor Number:"), motorNumberIn)

        motorSpeedInput = gui.Input()
        testButton = gui.Button("Test")
        motorSpeedBox = sea.hBoxWith(testButton, gui.Label("Speed:"), motorSpeedInput)

        def testMotor(button):
            try:
                motorNum = int(motorNumberIn.get_value())
            except:
                print("Motor number incorrect")
                return

            if not 1 <= motorNum <= 9:
                print("Motor number incorrect")
                return
        
            testSpeed = float(motorSpeedInput.get_value())

            if testSpeed < -1:
                testSpeed = -1
            elif testSpeed > 1:
                testSpeed = 1

            robot.testSettings[testNum - 1]["motorNum"] = motorNum
            robot.testSettings[testNum - 1]["speed"] = testSpeed

        testButton.set_on_click_listener(testMotor)

        testBox.append(gui.Label("Motor Test " + str(testNum)))
        testBox.append(motorSelectionBox)
        testBox.append(motorSpeedBox)
        return testBox
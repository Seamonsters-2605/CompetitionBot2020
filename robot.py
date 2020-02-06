import wpilib
import rev
import seamonsters as sea 
import math
import dashboard

class RevClientBot(sea.GeneratorBot):

    def robotInit(self):

        self.pdp = wpilib.PowerDistributionPanel(50)

        self.motor0 = None
        self.motor1 = None

        # controls the state of the robot
        self.controlModeMachine = sea.StateMachine()
        self.testState = sea.State(self.testing)

        # testing
        self.testSettings = [{ \
            "motorNum" : 1,
            "speed" : 0,
            "makeNewMotor" : False
            }, { \
            "motorNum" : 2,
            "speed" : 0,
            "makeNewMotor" : False
            }]

        self.app = None 
        sea.startDashboard(self, dashboard.RevDashboard)

    # Different Driving Modes

    # robot is controlled by the driver
    def teleop(self):
        pass
        yield from self.mainGenerator()

    # robot is controlled by the code
    def autonomous(self):
        pass
        yield from self.mainGenerator()

    # robot is being tested off the field
    def test(self):
        self.controlModeMachine.replace(self.testState)
        yield from self.mainGenerator()

    # runs every 50th of a second
    def mainGenerator(self):
        yield from sea.parallel(
            self.controlModeMachine.updateGenerator(), 
            self.updateDashboardGenerator())

    # switches to use the dashboard for testing purposes
    def testing(self):
        while True:

            if self.testSettings[0]["makeNewMotor"]:
                self.motor0 = rev.CANSparkMax(self.testSettings[0]["motorNum"], rev.MotorType.kBrushless)
                if self.motor0.getFirmwareVersion() == 0:
                    self.motor0 = None
                    print("Motor with ID: %s not found" % self.testSettings[0]["motorNum"])
                self.testSettings[0]["makeNewMotor"] = False

            if self.testSettings[1]["makeNewMotor"]:
                self.motor1 = rev.CANSparkMax(self.testSettings[1]["motorNum"], rev.MotorType.kBrushless)
                if self.motor1.getFirmwareVersion() == 0:
                    self.motor1 = None
                    print("Motor with ID: %s not found" % self.testSettings[1]["motorNum"])
                self.testSettings[1]["makeNewMotor"] = False
            
            if self.motor0 != None and self.motor1 != None:
                if self.motor0.getDeviceId() == self.motor1.getDeviceId():
                    self.motor1 = None
                    print("Cannot test the same motor")
                
            if self.motor0 != None:
                self.motor0.set(self.testSettings[0]["speed"])

            if self.motor1 != None:
                self.motor1.set(self.testSettings[1]["speed"])

            yield

    # updates the dashboard
    def updateDashboardGenerator(self):
        if self.app is not None:
            self.app.clearEvents()
        while True:
            v = None
            if self.app is not None:
                v = self.app.doEvents()
            yield v

if __name__ == "__main__":
    wpilib.run(RevClientBot)
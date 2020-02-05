import wpilib
import rev
import seamonsters as sea 
import math
import dashboard

class RevClientBot(sea.GeneratorBot):

    def robotInit(self):

        self.pdp = wpilib.PowerDistributionPanel(50)

        motor1 = rev.CANSparkMax(1, rev.CANSparkMax.MotorType.kBrushless)
        motor2 = rev.CANSparkMax(2, rev.CANSparkMax.MotorType.kBrushless)
        motor3 = rev.CANSparkMax(3, rev.CANSparkMax.MotorType.kBrushless)
        motor4 = rev.CANSparkMax(4, rev.CANSparkMax.MotorType.kBrushless)
        motor5 = rev.CANSparkMax(5, rev.CANSparkMax.MotorType.kBrushless)
        motor6 = rev.CANSparkMax(6, rev.CANSparkMax.MotorType.kBrushless)
        motor7 = rev.CANSparkMax(7, rev.CANSparkMax.MotorType.kBrushless)
        motor8 = rev.CANSparkMax(8, rev.CANSparkMax.MotorType.kBrushless)
        motor9 = rev.CANSparkMax(9, rev.CANSparkMax.MotorType.kBrushless)

        self.motors = [motor1, motor2, motor3, motor4, motor5, motor6, motor7, motor8, motor9]

        # controls the state of the robot
        self.controlModeMachine = sea.StateMachine()
        self.testState = sea.State(self.testing)

        # testing
        self.testSettings = [{ \
            "motorNum" : 1,
            "speed" : 0
            }, { \
            "motorNum" : 2,
            "speed" : 0
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
            self.updateDashboardGenerator(),
            self.updateMotorData())

    # switches to use the dashboard for testing purposes
    def testing(self):
        while True:

            self.motors[self.testSettings[0]["motorNum"]].set(self.testSettings[0]["speed"])
            self.motors[self.testSettings[1]["motorNum"]].set(self.testSettings[1]["speed"])

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

    # updates the motor data for the dashboard
    def updateMotorData(self):
        while True:

            for motor in range(len(self.superDrive.motors)):
                amps = round(self.superDrive.motors[motor].getOutputCurrent(), 2)
                temp = round(self.superDrive.motors[motor].getMotorTemperature(), 2)

                self.motorData[motor]["amps"] = amps
                self.motorData[motor]["temp"] = temp

                if amps > self.motorData[motor]["maxAmp"]:
                    self.motorData[motor]["maxAmp"] = amps

                if temp > self.motorData[motor]["maxTemp"]:
                    self.motorData[motor]["maxTemp"] = temp

            yield

if __name__ == "__main__":
    wpilib.run(RevClientBot)
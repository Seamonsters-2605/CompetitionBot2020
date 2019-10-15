import wpilib
import drivetrain
import seamonsters as sea 
import math
import navx

class CompetitionBot2020(sea.GeneratorBot):

    def robotInit(self):

        # devices
        self.controller = wpilib.Joystick(0)
        self.buttonBoard = wpilib.Joystick(1)

        ahrs = navx.AHRS.create_spi()

        self.pdp = wpilib.PowerDistributionPanel(50)

        self.superDrive = drivetrain.initDrivetrain()
        self.pathFollower = sea.PathFollower(self.superDrive, ahrs)

        self.controlModeMachine = sea.StateMachine()
        self.manualState = sea.State(self.driving)

        # for shifting gear box
        self.compressor = wpilib.Compressor(0)
        self.piston = wpilib.Solenoid(0)

        # drive gears
        self.superDrive.gear = None
        self.driveGear = drivetrain.slowVoltageGear
        self.driveMode = "voltage"
        self.driveSpeed = "slow"
        self.driveGears = \
            {"voltage" : \
                {"slow" : drivetrain.slowVoltageGear, 
                "medium" : drivetrain.mediumVoltageGear, 
                "fast" : drivetrain.fastVoltageGear}, 
            "velocity" : \
                {"slow" : drivetrain.slowVelocityGear, 
                "medium" : drivetrain.mediumVelocityGear, 
                "fast" : drivetrain.fastVelocityGear},      
            "position" : \
                {"slow" : drivetrain.slowPositionGear, 
                "medium" : drivetrain.mediumPositionGear, 
                "fast" : drivetrain.fastPositionGear} 
            }

    def teleop(self):
        self.manualMode()

        yield from sea.parallel(
            self.controlModeMachine.updateGenerator(), 
            self.buttonControl())

    def manualMode(self):
        self.controlModeMachine.replace(self.manualState)

    def driving(self):
        while True:

            self.pathFollower.updateRobotPosition()
            
            if self.superDrive.gear != self.driveGear:
                self.driveGear.applyGear(self.superDrive)

            # must be changed when I get more details
            if self.piston.get() and self.driveSpeed != "slow":
                self.piston.set(False)
            elif not self.piston.get() and self.driveSpeed == "slow":
                self.piston.set(True)

            lMag = -sea.deadZone(self.controller.getY()) 
            lMag *= self.driveGear.moveScale # maximum feet per second
            rMag = -sea.deadZone(self.controller.getThrottle())
            rMag *= self.driveGear.moveScale

            self.superDrive.drive(rMag, math.pi/2, 0, 1)
            self.superDrive.drive(lMag, math.pi/2, 0, 0)

            yield

    def buttonControl(self):
        # clears events on buttons
        for button in range(1, 11):
            self.buttonBoard.getRawButtonPressed(button)

        while True:

            if self.buttonBoard.getRawButtonPressed(3):
                self.driveSpeed = "slow"
            elif self.buttonBoard.getRawButtonPressed(4):
                self.driveSpeed = "medium"
            elif self.buttonBoard.getRawButtonPressed(5):
                self.driveSpeed = "fast"

            if self.buttonBoard.getRawButtonPressed(2):
                self.toggleDriveMode()

            self.driveGear = self.driveGears[self.driveMode][self.driveSpeed]

            yield

    def toggleDriveMode(self):
        if self.driveMode == "voltage":
            self.driveMode = "velocity"
        elif self.driveMode == "velocity":
            self.driveMode = "position"
        else:
            self.driveMode = "voltage"

if __name__ == "__main__":
    wpilib.run(CompetitionBot2020)
import wpilib
import drivetrain
import seamonsters as sea 
import math

class CompetitionBot2020(sea.GeneratorBot):

    def robotInit(self):
        self.joystick = wpilib.Joystick(0)
        self.buttonBoard = wpilib.Joystick(1)

        self.superDrive = drivetrain.initDrivetrain()
        self.superDrive.gear = None
        self.driveGear = drivetrain.slowPositionGear

    def teleop(self):
        yield from sea.parallel(self.drive(), self.buttonControl())

    def drive(self):
        while True:

            if self.superDrive.gear != self.driveGear:
                self.driveGear.applyGear(self.superDrive)

            mag = sea.deadZone(self.joystick.getY()) 
            mag *= self.driveGear.moveScale # maximum feet per second
            turn = sea.deadZone(self.joystick.getX())
            turn *= self.driveGear.turnScale # maximum radians per second

            self.superDrive.drive(mag, math.pi/2, turn)

            yield

    def buttonControl(self):
        # clears events on buttons
        for button in range(1, 11):
            self.buttonBoard.getRawButtonPressed(button)

        while True:

            if self.buttonBoard.getRawButtonPressed(3):
                self.driveGear = drivetrain.slowPositionGear
            elif self.buttonBoard.getRawButtonPressed(4):
                self.driveGear = drivetrain.mediumPositionGear
            elif self.buttonBoard.getRawButtonPressed(5):
                self.driveGear = drivetrain.fastPositionGear

            yield

if __name__ == "__main__":
    wpilib.run(CompetitionBot2020)
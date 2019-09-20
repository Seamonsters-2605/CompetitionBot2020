import wpilib
import drivetrain
import seamonsters as sea 
import math

class CompetitionBot2020(sea.GeneratorBot):

    def robotInit(self):
        self.joystick = wpilib.Joystick(0)
    
        self.superDrive = drivetrain.initDrivetrain()

    def teleop(self):
        while True:
            
            mag = sea.deadZone(self.joystick.getY())
            mag *= 5 # maximum feet per second
            turn = sea.deadZone(self.joystick.getX())
            turn *= math.radians(300) # maximum radians per second

            self.superDrive.drive(mag, math.pi/2, turn)

if __name__ == "__main__":
    wpilib.run(CompetitionBot2020)
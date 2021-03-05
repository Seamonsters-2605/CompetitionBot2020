import rev
import seamonsters as sea

# speeds for the motors need to be adjusted

class Climber:
    """
    This class represents the subsystem on the robot that is used to grab on to the 
    "generator switch" bar and hold itself above the ground.
    """
    def __init__(self, armMotorNum: int, winchMotorhNum: int):
        """
        Constructor.
        :param armMotorNum: the number of the motor that hooks the robot to the bar.
        :param winchMotorNum: the number of the motor that uses a winch to pull the robot up/down.
        """
        self.armMotor = sea.createSpark(armMotorNum, rev.CANSparkMax.MotorType.kBrushless)
        self.winchMotor = sea.createSpark(winchMotorhNum, rev.CANSparkMax.MotorType.kBrushless)

    # Arm Functions:

    def extend(self):
        self.armMotor.set(1)

    def retract(self):
        self.armMotor.set(-1)

    # Winch Functions:

    def climbUp(self):
        self.winchMotor.set(1)

    def climbDown(self):
        self.winchMotor.set(-1)
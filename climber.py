import rev
import seamonsters as sea

# speeds for the motors need to be adjusted

class Climber:
    """
    This class represents the arm and winch the robot uses to hook itself on to the bar
    and pull itself up.
    (It is a subsystem of the robot.)
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
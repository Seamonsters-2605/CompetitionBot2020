import rev
from physics import getSpark

# speeds for the motors need to be adjusted

class Climber:

    def __init__(self, armMotorNum, winchMotorhNum):
        self.armMotor = getSpark(armMotorNum, rev.CANSparkMax.MotorType.kBrushless)
        self.winchMotor = getSpark(winchMotorhNum, rev.CANSparkMax.MotorType.kBrushless)

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
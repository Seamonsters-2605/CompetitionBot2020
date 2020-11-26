import rev
from physics import getSpark

class Shooter:

    def __init__(self, motorNum1, motorNum2):

        p = 0.00007
        i = 0.0000007
        d = 0
        f = 0
        
        self.motor1 = getSpark(motorNum1, rev.CANSparkMax.MotorType.kBrushless)
        self.motor2 = getSpark(motorNum2, rev.CANSparkMax.MotorType.kBrushless)

        self.motorController1 = self.motor1.getPIDController()
        self.motorController2 = self.motor2.getPIDController()

        for motorController in [self.motorController1, self.motorController2]:
                motorController.setP(p)
                motorController.setI(i)
                motorController.setD(d)
                motorController.setFF(f)

        self.running = False
        self.speed = 5_500 # 5_000 for right in front of the port mode

    # is a genrator to actually drive the motors, should be called 50 times a second
    def spin(self):

        while True:
        
            if self.running:
                self.motorController1.setReference(-self.speed, rev.ControlType.kVelocity)
                self.motorController2.setReference(self.speed, rev.ControlType.kVelocity)
            else:
                self.motor1.set(0)
                self.motor2.set(0)

            yield

    # stops the motors
    def stop(self):
        self.running = False

    def start(self):
        self.running = True

    def toggleMotors(self):
        self.running = not self.running

    # allows the speed the motor spins to be adjusted
    def adjustSpeed(self, change):
        self.speed += change

        if self.speed < 0:
            self.speed = 0
        elif self.speed > 5_676: # max speed of neo motor
            self.speed = 5_676
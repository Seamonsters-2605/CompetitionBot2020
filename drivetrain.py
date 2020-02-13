import seamonsters as sea 
from gear import DriveGear
import math, rev

ROBOT_LENGTH = 3
ROBOT_WIDTH = 3

def initDrivetrain():
    superDrive = sea.SuperHolonomicDrive()

    superDrive.motors = [] # not a normal property of SuperHolonomicDrive

    # 3 motors per wheel but wheels cannot have the same position so 
    # add a small amount to it to make it work
    _makeWheel(superDrive, 7, 8, 9, rev.MotorType.kBrushless, 1, 0)
    _makeWheel(superDrive, 10, 11, 12, rev.MotorType.kBrushless, -1, 0, reverse=True)
    sea.setSimulatedDrivetrain(superDrive)
    return superDrive

def _makeWheel(superDrive, sparkMaxNum1, sparkMaxNum2, sparkMaxNum3, motorType, xPos, yPos, reverse=False):
    sparkMax1 = rev.CANSparkMax(sparkMaxNum1, motorType)
    sparkMax2 = rev.CANSparkMax(sparkMaxNum2, motorType)
    sparkMax3 = rev.CANSparkMax(sparkMaxNum3, motorType)
    for sparkMax in [sparkMax1, sparkMax2, sparkMax3]:
        sparkMax.restoreFactoryDefaults()
        sparkMax.setIdleMode(rev.CANSparkMax.IdleMode.kBrake)
        superDrive.motors.append(sparkMax)

    # maxVoltageVelocity = 5 ft per second * 60 seconds = 300 rpm
    # probably wrong though because 16 works

    wheelDiameter = 6 / 12 # 6 inches converted to feet
    wheelCircumference = wheelDiameter * math.pi

    angledWheel = sea.AngledWheel(sparkMax1, xPos, yPos, math.radians(90), wheelCircumference, 16, reverse=reverse)
    angledWheel.addMotor(sparkMax2)
    angledWheel.addMotor(sparkMax3)

    superDrive.addWheel(angledWheel)

# drive gears 
# TODO: update the pids based on speed and adjust move/turn scales
# slow gear is set to max because the shifting gearbox slows it down

slowVoltageGear = DriveGear("Slow Voltage", rev.ControlType.kVoltage, gearRatio=1/18.03, 
moveScale=0.55, turnScale=0.8)
mediumVoltageGear = DriveGear("Medium Voltage", rev.ControlType.kVoltage, gearRatio=1/6.49,
moveScale=0.35, turnScale=0.5)
fastVoltageGear = DriveGear("Fast Voltage", rev.ControlType.kVoltage, gearRatio=1/6.49, 
moveScale=0.55, turnScale=0.8) 

slowVelocityGear = DriveGear("Slow Velocity", rev.ControlType.kVelocity,
    gearRatio=1/21.547202, moveScale=4, turnScale=1.5, p=0.0000688, i=0.0000007, d=0.00001, f=0.0)
mediumVelocityGear = DriveGear("Medium Velocity", rev.ControlType.kVelocity,
    gearRatio=1/5.7459207, moveScale=6, turnScale=4, p=0.00007, i=0.0000007, d=0.00001, f=0.0)
fastVelocityGear = DriveGear("Fast Velocity", rev.ControlType.kVelocity,
    gearRatio=1/5.7459207, moveScale=10, turnScale=5.5, p=0.00007, i=0.0000007, d=0.0001, f=0.0)

slowPositionGear = DriveGear("Slow Position", rev.ControlType.kPosition,
    gearRatio=1/21.547202, moveScale=4, turnScale=3, p=0.5, i=0.0, d=3.0, f=0.0)
mediumPositionGear = DriveGear("Medium Position", rev.ControlType.kPosition,
    gearRatio=1/5.7459207, moveScale=2, turnScale=1.5, p=0.5, i=0.0, d=3.0, f=0.0)
fastPositionGear = DriveGear("Fast Position", rev.ControlType.kPosition,
    gearRatio=1/5.7459207, moveScale=6, turnScale=5, p=0.5, i=0.0, d=3.0, f=0.0)

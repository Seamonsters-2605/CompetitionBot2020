import seamonsters as sea 
from gear import DriveGear
from motorNums import DRIVETRAIN_LEFT, DRIVETRAIN_RIGHT
import math, rev, sys

"""
This file contains information and functions for controlling the robot's drivetrain.
These functions being: adding wheels and initializing the drivetrain.
It also has configuration of the different drive gears (fast/slow, in voltage/position mode)
"""

ROBOT_LENGTH = 3
ROBOT_WIDTH = 3

def initDrivetrain():
    superDrive = sea.SuperHolonomicDrive()

    superDrive.motors = [] # not a normal property of SuperHolonomicDrive

    _makeWheel(superDrive, DRIVETRAIN_LEFT[0], DRIVETRAIN_LEFT[1], DRIVETRAIN_LEFT[2],
        rev.MotorType.kBrushless, 1, 0)
        
    _makeWheel(superDrive, DRIVETRAIN_RIGHT[0], DRIVETRAIN_RIGHT[1], DRIVETRAIN_RIGHT[2],
        rev.MotorType.kBrushless, -1, 0, reverse=True)

    sea.setSimulatedDrivetrain(superDrive)
    return superDrive

def _makeWheel(superDrive, sparkMaxNum1, sparkMaxNum2, sparkMaxNum3, motorType, xPos, yPos, reverse=False):


    sparkMax1 = sea.createSpark(sparkMaxNum1, motorType)
    sparkMax2 = sea.createSpark(sparkMaxNum2, motorType)
    sparkMax3 = sea.createSpark(sparkMaxNum3, motorType)
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

slowVoltageGear = DriveGear("Slow Voltage", rev.ControlType.kVoltage, gearRatio=1/21.55, 
moveScale=0.55, turnScale=0.8)
mediumVoltageGear = DriveGear("Medium Voltage", rev.ControlType.kVoltage, gearRatio=1/7.33,
moveScale=0.35, turnScale=0.15)
fastVoltageGear = DriveGear("Fast Voltage", rev.ControlType.kVoltage, gearRatio=1/7.33, 
moveScale=0.55, turnScale=0.8) 

slowVelocityGear = DriveGear("Slow Velocity", rev.ControlType.kVelocity,
    gearRatio=1/21.55, moveScale=5, turnScale=2.1, p=0.0000688, i=0.0000007, d=0.00001, f=0.0)
mediumVelocityGear = DriveGear("Medium Velocity", rev.ControlType.kVelocity,
    gearRatio=1/7.33, moveScale=6, turnScale=2, p=0.00007, i=0.0000007, d=0.00001, f=0.0)
fastVelocityGear = DriveGear("Fast Velocity", rev.ControlType.kVelocity,
    gearRatio=1/7.33, moveScale=10, turnScale=5.5, p=0.00007, i=0.0000007, d=0.0001, f=0.0)

slowPositionGear = DriveGear("Slow Position", rev.ControlType.kPosition,
    gearRatio=1/21.55, moveScale=4, turnScale=3, p=0.5, i=0.0, d=3.0, f=0.0)
mediumPositionGear = DriveGear("Medium Position", rev.ControlType.kPosition,
    gearRatio=1/7.33, moveScale=2, turnScale=1.5, p=0.5, i=0.0, d=3.0, f=0.0)
fastPositionGear = DriveGear("Fast Position", rev.ControlType.kPosition,
    gearRatio=1/7.33, moveScale=6, turnScale=5, p=0.5, i=0.0, d=3.0, f=0.0)

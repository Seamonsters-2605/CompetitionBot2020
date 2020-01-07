import seamonsters as sea
import math
from networktables import NetworkTables
import robot

ANGLE_THRESHHOLD = 2 # in degrees; if the target is off by this much or greater, shouldAlign() will return True

# very rough values
LIMELIGHT_HEIGHT = 16 # inches
TARGET_HEIGHT = 29 # inches

BASE_TARGET_RATIO = 1 / 3

# pipelines
DUAL_PIPELINE = 0
LEFT_PIPELINE = 1
RIGHT_PIPELINE = 2

def visionHasTarget(limelight):
        hasTargets = limelight.getNumber('tv', None)

        if hasTargets == None:
            print("No limelight connection")
            return False

        elif hasTargets == 0:
            print("No vision targets")
            return False

        return True

def getAngleOffset(limelight):

    limelight.putNumber('pipeline', DUAL_PIPELINE)

    hor = limelight.getNumber('thor',None) # horizontal value of the box
    vert = limelight.getNumber('tvert',None) # vertical value of the box

    offset = math.acos((hor / vert) * BASE_TARGET_RATIO)

    limelight.putNumber('pipeline', LEFT_PIPELINE)
    leftDist = getDistance(limelight.getNumber('ty',None))

    limelight.putNumber('pipeline', RIGHT_PIPELINE)
    rightDist = getDistance(limelight.getNumber('ty',None))

    if leftDist < rightDist:
        offset *= -1

    return 90 - offset

# this is inaccurate when the limelight is a similar height to the target
def getDistance(limelight):
    yAngle = limelight.getNumber('ty', None)

    leg = TARGET_HEIGHT - LIMELIGHT_HEIGHT

    return leg / math.tan(math.radians(yAngle)) * (1 - .234)

# uses the limelight to align with and drive into a vision target; returns True if completed without error
def driveIntoVisionTarget(robot : robot.CompetitionBot2020):

    if not visionHasTarget(robot.limelight):
        return False

    try:
        # Step 1: point at target

        robot.limelight.putNumber('pipeline', DUAL_PIPELINE)
        hOffset = robot.limelight.getNumber('tx', None)
        robot.turnDegrees(-hOffset)

        # Step 2: drive to the target

        dist = getDistance(robot.limelight)
        robot.driveDist(dist)

        robot.superDrive.drive(0,0,0)

        return True
    except:
        return False
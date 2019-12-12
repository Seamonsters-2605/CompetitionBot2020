import seamonsters as sea
import math
from networktables import NetworkTables
import robot

ANGLE_THRESHHOLD = 2 # in degrees; if the target is off by this much or greater, shouldAlign() will return True
LIMELIGHT_HEIGHT = 10 # inches
TARGET_HEIGHT = 30 # inches

BASE_TARGET_RATIO = 1 / 2

DUAL_PIPELINE = 0
LEFT_PIPELINE = 1
RIGHT_PIPELINE = 2

def visionHasTarget(limelight):
        hasTargets = limelight('tv', None)

        if hasTargets == None:
            print("No limelight connection")
            return False

        elif hasTargets == 0:
            print("No vision targets")
            return False

        return True

def getAngleOffset(limelight):

    limelight.putNumber('pipeline', DUAL_PIPELINE)

    hval = limelight.getNumber('thor')
    vval = limelight.getNumber('tvert')

    ratio = vval / hval

    offset = math.acos(ratio / BASE_TARGET_RATIO)

    limelight.putNumber('pipeline', LEFT_PIPELINE)
    leftDist = getDistance(limelight.getNumber('ty'))

    limelight.putNumber('pipeline', RIGHT_PIPELINE)
    rightDist = getDistance(limelight.getNumber('ty'))

    if leftDist < rightDist:
        offset *= -1

    return offset

def getDistance(yAngle):

    leg = TARGET_HEIGHT - LIMELIGHT_HEIGHT

    return leg / math.tan(yAngle)  

# uses the limelight to align with a vision target returns True if completes without error
def driveIntoVisionTarget(robot : robot.CompetitionBot2020):

    if not visionHasTarget(robot.limelight):
        return False

    # Step 1: point at target

    robot.limelight.putNumber('pipeline', DUAL_PIPELINE)
    hOffset = robot.limelight.getNumber('th')
    robot.turnDegrees(-1 * hOffset)

    # rough estimates
    while True:

        if not visionHasTarget(robot.limelight):
            return False
        
        yAngle = robot.limelight.getNumber('ty', None)

        dist = getDistance(yAngle)

        print(dist)

        yield

    robot.superDrive.drive(0,0,0)
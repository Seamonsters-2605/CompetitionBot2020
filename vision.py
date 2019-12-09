import seamonsters as sea
import math
from networktables import NetworkTables

ANGLE_THRESHHOLD = 2 # in degrees; if the target is off by this much or greater, shouldAlign() will return True
LIMELIGHT_HEIGHT = 10 # inches
TARGET_HEIGHT = 30 # inches

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

# uses the limelight to align with a vision target returns True if completes without error
def driveIntoVisionTarget(robot):

    # Step 1: point at target

    robot.limelight.putNumber('pipeline', DUAL_PIPELINE)

    # rough estimates
    while True:

        if not visionHasTarget(robot.limelight):
            return False
        
        yAngle = robot.limelight.getNumber('ty', None)
        leg = TARGET_HEIGHT - LIMELIGHT_HEIGHT

        dist = leg / math.tan(yAngle)

        print(dist)

        yield

    robot.superDrive.drive(0,0,0)
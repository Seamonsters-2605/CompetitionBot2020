import math, coordinates, drivetrain
from autoScheduler import Action
import seamonsters as sea

def driveToPoint(pathFollower, coord, speed, rotateAtTheEnd=False):
    drivetrain.mediumVelocityGear.applyGear(pathFollower.drive)

    if coord in coordinates.targetPoints:
        rotateAtTheEnd = True

    angle = None
    if rotateAtTheEnd:
        angle = coord.angle

    yield from sea.ensureTrue(
        pathFollower.driveToPointGenerator(coord.x, coord.y, angle, speed, 2, math.radians(5)), 25)

def createDriveToPointAction(pathFollower, coord, speed):
    return Action("Drive to " + coord.name,
        lambda: driveToPoint(pathFollower, coord, speed), "drive", coord)

def createRotateInPlaceAction(pathFollower, coord):
    newCoord = coordinates.FieldCoordinate("Rotated",
        pathFollower.robotX, pathFollower.robotY, coord.angle)
    
    return Action("Rotate to " + newCoord.name,
        lambda: driveToPoint(pathFollower, newCoord, 0.5, True), "rotate", newCoord)

def createRotateTowardsPointAction(robot, coord):
    # calculates the angle to rotate to be
    # facing at the point coord
    xDiff = coord.x - robot.pathFollower.robotX
    yDiff = coord.y - robot.pathFollower.robotY
    angle = math.atan2(yDiff, xDiff) - math.pi / 2

    newCoord = coordinates.FieldCoordinate("Rotated",
        robot.pathFollower.robotX, robot.pathFollower.robotY, angle)

    # rotates to where it thinks the location is
    # then uses the limelight to get very close
    return Action("Rotate towards " + newCoord.name,
        lambda: sea.sequence(driveToPoint(robot.pathFollower, newCoord, 0.5, True), 
        robot.faceVisionTarget()), "face", newCoord)

def waitOneSecond():
    yield from sea.wait(sea.ITERATIONS_PER_SECOND)

def endAuto(robot):
    yield
    robot.manualMode()

def createEndAction(robot):
    return Action("END", lambda: endAuto(robot), 0)

def setRobotPosition(pathFollower, coord):
    yield
    pathFollower.setPosition(coord.x, coord.y, coord.angle)

def createSetRobotPositionAction(pathFollower, coord):
    return Action("Set Starting Position", 
        lambda: setRobotPosition(pathFollower, coord), "set", coord)

# generic actions have a key that is the same as the index in the list
# so they can be recreated easily by the auto preset opener
def createGenericAutoActions(robot):
    return [
        createEndAction(robot),
        Action("Wait 1 sec", waitOneSecond, 1)
    ]
import math, coordinates, drivetrain
from autoScheduler import Action
import seamonsters as sea

def driveToPoint(pathFollower : sea.PathFollower, coord : coordinates.FieldCoordinate, speed):
    drivetrain.mediumVelocityGear.applyGear(pathFollower.drive)

    angle = sea.circleDistance(pathFollower.robotAngle, coord.angle) + pathFollower.robotAngle
    dist = math.hypot(coord.x - pathFollower.robotX, coord.y - pathFollower.robotY)
    if dist < 0.1:
        time = 1
    else:
        time = dist / speed
    yield from sea.ensureTrue(
        pathFollower.driveToPointGenerator(coord.x, coord.y, angle, time,
            0.2, math.radians(2)),
        25)

def createDriveToPointAction(pathFollower, coord, speed, key):
    return Action("Drive to " + coord.name,
        lambda: driveToPoint(pathFollower, coord, speed))

def rotateInPlace(pathFollower, angle):
    coord = coordinates.FieldCoordinate("Rotated",
        pathFollower.robotX, pathFollower.robotY, angle)
    yield from driveToPoint(pathFollower, coord, 5)

def createRotateInPlaceAction(pathFollower, angle):
    return Action("Rotate to " + str(round(math.degrees(angle))),
        lambda: rotateInPlace(pathFollower, angle))

def waitOneSecond():
    yield from sea.wait(sea.ITERATIONS_PER_SECOND)

def endAuto(robot):
    yield
    robot.manualMode()

def createEndAction(robot, key):
    return Action("END", lambda: endAuto(robot))
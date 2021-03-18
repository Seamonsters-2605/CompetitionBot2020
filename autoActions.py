import math, coordinates, sys, pickle, os
from autoScheduler import Action
import seamonsters as sea

def driveToPoint(pathFollower, coord, speed, rotateAtTheEnd=False):

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

def driveBezierPath(pathFollower, coordList, speed):
    yield from sea.ensureTrue(pathFollower.driveBezierPathGenerator(coordList, speed), 25)

def createBezierAction(pathFollower, coordList, speed):
    return Action("Bezier Curve", lambda: driveBezierPath(pathFollower, coordList, speed), "bezier", coordList)

def createRotateInPlaceAction(pathFollower, coord):
    newCoord = coordinates.FieldCoordinate("Rotated",
        pathFollower.robotX, pathFollower.robotY, coord.angle)
    
    return Action("Rotate to " + newCoord.name,
        lambda: driveToPoint(pathFollower, newCoord, 0.5, True), "rotate", newCoord)

def rotateTowardsPoint(robot, coord):
    # rotates to where it thinks the location is
    # then uses the limelight to get very close
    
    yield from driveToPoint(robot.pathFollower, coord, 0.5, True) 
        #robot.faceVisionTarget())

def createRotateTowardsPointAction(robot, coord):

    # calculates the angle to rotate to be
    # facing at the point coord
    xDiff = coord.x - robot.pathFollower.robotX
    yDiff = coord.y - robot.pathFollower.robotY
    angle = math.atan2(yDiff, xDiff) - math.pi / 2

    newCoord = coordinates.FieldCoordinate("Rotated",
        robot.pathFollower.robotX, robot.pathFollower.robotY, angle)

    return Action("Rotate towards " + newCoord.name,
        lambda: rotateTowardsPoint(robot, newCoord), "face", newCoord)

# runs the indexer for 3 seconds to shoot balls
# the shooter should already be running before this is called
def shoot(robot):
    while True:
        robot.indexer.start()
        if sys.argv[1] == "sim":
            yield from sea.waitSeconds(3)
        else:
            yield from sea.wait(150)
        robot.indexer.stop()
        robot.shooter.stop()
        break

def createShootAction(robot):
    return Action("Shoot", lambda: shoot(robot), "shoot")

def toggleIntake(robot):
    robot.intake.toggleIntake()
    robot.intake.toggleMotor()
    
    if robot.intake.running:
        robot.intake.start()
    else:
        robot.intake.stop()

def createToggleIntakeAction(robot):
    return Action("Toggle Intake", lambda: toggleIntake(robot), "intake")
    
def waitOneSecond():
    if sys.argv[1] == "sim":
        yield from sea.waitSeconds(1)
    else:
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

def setRobotAngleToCursor(pathFollower, coord):
    yield
    xdif = coord.x - pathFollower.robotX
    ydif = coord.y - pathFollower.robotY

    angle = -math.atan2(xdif, ydif)

    pathFollower.setPosition(
        pathFollower.robotX, 
        pathFollower.robotY, 
        angle
    )

def createSetRobotAngleToCursorAction(pathFollower, coord):
    return Action("Set Robot Starting Angle",
        lambda: setRobotAngleToCursor(pathFollower, coord), "angle", coord)

# generic actions have a key that is the same as the index in the list
# so they can be recreated easily by the auto preset opener
def createGenericAutoActions(robot):
    return [
        createEndAction(robot),
        Action("Wait 1 sec", waitOneSecond, 1)
    ]

def startRecording(robot):

    if robot.isRecording:
        print("Already recording robot data")
        return
    
    robot.recordedData = ([], [])
    robot.isRecording = True

def stopRecording(robot):

    if not robot.isRecording:
        print("Robot not recording")
        return

    robot.isRecording = False

def saveRecording(robot, filename):

    # Saves the file as an:
    # Autonomous Numeric Kinematic Library file (.ankl)

    with open(os.path.join(sea.getRobotPath('autoPresets'), filename + ".ankl"), "wb") as outFile:
        pickle.dump(robot.recordedData, outFile)

def driveRecordedPath(pathFollower, filename):
    yield from sea.ensureTrue(pathFollower.driveRecordedPathGenerator(filename))

def createDriveRecordedPathAction(pathFollower, filename):
    return Action("Recorded Path", lambda: driveRecordedPath(pathFollower, filename), "recorded")

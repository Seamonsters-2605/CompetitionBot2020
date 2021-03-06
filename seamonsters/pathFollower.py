import math, sys
import seamonsters as sea

class PathFollower:
    """
    Controls a SuperHolonomicDrive to follow paths on the field.
    """

    NAVX_LAG = 7 # frames
    NAVX_ERROR_CORRECTION = 0 # out of 1

    def __init__(self, drive, ahrs=None):
        """
        :param drive: a SuperHolonomicDrive
        :param x: starting x position of the robot, in feet
        :param y: starting y position of the robot, in feet
        :param angle: starting angle of the robot, radians.
            0 means the robot's local XY coordinates line up with the field XY
            coordinates.
        :param ahrs: an optional AHRS (NavX) instance. If provided, this will
            be used to track the robot's rotation; if not, the rotation will
            be calculated based on the movement of the motors.
        """
        self.drive = drive
        self._drivePositionState = None
        self.ahrs = ahrs
        self._ahrsOrigin = 0
        if ahrs is not None:
            self._ahrsOrigin = self._getAHRSAngle()
        self.robotX = 0
        self.robotY = 0
        self.robotAngle = 0

        self._robotAngleHistory = []

    def setPosition(self, x, y, angle):
        self.robotX = x
        self.robotY = y
        if angle is not None:
            self.robotAngle = angle
            if self.ahrs is not None:
                self._ahrsOrigin = 0
                self._ahrsOrigin = self._getAHRSAngle() - angle
            self._robotAngleHistory.clear()
        self._drivePositionState = None

    def _getAHRSAngle(self):
        return -math.radians(self.ahrs.getAngle()) - self._ahrsOrigin

    def updateRobotPosition(self):
        moveDist, moveDir, moveTurn, self._drivePositionState = \
            self.drive.getRobotPositionOffset(self._drivePositionState, target=False)
            # set the target to False because it is more accurate

        self.robotAngle += moveTurn
        self._robotAngleHistory.append(self.robotAngle)
        # pretty sure this isn't off by 1
        if len(self._robotAngleHistory) >= PathFollower.NAVX_LAG:
            laggedAngle = self._robotAngleHistory.pop(0)
            if self.ahrs is not None:
                navxAngle = self._getAHRSAngle()
                error = (navxAngle - laggedAngle) * PathFollower.NAVX_ERROR_CORRECTION
                self.robotAngle += error
                for i in range(0, len(self._robotAngleHistory)):
                    self._robotAngleHistory[i] += error

        robotDifX = math.cos(moveDir + self.robotAngle) * moveDist
        robotDifY = math.sin(moveDir + self.robotAngle) * moveDist

        self.robotY += robotDifY
        self.robotX += robotDifX

    def driveToPointGenerator(self, x, y, finalAngle=None, speed=1, robotPositionTolerance=0, robotAngleTolerance=0):
        """
        A generator to drive to a location on the field while simultaneously
        pointing the robot in a new direction. This will attempt to move the
        robot so it reaches the target position at a given speed and ends by 
        rotating to the inputted angle.
        This generator never exits, but yields ``True`` or ``False``
        if the robot is close enough to its target position, within tolerance.
        """
        dist, aDiff = self._robotVectorToPoint(x, y)
        for wheel in self.drive.wheels:
            wheel.resetPosition()

        if dist < 0.1: # TODO: constant
            dist = 0
        if abs(aDiff) < math.radians(1): # TODO
            aDiff = 0

        # if the robot has reached the angle or position
        hasReachedInitialAngle = False
        hasReachedPosition = False
        hasReachedFinalAngle = True
        if finalAngle is not None:
            hasReachedFinalAngle = False

        # if the robot should go backwards
        backwards = False

        accel = 0
        while True:
            accel += 0.1
            if accel > 1:
                accel = 1

            self.updateRobotPosition()

            dist, aDiff = self._robotVectorToPoint(x, y)

            # when it reaches the initial angle,
            # work towards the final angle
            if hasReachedPosition and not hasReachedFinalAngle:
                aDiff = finalAngle - self.robotAngle

            # make robot turn the shorter distance
            # and not always go clockwise
            aDiff %= math.pi * 2
            if aDiff > math.pi:
                aDiff -= math.pi * 2
            elif aDiff < -math.pi:
                aDiff += math.pi * 2

            if not hasReachedPosition:
                # decide if the robot should go 
                # backwards and adjust the angle
                if aDiff > math.pi / 2 and not aDiff < math.pi / 2 + math.degrees(5):
                    aDiff -= math.pi
                    backwards = True
                # the additional 5 degrees makes it not go backwards occasionally on accident
                elif aDiff < -math.pi / 2 and not aDiff > math.pi / 2 - math.degrees(5):
                    aDiff += math.pi
                    backwards = True

            # is the robot close enough to call it good?
            atPosition = abs(dist) <= robotPositionTolerance
            atAngle = abs(aDiff) <= robotAngleTolerance

            # updates the angle and position reached variables
            if not hasReachedInitialAngle:
                hasReachedInitialAngle = atAngle
            elif not hasReachedPosition:
                hasReachedPosition = atPosition
            elif not hasReachedFinalAngle:
                hasReachedFinalAngle = atAngle

            mag = dist * accel * speed
            aMag = -aDiff * accel * speed * 2
            
            # the robot is a simultaion
            if sys.argv[1] == 'sim':
                aMag *= -1

            if backwards:
                mag *= -1

            # once the robot reaches the initial angle,
            # it will drive forward until it reaches the 
            # position and then face the final angle 

            # turn to face the target first, then drive forward
            if not hasReachedInitialAngle or (hasReachedPosition and not hasReachedFinalAngle):
                self.drive.drive(0, 0, aMag)
            elif not hasReachedPosition:
                if abs(aDiff) > robotAngleTolerance: # so it will correct if the robot is off course
                    aMag *= 1.5
                self.drive.drive(mag, math.pi/2, aMag)

            yield hasReachedPosition and hasReachedFinalAngle

    def driveBezierPathGenerator(self, pointList, speed=4):

        curves = []
        l = len(pointList)

        def midpoint(p0, p1):
            return ((p0[0] + p1[0])/2, (p0[1] + p1[1])/2)

        curves.append((
            pointList[0],
            midpoint(pointList[0], midpoint(pointList[0], pointList[1])),
            midpoint(pointList[0], pointList[1])
        ))

        for curve in range(1, l-1):
            curves.append((
                midpoint(pointList[curve-1], pointList[curve]),
                pointList[curve],
                midpoint(pointList[curve], pointList[curve+1])
            ))
        
        curves.append((
            midpoint(pointList[l-1],pointList[l]),
            midpoint(midpoint(pointList[l-1],pointList[l]),pointList[l]),
            pointList[l]
        ))

        for curve in curves:

            distance_estimate = \
                math.hypot(curve[0,0] - curve[1,0], curve[0,1] - curve[1,1]) + \
                math.hypot(curve[1,0] - curve[2,0], curve[1,1] - curve[2,1])
            
            total_time = speed / distance_estimate

            def gx(t):
                return 2 * (curve[0,0] * (t - 1) - curve[1,0] * (2 * t - 1) + t * curve[2,0])

            def gy(t):
                return 2 * (curve[0,1] * (t - 1) - curve[1,1] * (2 * t - 1) + t * curve[2,1])
            
            def gpx(t):
                return 2 * (curve[2,0] - 2 * curve[1,0] + curve[0,0])

            def gpy(t):
                return 2 * (curve[2,1] - 2 * curve[1,1] + curve[0,1])

            for time in range(int(total_time * 50)):

                t = time / total_time / 50

                mag = math.sqrt(gx(t)*gx(t), gy(t)*gy(t)) / total_time
                turn = -(gpx(t) * gy(t) - gpy(t) * gx(t)) / (gx(t)*gx(t) + gy(t)*gy(t))

                self.drive.drive(mag, math.pi/2, turn)

                yield False
            
        yield True

    # return magnitude, angle
    def _robotVectorToPoint(self, x, y):
        xDiff = x - self.robotX
        yDiff = y - self.robotY
        return (math.sqrt(xDiff ** 2 + yDiff ** 2),
                math.atan2(yDiff, xDiff) - self.robotAngle - math.pi/2)
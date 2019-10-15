import math
import rev
import seamonsters as sea
import time

TWO_PI = math.pi * 2

# for AngledWheel
CHECK_DRIVE_ENCODER_CYCLE = 10 # cycles
MAX_DRIVE_ERROR = 6.0 # feet
MAX_POSITION_OCCURENCE = 10

# for SwerveWheel
CHECK_SWERVE_ENCODER_CYCLE = 50 # cycles
MAX_SWERVE_ERROR = 2 * math.pi / 3 # radians

# for spark max
DISABLED = 7

def _iteratePairs(list):
    for i in range(0, len(list) - 1):
        for j in range(i + 1, len(list)):
            yield list[i], list[j]


class Wheel:
    """
    Interface for wheels. A Wheel has a location and can put out force in a
    direction.
    """

    def __init__(self, x, y):
        """
        :param x: X offset from origin in feet
        :param y: Y offset from origin in feet
        """
        self.x = float(x)
        self.y = float(y)
        # if True, all calls to drive() or stop() will disable
        self.disabled = False
        # list of strings describing errors
        self.faults = []

    def limitMagnitude(self, magnitude, direction):
        """
        Return the scaling factor necessary to keep the wheel speed within its
        limits.

        :param magnitude: speed in feet per second
        :param direction: radians. 0 is right, positive counter-clockwise
        :return: 1.0 if wheel speed is within it limits, otherwise a value
            between 0 and 1 to scale the wheel down to its maximum speed.
        """
        return 1.0

    def drive(self, magnitude, direction):
        """
        Spin the wheel. This should be called 50 times per second.

        :param magnitude: speed in feet per second. Even if the magnitude is
            zero, the wheel will attempt to orient in the given direction
        :param direction: radians. 0 is right, positive counter-clockwise
        """
        if self.disabled:
            self.disable()
        else:
            self._drive(magnitude, direction)

    def _drive(self, magnitude, direction):
        pass

    def stop(self):
        """
        Stop driving.
        """
        if self.disabled:
            self.disable()
        else:
            self._stop()

    def _stop(self):
        pass

    def disable(self):
        """
        Disable motors. Calling drive() will enable them again.
        """

    def resetPosition(self):
        pass

    def getRealPosition(self):
        """
        :return: a value representing distance the wheel has travelled, which
            accumulates over the lifetime of the wheel.
        """
        return 0

    def getTargetPosition(self):
        """
        :return: target value for ``getRealPosition()`` -- where wheel is
            moving to
        """
        return 0

    def getRealDirection(self):
        """
        :return: the current direction the wheel is moving in radians. This may
            be based on sensors.
        """
        return 0

    def getTargetDirection(self):
        """
        :return: target value for ``getRealDirection()``
        """
        return 0

    def getRealVelocity(self):
        """
        :return: the current velocity of the wheel in feet per second, based on
            sensors.
        """
        return 0


class CasterWheel(Wheel):
    """
    Doesn't drive a motor, only stores its drive parameters and echoes them
    back for getRealDirection and getRealVelocity.
    """

    def __init__(self, x, y):
        super().__init__(x, y)
        self._storedMagnitude = 0
        self._storedDirection = 0
        self._distance = 0

    def _drive(self, magnitude, direction):
        self._storedMagnitude = magnitude
        self._storedDirection = direction
        self._distance += magnitude / sea.ITERATIONS_PER_SECOND
    
    def _stop(self):
        self._storedMagnitude = 0

    def getRealPosition(self):
        return self.getTargetPosition()
    
    def getTargetPosition(self):
        return self._distance

    def getRealDirection(self):
        return self.getTargetDirection()

    def getTargetDirection(self):
        return self._storedDirection

    def getRealVelocity(self):
        return self._storedMagnitude


class TestWheel(CasterWheel):
    """
    Logs parameters for drive(), for testing.
    """

    def __init__(self, name, x, y):
        """
        :param name: Name to include when logging parameters.
        :param x: X offset from origin in feet
        :param y: Y offset from origin in feet
        """
        super().__init__(x, y)
        self.name = name

    def _drive(self, magnitude, direction):
        super()._drive(magnitude, direction)
        print(self.name, "Mag:", magnitude, "Dir:", math.degrees(direction))

    def _stop(self):
        super()._stop()
        print(self.name, "stop")

    def disable(self):
        super().disable()
        print(self.name, "disable")


class AngledWheel(Wheel):
    """
    An AngledWheel is a wheel oriented in a fixed direction, which it can't
    change on its own. It uses a SparkMax to drive.
    """

    def __init__(self, motor: rev.CANSparkMax, x, y, angle,
                 encoderCountsPerFoot, maxVoltageVelocity, reverse=False):
        """
        :param motors: a SparkMax
        :param x: X position in feet
        :param y: Y position in feet
        :param angle: radians, direction of force. 0 is right, positive
            counter-clockwise
        :param encoderCountsPerFoot: number of encoder counts to travel 1 foot
        :param maxVoltageVelocity: velocity at 100% in voltage mode, in feet
            per second
        :param reverse: boolean, optional
        """
        super().__init__(x, y)
        self.motors = [motor]
        self.motorControllers = [rev._impl.CANPIDController(motor)]
        self.angle = angle
        self.encoderCountsPerFoot = encoderCountsPerFoot
        self.maxVoltageVelocity = maxVoltageVelocity
        self.reverse = reverse

        self.driveMode = rev.ControlType.kVoltage
        self.realTime = False

        self._motorState = None
        self._positionTarget = 0
        self._encoderCheckCount = 0
        self._oldPosition = 0
        self._positionOccurence = 0
        self._prevTime = time.time()
    
    # for wheels with gearboxes, so all motors can be driven at the same speed
    def addMotor(self, motor: rev.CANSparkMax):
        self.motors.append(motor)
        self.motorControllers.append(rev._impl.CANPIDController(motor))

    def limitMagnitude(self, magnitude, direction):
        # TODO: check position error in this function instead, and factor it
        # into the scale
        magnitude *= math.cos(direction - self.angle)
        if abs(magnitude) > self.maxVoltageVelocity:
            return self.maxVoltageVelocity / abs(magnitude)
        return 1.0

    def _encoderCheck(self):
        for motor in self.motors:
            newPosition = motor.getEncoder().getPosition()
            err = motor.setEncPosition(motor.getEncoder().getPosition())
            # setEncPosition() returns a CANError so we set it to the current
            # position to get the error but affect nothing
            if err == rev.CANError.kTimeout:
                print("Stale CAN frame so we won't check for errors :(",
                    motor.getDeviceId())
                return
            elif err != rev.CANError.kOK:
                print("Spark max error", motor.getDeviceId())

            if abs(newPosition - self._oldPosition) <= 1:
                self._positionOccurence += 1
            else:
                self._positionOccurence = 0
                self._oldPosition = newPosition

            if self._positionOccurence >= MAX_POSITION_OCCURENCE:
                self.faults.append("Encoder not moving")
                self._positionOccurence = 0

            if self.driveMode == rev.ControlType.kPosition:
                # TODO: this is arbitrary
                maxError = self.encoderCountsPerFoot * MAX_DRIVE_ERROR
                if abs(newPosition - self._positionTarget) > maxError:
                    self.faults.append("Can't reach target")
                    self._positionTarget = newPosition

    def _drive(self, inputMagnitude, direction):
        for motor in range(0, len(self.motors)):
            magnitude = inputMagnitude * math.cos(direction - self.angle)
            if self.reverse: 
                magnitude = -magnitude

            if self.driveMode == rev.ControlType.kPosition \
                    and self._motorState != self.driveMode:
                self._positionTarget = self.motors[motor].getEncoder().getPosition()
                self._encoderCheckCount = 0

            curTime = time.time()
            if self.realTime and self._motorState == self.driveMode:
                tDiff = curTime - self._prevTime
            else:
                tDiff = 1 / sea.ITERATIONS_PER_SECOND
            self._prevTime = curTime

            encoderCountsPerSecond = magnitude * self.encoderCountsPerFoot
            # always incremented, even if not in position mode
            # used by getTargetPosition
            self._positionTarget += encoderCountsPerSecond * tDiff

            if self.driveMode == DISABLED:
                if self._motorState != self.driveMode:
                    self.motors[motor].disable()
            elif self.driveMode == rev.ControlType.kVelocity:
                self.motorControllers[motor].setReference(encoderCountsPerSecond / 10.0, self.driveMode)
            elif self.driveMode == rev.ControlType.kPosition:
                self.motorControllers[motor].setReference(self._positionTarget, self.driveMode)
            elif self.driveMode == rev.ControlType.kVoltage:
                self.motorControllers[motor].setReference(magnitude / self.maxVoltageVelocity, self.driveMode)

            self._motorState = self.driveMode

            self._encoderCheckCount += 1
            # TODO: document constant
            if abs(encoderCountsPerSecond) > 400 \
                    and not self.driveMode == DISABLED:
                if self._encoderCheckCount % CHECK_DRIVE_ENCODER_CYCLE == 0:
                    # getEncoder().getPosition is slow so only check a few times
                    # per second
                    self._encoderCheck()
            else:
                self._positionOccurence = 0

    def _stop(self):
        self.drive(0, 0)

    def disable(self):
        if self._motorState != DISABLED:
            for motor in self.motors:
                motor.disable()
            self._motorState = DISABLED

    def resetPosition(self):
        self._motorState = None
    
    def _sensorPositionToDistance(self, pos):
        if self.reverse:
            pos = -pos
        return pos / self.encoderCountsPerFoot

    def getRealPosition(self):
        encPos = 0
        for motor in self.motors:
            encPos += motor.getEncoder().getPosition()
        encPos /= len(self.motors)
        return self._sensorPositionToDistance(encPos)

    def getTargetPosition(self):
        return self._sensorPositionToDistance(self._positionTarget)

    def getRealDirection(self):
        return self.getTargetDirection()

    def getTargetDirection(self):
        return self.angle

    def getRealVelocity(self):
        sensorVel = 0
        for motor in self.motors:
            sensorVel += motor.getEncoder().getVelocity()
        sensorVel /= len(self.motors)
        if self.reverse:
            sensorVel = -sensorVel
        return sensorVel * 10.0 / self.encoderCountsPerFoot


class MecanumWheel(AngledWheel):
    """
    An angled Mecanum wheel. The velocity of the wheel is scaled up to
    compensate for the effect of the rollers. For the angle of the wheel, use
    the diagonal direction of force in the diamond pattern.
    """

    SQRT_2 = math.sqrt(2)

    def limitMagnitude(self, magnitude, direction):
        return super().limitMagnitude(magnitude * MecanumWheel.SQRT_2, direction)

    def _drive(self, magnitude, direction):
        return super()._drive(magnitude * MecanumWheel.SQRT_2, direction)

    def getRealPosition(self):
        return super().getRealPosition() / MecanumWheel.SQRT_2

    def getTargetPosition(self):
        return super().getTargetPosition() / MecanumWheel.SQRT_2

    def getRealVelocity(self):
        return super().getRealVelocity() / MecanumWheel.SQRT_2


class SwerveWheel(Wheel):
    """
    A wheel which can rotate. A SwerveWheel drives using an AngledWheel, and
    rotates using a SparkMax.
    """

    def __init__(self, angledWheel: AngledWheel, steerMotor: rev.CANSparkMax,
                 encoderCountsPerRev, rotationVelocity, offsetX = 0, offsetY = 0,
                 reverseSteerMotor=False):
        """
        ``zeroSteering()`` is called in __init__.

        :param angledWheel: an AngledWheel for driving. Its angle will be
            updated as the swerve wheel rotates. The SwerveWheel will borrow its
            X/Y position when it's initialized.
        :param steerMotor: a SparkMax for rotating the swerve wheel. It should
            have a feedback sensor set for position mode.
        :param encoderCountsPerRev: number of encoder counts in a full rotation
            of the steer motor
        :param reverseSteerMotor: boolean, optional
        """
        super().__init__(angledWheel.x, angledWheel.y)
        self.angledWheel = angledWheel
        self.steerMotor = steerMotor
        self.encoderCountsPerRev = encoderCountsPerRev
        self.rotationVelocity = rotationVelocity
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.reverseSteerMotor = reverseSteerMotor

        self.zeroSteering()
        self._targetDirection = angledWheel.angle
        self._motorDisabled = True
        self._encoderCheckCount = 0

    def zeroSteering(self, currentAngle=0):
        """
        Reset the origin (rotation of wheel when facing right) so that the
        current position of the steer motor is ``currentAngle`` (defaults 0).
        """
        self._steerOrigin = self.steerMotor.getEncoder().getPosition()
        offset = currentAngle * self.encoderCountsPerRev / TWO_PI
        if self.reverseSteerMotor:
            offset = -offset
        self._steerOrigin -= offset
        self._simulatedCurrentDirection = self._getCurrentSteeringAngle()

    def limitMagnitude(self, magnitude, direction):
        return self.angledWheel.limitMagnitude(magnitude, direction)

    def _getCurrentSteeringAngle(self):
        offset = self.steerMotor.getEncoder().getPosition() \
                 - self._steerOrigin
        if self.reverseSteerMotor:
            offset = -offset
        return offset * TWO_PI / self.encoderCountsPerRev

    def _setSteering(self, direction):
        self._targetDirection = direction
        pos = direction * self.encoderCountsPerRev / TWO_PI
        if self.reverseSteerMotor:
            pos = -pos
        if self._motorDisabled:
            self.steerMotor.setIdleMode(rev.IdleMode.kBrake)
            self._motorDisabled = False
        self.steerMotor.setEncPosition(pos + self._steerOrigin)

    def _updateMotorPosition(self):
        if self._motorDisabled:
            return
        change = self.rotationVelocity / sea.ITERATIONS_PER_SECOND
        if abs(self._simulatedCurrentDirection - self._targetDirection) < change:
            self._simulatedCurrentDirection = self._targetDirection
        elif self._simulatedCurrentDirection > self._targetDirection:
            self._simulatedCurrentDirection -= change
        else:
            self._simulatedCurrentDirection += change
        
        self._encoderCheckCount += 1
        if self._encoderCheckCount % CHECK_SWERVE_ENCODER_CYCLE == 0:
            curPos = self._getCurrentSteeringAngle()
            if abs(curPos - self._simulatedCurrentDirection) > MAX_SWERVE_ERROR:
                self.faults.append("Can't reach target!")

    def _drive(self, magnitude, direction):
        self._updateMotorPosition()
        currentAngle = self._simulatedCurrentDirection
        # steering should never rotate more than 90 degrees from any position
        angleDiff = sea.circleDistance(currentAngle, direction, math.pi)
        target = currentAngle + angleDiff
        #print(math.degrees(currentAngle), math.degrees(target))
        self._setSteering(target)
        self.angledWheel.angle = currentAngle
        self.angledWheel.x = self.x + math.cos(currentAngle) * self.offsetX - math.sin(currentAngle) * self.offsetY
        self.angledWheel.y = self.y + math.sin(currentAngle) * self.offsetX + math.cos(currentAngle) * self.offsetY
        self.angledWheel.drive(magnitude, direction)

    def _stop(self):
        self._updateMotorPosition()
        self.angledWheel.stop()

    def disable(self):
        self.angledWheel.disable()
        if not self._motorDisabled:
            self.steerMotor.disable()
            self.steerMotor.setIdleMode(rev.IdleMode.kCoast)
            self._motorDisabled = True

    def resetPosition(self):
        self._simulatedCurrentDirection = self._getCurrentSteeringAngle()
        self.angledWheel.resetPosition()

    def getRealPosition(self):
        return self.angledWheel.getRealPosition()

    def getTargetPosition(self):
        return self.angledWheel.getTargetPosition()

    def getRealDirection(self):
        return self.angledWheel.getRealDirection()

    def getTargetDirection(self):
        return self._targetDirection

    def getRealVelocity(self):
        return self.angledWheel.getRealVelocity()


class SuperHolonomicDrive:

    def __init__(self):
        self.wheels = []
        self.autoDisableTime = sea.ITERATIONS_PER_SECOND # 1 second
        self._disableCounter = 0

    def addWheel(self, wheel):
        """
        Add a wheel to the set of drivetrain wheels.
        :param wheel: a ``Wheel``
        """
        self.wheels.append(wheel)

    def undisable(self):
        self._disableCounter = 0

    def drive(self, magnitude, direction, turn, wheelNum = None):
        """
        Drive the robot. This should be called 50 times per second.

        If drive is called with a magnitude/turn of 0 for more than
        ``autoDisableTime`` iterations, all wheels will be disabled.

        :param magnitude: feet per second
        :param direction: radians. 0 is right, positive counter-clockwise
        :param turn: radians per second. positive counter-clockwise
        :param wheelNum: optional int argument to drive a single wheel
        :return: the scale of the actual output speed, as a fraction of the
            input magnitude and turn components
        """
        if magnitude == 0 and turn == 0:
            self._disableCounter += 1
        else:
            self._disableCounter = 0
        if self._disableCounter > self.autoDisableTime:
            self.disable()
            return 1.0

        moveX = math.cos(direction) * magnitude
        moveY = math.sin(direction) * magnitude

        wheelMagnitudes = []
        wheelDirections = []
        wheelLimitScales = []

        if wheelNum is None:
            for wheel in self.wheels:
                wheelVectorX, wheelVectorY = self._calcWheelVector(
                    wheel, moveX, moveY, turn)
                wheelMag = math.sqrt(wheelVectorX ** 2.0 + wheelVectorY ** 2.0)
                wheelDir = math.atan2(wheelVectorY, wheelVectorX)
                wheelMagnitudes.append(wheelMag)
                wheelDirections.append(wheelDir)
                wheelLimitScales.append(wheel.limitMagnitude(wheelMag, wheelDir))

                minWheelScale = min(wheelLimitScales)
                for i in range(len(self.wheels)):
                    if wheelMagnitudes[i] == 0:
                        self.wheels[i].stop()
                    else:
                        self.wheels[i].drive(wheelMagnitudes[i] * minWheelScale,
                                            wheelDirections[i])
                return minWheelScale
        else:
            try:
                wheelVectorX, wheelVectorY = self._calcWheelVector(
                    self.wheels[wheelNum], moveX, moveY, turn)
                wheelMag = math.sqrt(wheelVectorX ** 2.0 + wheelVectorY ** 2.0)
                wheelDir = math.atan2(wheelVectorY, wheelVectorX)

                wheelScale = self.wheels[wheelNum].limitMagnitude(wheelMag, wheelDir)
                if wheelMag == 0:
                    self.wheels[wheelNum].stop()
                else:
                    self.wheels[wheelNum].drive(wheelMag * wheelScale, wheelDir)
                return wheelScale
            except:
                print("Wheel " + str(wheelNum) + " not in list of wheels")
    
    def orientWheels(self, magnitude, direction, turn):
        """
        Orient the wheels as if the robot was driving, but don't move.
        """
        self._disableCounter = 0
        moveX = math.cos(direction) * magnitude
        moveY = math.sin(direction) * magnitude

        for wheel in self.wheels:
            wheelVectorX, wheelVectorY = self._calcWheelVector(
                wheel, moveX, moveY, turn)
            if wheelVectorX != 0 and wheelVectorY != 0:
                wheelDir = math.atan2(wheelVectorY, wheelVectorX)
                wheel.drive(0, wheelDir)

    def disable(self):
        """
        Disable all motors. Calling drive() will enable them again.
        """
        # calling drive(0,x,0) after this will keep motors disabled
        self._disableCounter = self.autoDisableTime + 1
        for wheel in self.wheels:
            wheel.disable()

    def _calcWheelVector(self, wheel, moveX, moveY, turn):
        return moveX - wheel.y * turn, moveY + wheel.x * turn

    def getRobotMovement(self):
        """
        Get the movement of the robot as a whole, based on wheel sensors.

        :return: (magnitude, direction, turn). Magnitude in feet per second,
            direction in radians, turn in radians per second.
        """
        wheelValues = []
        for wheel in self.wheels:
            wheelMag = wheel.getRealVelocity()
            wheelDir = wheel.getRealDirection()
            dx = wheelMag * math.cos(wheelDir)
            dy = wheelMag * math.sin(wheelDir)
            wheelValues.append((wheel, dx, dy))
        return self._calcRobotMovement(wheelValues)

    def getRobotPositionOffset(self, origin, target=False):
        """
        Calculate how the robot has moved from a previous position.

        :param origin: an object returned by a previous call to
            ``getRobotPositionOffset``, for comparing previous state. Passing
            None will return an offset of 0 and a newly initialized state
        :param targetPosition: if False, the "real" position of wheels will be
            used based on encoder values. If True, the target position of
            wheels will be used based on where they were last told to move.
        :return: a tuple of ``(distance, direction, turn, state)`` where
            ``distance`` and ``direction`` define linear offset in feet and
            radians, ``turn`` defines angular offset in radians, and ``state``
            is an object that can be stored and passed to a future call of
            ``getRobotPositionOffset`` for comparison.
        """
        currentPositions = [
            (w.getTargetPosition() if target else w.getRealPosition())
            for w in self.wheels]
        if origin == None:
            return 0.0, 0.0, 0.0, currentPositions
        wheelValues = []
        for i in range(len(currentPositions)):
            wheel = self.wheels[i]
            wheelMag = currentPositions[i] - origin[i]
            wheelDir = wheel.getTargetDirection() if target \
                else wheel.getRealDirection()
            dx = wheelMag * math.cos(wheelDir)
            dy = wheelMag * math.sin(wheelDir)
            wheelValues.append((wheel, dx, dy))
        outMag, outDir, outTurn = self._calcRobotMovement(wheelValues)
        return outMag, outDir, outTurn, currentPositions

    # wheel values is a list of (wheel, dx, dy)
    # return (mag, dir, turn)
    def _calcRobotMovement(self, wheelValues):
        totalX = 0
        totalY = 0
        totalA = 0
        pairCount = 0
        for (wheelA, aDx, aDy), (wheelB, bDx, bDy) in _iteratePairs(wheelValues):
            # calc wheel b relative to wheel a
            relPosX = wheelB.x - wheelA.x
            relPosY = wheelB.y - wheelA.y
            relPosMag = math.sqrt(relPosX ** 2 + relPosY ** 2)
            relPosDir = math.atan2(relPosY, relPosX)
            relVelX = bDx - aDx
            relVelY = bDy - aDy
            relVelDir = math.atan2(relVelY, relVelX)
            relVelMag = math.sqrt(relVelX ** 2 + relVelY ** 2)

            totalX += (aDx + bDx) / 2
            totalY += (aDy + bDy) / 2
            totalA += relVelMag * math.sin(relVelDir - relPosDir) / relPosMag
            pairCount += 1
        totalX /= pairCount
        totalY /= pairCount
        totalA /= pairCount

        return math.sqrt(totalX ** 2 + totalY ** 2), math.atan2(totalY, totalX), totalA


if __name__ == "__main__":
    drive = SuperHolonomicDrive()
    drive.addWheel(TestWheel("Wheel A", 1, 1))
    drive.addWheel(TestWheel("Wheel B", -1, 1))
    drive.addWheel(TestWheel("Wheel C", 1, -1))
    drive.addWheel(TestWheel("Wheel D", -1, -1))

    def testDrive(mag, dir, turn):
        print("Drive Input mag:", mag, "dir:", math.degrees(dir), "turn:", turn)
        drive.drive(mag, dir, turn)
        magOut, dirOut, turnOut = drive.getRobotMovement()
        print("Drive Output mag:", magOut, "dir:", math.degrees(dirOut), "turn:", turnOut)

    testDrive(0, 0, 0)
    testDrive(4, math.radians(90), 0)
    testDrive(-5, math.radians(46), 0)
    testDrive(0, 0, 1)
    testDrive(-5, math.radians(46), 3)

import wpilib
import rev
import drivetrain
import seamonsters as sea 
import math
import navx
import dashboard
import autoScheduler
import vision
from networktables import NetworkTables

SOLENOID_FORWARD = wpilib.DoubleSolenoid.Value.kForward
SOLENOID_REVERSE = wpilib.DoubleSolenoid.Value.kReverse

class CompetitionBot2020(sea.GeneratorBot):

    def robotInit(self):

        # devices
        self.controller = wpilib.XboxController(0)

        ahrs = navx.AHRS.create_spi()

        self.pdp = wpilib.PowerDistributionPanel(50)

        self.ledStrip = wpilib.PWM(0)
        self.ledInput = -0.99

        self.superDrive = drivetrain.initDrivetrain()
        # multiDrive allows the robot to be driven multiple times in a loop and the values are averaged
        self.multiDrive = sea.MultiDrive(self.superDrive) 
        self.pathFollower = sea.PathFollower(self.superDrive, ahrs)

        self.limelight = NetworkTables.getTable('limelight')
        self.limelight.putNumber('pipeline', vision.DUAL_PIPELINE)

        # for autonomous mode
        self.autoScheduler = autoScheduler.AutoScheduler()
        self.autoScheduler.idleFunction = self.autoIdle
        self.autoScheduler.updateCallback = self.updateScheduler

        # controls the state of the robot
        self.controlModeMachine = sea.StateMachine()
        self.manualState = sea.State(self.driving)
        self.autoState = sea.State(self.autoScheduler.runSchedule)
        self.testState = sea.State(self.testing)

        # for shifting gear box
        self.compressor = wpilib.Compressor(0)
        self.compressor.stop()
        self.piston1 = wpilib.DoubleSolenoid(0, 1)
        self.piston2 = wpilib.DoubleSolenoid(2, 3)

        # drive gears
        self.superDrive.gear = None
        self.driveGear = drivetrain.mediumVelocityGear
        self.driveMode = "velocity"
        self.driveSpeed = "medium"
        self.driveGears = \
            {"voltage" : \
                {"slow" : drivetrain.slowVoltageGear, 
                "medium" : drivetrain.mediumVoltageGear, 
                "fast" : drivetrain.fastVoltageGear}, 
            "velocity" : \
                {"slow" : drivetrain.slowVelocityGear, 
                "medium" : drivetrain.mediumVelocityGear, 
                "fast" : drivetrain.fastVelocityGear},      
            "position" : \
                {"slow" : drivetrain.slowPositionGear, 
                "medium" : drivetrain.mediumPositionGear, 
                "fast" : drivetrain.fastPositionGear} 
            }

        # testing
        self.testSettings = { \
            "wheelNum" : 0,
            "motorNum" : 0,
            "speed" : 0
            }

        # for dashboard motor data
        self.motorData = [dict() for _ in range(len(self.superDrive.motors))]

        # sets initial values so the dashboard doesn't break when it tries to get 
        # them before the values are updated in self.updateMotorData
        for motor in range(len(self.superDrive.motors)):
            initAmps = round(self.superDrive.motors[motor].getOutputCurrent(), 2) 
            initTemp = round(self.superDrive.motors[motor].getMotorTemperature(), 2)

            self.motorData[motor]["amps"] = initAmps
            self.motorData[motor]["temp"] = initTemp

            self.motorData[motor]["maxAmp"] = initAmps
            self.motorData[motor]["maxTemp"] = initTemp

        self.app = None 
        sea.startDashboard(self, dashboard.CompetitionDashboard)

    # Different Driving Modes

    # robot is controlled by the driver
    def teleop(self):
        self.manualMode()
        yield from self.mainGenerator()

    # robot is controlled by the code
    def autonomous(self):
        self.autoMode()
        yield from self.mainGenerator()

    # robot is being tested off the field
    def test(self):
        self.testMode()
        yield from self.mainGenerator()

    # runs every 50th of a second
    def mainGenerator(self):

        self.superDrive.resetWheelPositions()

        yield from sea.parallel(
            self.controlModeMachine.updateGenerator(), 
            self.updateDashboardGenerator(),
            self.updateMotorData())

    # switches the robot into teleop
    def manualMode(self):
        for wheel in self.superDrive.wheels:
            wheel.setIdleMode(rev.IdleMode.kBrake)
         
        self.piston1.set(SOLENOID_FORWARD)
        self.piston2.set(SOLENOID_FORWARD)

        self.controlModeMachine.replace(self.manualState)

    # switches the robot into auto
    def autoMode(self):
        for wheel in self.superDrive.wheels:
            wheel.setIdleMode(rev.IdleMode.kBrake)
         
        self.controlModeMachine.replace(self.autoState)

    # switches the robot into test mode
    def testMode(self):
        for wheel in self.superDrive.wheels:
            wheel.setIdleMode(rev.IdleMode.kCoast)
            
        self.superDrive.disable()
        self.controlModeMachine.replace(self.testState)

    # is run in teleop to get input and make the robot go 
    def driving(self):
        while True:

            self.pathFollower.updateRobotPosition()
            
            if self.superDrive.gear != self.driveGear:
                self.driveGear.applyGear(self.superDrive)
                if self.app is not None:
                    self.app.gearGroup.highlight(self.driveMode)
                    self.app.speedGroup.highlight(self.driveSpeed)

            if self.piston1.get() == SOLENOID_REVERSE and self.driveSpeed != "slow":
                self.piston1.set(SOLENOID_FORWARD)
                self.piston2.set(SOLENOID_FORWARD)
            elif self.piston1.get() == SOLENOID_FORWARD and self.driveSpeed == "slow":
                self.piston1.set(SOLENOID_REVERSE)
                self.piston2.set(SOLENOID_REVERSE)

            turn = sea.deadZone(self.controller.getX(1), deadZone=0.05)
            turn *= self.driveGear.turnScale
            mag = -sea.deadZone(self.controller.getY(0), deadZone=0.05)
            mag *= self.driveGear.moveScale

            self.multiDrive.drive(mag, math.pi/2, turn)
            self.multiDrive.update()

            self.ledStrip.setSpeed(self.ledInput)

            if self.controller.getAButtonPressed():
                yield from self.faceVisionTarget()
            if self.controller.getBumper(0):
                # the robot works towards aligning with a vision 
                # target while the bumper is being held down
                self._turnDegree(None, accuracy=0, multiplier=9, visionTarget=True)
        
            yield

    # switches to use the dashboard for testing purposes
    def testing(self):
        while True:

            self.superDrive.wheels[self.testSettings["wheelNum"]]._drive( \
                self.testSettings["speed"] * self.driveGear.moveScale, \
                math.pi/2, self.testSettings["motorNum"])

            yield

    # runs in autonomous when nothing else is going
    def autoIdle(self):
        self.pathFollower.updateRobotPosition()
        self.superDrive.drive(0, 0, 0)

    # Helpful Movement Functions

    # turns the robot a small fraction of the inputted value degree.
    # if called in a loop, the result will be the robot turning the desired amount
    def _turnDegree(self, degrees, accuracy=3, multiplier=1, visionTarget=False):
        # if degrees is None, the robot will *only* try to allign
        # with a vision target and not move otherwise
        
        # visionTarget: weather or not the robot will try to align to a vision target

        if degrees is None and not visionTarget:
            raise ValueError("visionTarget must be True if degrees is None")

        self.pathFollower.updateRobotPosition()

        if visionTarget:

            if vision.targetDetected(self.limelight):
                hOffset = -vision.getXOffset(self.limelight)

            elif degrees is None:
                return False

            # prevents robot from spinning uncontrollably
            if abs(hOffset) < 180:
                offset = hOffset

        else:
            offset = math.degrees(self.pathFollower.robotAngle) + degrees

        # as the robot gets closer to the target angle, it will slow down
        speed = (-offset / 360) * multiplier
        if speed > 1:
            speed = 1
        speed *= self.driveGear.turnScale

        self.multiDrive.drive(0, math.pi/2, speed) 
    
        # returns if the robot is within the desired accuracy
        return -accuracy < abs(offset) < accuracy

    # turns the robot a certain amount
    # or aligns with a vision target if visionTarget is True
    def turnDegrees(self, degrees, accuracy=3, multiplier=1, visionTarget=False):

        # the function ends if the robot is looking for a vision target but there are none
        if visionTarget:
            self.limelight.putNumber('pipeline', vision.DUAL_PIPELINE)

            if not vision.targetDetected(self.limelight):
                return False

        # stops the robot from spinnig uncontrollably
        if degrees > 180:
            return False

        accuracy = abs(accuracy)
        accuracyCount = 0 # the amount of iterations the robot has been within the accuracy range

        while True:
            accurate = self._turnDegree(degrees, accuracy, multiplier, visionTarget)
            self.multiDrive.update()
            
            if accurate:
                accuracyCount += 1
            else:
                accuracyCount = 0

            if accuracyCount > 5:
                return True

            yield

    def faceVisionTarget(self):
        self.limelight.putNumber('pipeline', vision.DUAL_PIPELINE)
        hOffset = vision.getXOffset(self.limelight)

        if not vision.targetDetected(self.limelight) or abs(hOffset) > 180:
            return False

        yield from self.turnDegrees(-hOffset, accuracy=2, multiplier=9, visionTarget=True)

    # drives the robot a specified distance in a straight line
    # distance measured in feet
    def driveDist(self, distance, accuracy=0.025, slowDist=1):
        accuracy = abs(accuracy)
        accuracyCount = 0 # the amount of iterations the robot has been within the accuracy range

        # the right side is negative because the motor is turned around
        targetDistL = self.superDrive.wheels[0].getRealPosition() + distance
        targetDistR = -self.superDrive.wheels[1].getRealPosition() + distance
        targetDist = (targetDistL + targetDistR) / 2

        def getLocation():
            locationL = self.superDrive.wheels[0].getRealPosition()
            locationR = -self.superDrive.wheels[1].getRealPosition()
            location = (locationL + locationR) / 2

            return location

        while True:
            self.pathFollower.updateRobotPosition()

            offset = targetDist - getLocation()
            
            # the robot will start to slow down once it is 
            # slowDist feet away from the target
            speed = offset / slowDist 
            if speed > 1:
                speed = 1
            speed *= self.driveGear.moveScale
            
            self.multiDrive.drive(speed, math.pi/2, 0)
            self.multiDrive.update()

            if -accuracy < abs(offset) < accuracy:
                accuracyCount += 1
            else:
                accuracyCount = 0

            if accuracyCount > 5:
                return True

            yield

    # updates the dashboard
    def updateDashboardGenerator(self):
        if self.app is not None:
            self.app.clearEvents()
        while True:
            v = None
            if self.app is not None:
                v = self.app.doEvents()
            yield v

    # updates the motor data for the dashboard
    def updateMotorData(self):
        while True:

            for motor in range(len(self.superDrive.motors)):
                amps = round(self.superDrive.motors[motor].getOutputCurrent(), 2)
                temp = round(self.superDrive.motors[motor].getMotorTemperature(), 2)

                self.motorData[motor]["amps"] = amps
                self.motorData[motor]["temp"] = temp

                if amps > self.motorData[motor]["maxAmp"]:
                    self.motorData[motor]["maxAmp"] = amps

                if temp > self.motorData[motor]["maxTemp"]:
                    self.motorData[motor]["maxTemp"] = temp

            yield

    # updates self.autoScheduler to run functions in autonomous
    def updateScheduler(self):
        # needs work

        pass

    # Dashboard Callbacks
    
    @sea.queuedDashboardEvent
    def c_changeGear(self, button):
        self.driveMode = button.get_text()
        self.driveGear = self.driveGears[self.driveMode][self.driveSpeed]

    @sea.queuedDashboardEvent
    def c_changeSpeed(self, button):
        self.driveSpeed = button.get_text()
        self.driveGear = self.driveGears[self.driveMode][self.driveSpeed]

    @sea.queuedDashboardEvent
    def c_stop(self, button):
        self.superDrive.disable()

    @sea.queuedDashboardEvent
    def c_compressor(self, button):
        if self.app is not None:
            if button.get_text() == "start":
                self.compressor.start()
                self.app.compressorGroup.highlight("start")
            else:
                self.compressor.stop()
                self.app.compressorGroup.highlight("stop")

if __name__ == "__main__":
    wpilib.run(CompetitionBot2020)
import wpilib
import rev
import drivetrain
import seamonsters as sea 
import math
import navx
import dashboard
import autoScheduler

SOLENOID_FORWARD = wpilib.DoubleSolenoid.Value.kForward
SOLENOID_REVERSE = wpilib.DoubleSolenoid.Value.kReverse

# determines how many iterations back to average 
# to get the value to set the motor to
SPEED_CONTROL_AMOUNT = 5

class CompetitionBot2020(sea.GeneratorBot):

    def robotInit(self):

        # devices
        self.joystick = wpilib.Joystick(0)
        self.buttonBoard = wpilib.Joystick(1)

        ahrs = navx.AHRS.create_spi()

        self.pdp = wpilib.PowerDistributionPanel(50)

        self.superDrive = drivetrain.initDrivetrain()
        self.pathFollower = sea.PathFollower(self.superDrive, ahrs)

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
        self.piston1 = wpilib.DoubleSolenoid(0, 1)
        self.piston2 = wpilib.DoubleSolenoid(2, 3)

        # drive gears
        self.superDrive.gear = None
        self.driveGear = drivetrain.mediumVoltageGear
        self.driveMode = "voltage"
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

        # every loop, this gets the current input
        # value from the joystick and puts it in 
        # the list, the oldest value is removed and
        # they are all averaged to set the speed of 
        # the motors
        self.speedControlList = [0 for _ in range(SPEED_CONTROL_AMOUNT)]

        self.app = None 
        sea.startDashboard(self, dashboard.CompetitionDashboard)

    # different driving modes

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

        yield from sea.parallel(
            self.controlModeMachine.updateGenerator(), 
            self.buttonControl(),
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

            mag = sea.deadZone(self.joystick.getY()) 
            mag *= self.driveGear.moveScale # maximum feet per second
            turn = sea.deadZone(self.joystick.getX())
            turn *= self.driveGear.moveScale # maximum radians per second
           
            # sets to the average of the past SPEED_CONTROL_AMOUNT
            # number of inputs including the current one
            mag = self.speedControl(mag, self.speedControlList)

            self.superDrive.drive(mag, math.pi/2, turn)

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

    # takes in input from the physical driver station
    def buttonControl(self):
        # clears events on buttons
        for button in range(1, 11):
            self.buttonBoard.getRawButtonPressed(button)

        while True:

            if self.buttonBoard.getRawButtonPressed(3):
                self.driveSpeed = "slow"
            elif self.buttonBoard.getRawButtonPressed(4):
                self.driveSpeed = "medium"
            elif self.buttonBoard.getRawButtonPressed(5):
                self.driveSpeed = "fast"

            if self.buttonBoard.getRawButtonPressed(2):
                self.toggleDriveMode()

            self.driveGear = self.driveGears[self.driveMode][self.driveSpeed]

            yield

    # changes the drive mode when the button
    # on the driver station is pressed
    def toggleDriveMode(self):
        if self.driveMode == "voltage":
            self.driveMode = "velocity"
            
        # position mode is too funky to use 

        #elif self.driveMode == "velocity":
        #    self.driveMode = "position"

        else:
            self.driveMode = "voltage"

    # used for shifting and averaging the speedControl lists
    def speedControl(self, value, speedControlList):
        speedControlList.append(value)
        speedControlList.pop(0)

        average = 0
        for num in speedControlList:
            average += num
        
        average /= len(speedControlList)

        return average


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

    @sea.queuedDashboardEvent
    def c_changeSpeed(self, button):
        self.driveSpeed = button.get_text()

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
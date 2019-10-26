import wpilib
import drivetrain
import seamonsters as sea 
import math
import navx
import dashboard

class CompetitionBot2020(sea.GeneratorBot):

    def robotInit(self):

        # devices
        self.controller = wpilib.XboxController(0)
        self.buttonBoard = wpilib.Joystick(1)

        ahrs = navx.AHRS.create_spi()

        self.pdp = wpilib.PowerDistributionPanel(50)

        self.superDrive = drivetrain.initDrivetrain()
        self.pathFollower = sea.PathFollower(self.superDrive, ahrs)

        self.controlModeMachine = sea.StateMachine()
        self.manualState = sea.State(self.driving)
        self.autoState = sea.State(self.auto)
        self.testState = sea.State(self.testing)

        # for shifting gear box
        self.compressor = wpilib.Compressor(0)
        self.piston1 = wpilib.Solenoid(0)# pcm 0 and 2
        self.piston2 = wpilib.Solenoid(1)# pcm 1 and 3

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

        self.app = None 
        sea.startDashboard(self, dashboard.CompetitionDashboard)

    def teleop(self):
        self.manualMode()
        yield from self.mainGenerator()

    def autonomous(self):
        self.autoMode()
        yield from self.mainGenerator()

    def test(self):
        self.testMode()
        yield from self.mainGenerator()

    def mainGenerator(self):

        yield from sea.parallel(
            self.controlModeMachine.updateGenerator(), 
            self.buttonControl(),
            self.updateDashboardGenerator())

    def manualMode(self):
        self.controlModeMachine.replace(self.manualState)

    def autoMode(self):
        self.controlModeMachine.replace(self.autoState)

    def testMode(self):
        self.superDrive.disable()
        self.controlModeMachine.replace(self.testState)

    def driving(self):
        self.piston2.set(self.piston1.get())
        while True:

            self.pathFollower.updateRobotPosition()
            
            if self.superDrive.gear != self.driveGear:
                self.driveGear.applyGear(self.superDrive)
                self.app.gearGroup.highlight(self.driveMode)
                self.app.speedGroup.highlight(self.driveSpeed)

            # must be changed when I get more details
            if self.piston1.get() and self.driveSpeed != "slow":
                self.piston1.set(False)
                self.piston2.set(False)
            elif not self.piston1.get() and self.driveSpeed == "slow":
                self.piston1.set(True)
                self.piston2.set(True)

            lMag = -sea.deadZone(self.controller.getY(0)) 
            lMag *= self.driveGear.moveScale # maximum feet per second
            rMag = sea.deadZone(self.controller.getY(1))
            rMag *= self.driveGear.moveScale
            

            self.superDrive.drive(rMag, math.pi/2, 0, 1)
            self.superDrive.drive(lMag, math.pi/2, 0, 0)

            yield

    def auto(self):
        while True:

            #put the stuff here
            
            yield

    def testing(self):
        while True:

            self.superDrive.wheels[self.testSettings["wheelNum"]]._drive( \
                self.testSettings["speed"] * self.driveGear.moveScale, \
                math.pi/2, self.testSettings["motorNum"])

            yield

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

    def toggleDriveMode(self):
        if self.driveMode == "voltage":
            self.driveMode = "velocity"
            
        # position mode is too funky to use 

        #elif self.driveMode == "velocity":
        #    self.driveMode = "position"
        else:
            self.driveMode = "voltage"

    def updateDashboardGenerator(self):
        if self.app is not None:
            self.app.clearEvents()
        while True:
            v = None
            if self.app is not None:
                v = self.app.doEvents()
            yield v

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
        if button.get_text() == "start":
            self.compressor.start()
            self.app.compressorGroup.highlight("start")
        else:
            self.compressor.stop()
            self.app.compressorGroup.highlight("stop")

if __name__ == "__main__":
    wpilib.run(CompetitionBot2020)
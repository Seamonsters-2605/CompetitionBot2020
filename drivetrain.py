import seamonsters as sea 
import rev

def initDrivetrain():
    superDrive = sea.SuperHolonomicDrive()
    _makeWheel(superDrive, 1, rev.MotorType.kBrushless, -1, 0)
    _makeWheel(superDrive, 2, rev.MotorType.kBrushless, 1, 0)
    sea.setSimulatedDrivetrain(superDrive)
    return superDrive

def _makeWheel(superDrive, sparkMaxNum, motorType, xPos, yPos):
    sparkMax = rev.CANSparkMax(sparkMaxNum, motorType)
    sparkMax.restoreFactoryDefaults()
    sparkMax.setIdleMode(rev.IdleMode.kBrake)

    angledWheel = sea.AngledWheel(sparkMax, xPos, yPos, 0, 1, 16)

    superDrive.addWheel(angledWheel)
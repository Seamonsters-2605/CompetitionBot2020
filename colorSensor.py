import wpilib
from rev.color import ColorSensorV3

colorSensor = ColorSensorV3(wpilib.I2C.Port.kOnboard)

def getColor():
    detectedColor = colorSensor.getColor()
    return (detectedColor.red, detectedColor.blue, detectedColor.green)
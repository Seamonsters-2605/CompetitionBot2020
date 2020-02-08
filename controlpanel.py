import robot, random, colorSensor

cpColors = ["R","Y","B","G"] # The order of colors as they show up on the control panel, clockwise

# It then returns the value of that color, shifted STEPS colors clockwise. 
# For example, typing shiftColor("red", 2) will return "blue" because that is two colors clockwise of red on the color wheel.
def shiftColor(color : str, steps : int) -> int:
    colorIndex = cpColors.index(color) # the index of the given color on the control panel.
    newColorIndex = (colorIndex + steps) % 4 # the index of the given color, shifted two colors clockwise.
    return cpColors[newColorIndex]

# Turns the wheel clockwise until it is on the next color.
def nextColor(): 
    startColor = colorSensor.getColor() # the color the camera starts on
    endColor = shiftColor(startColor, 1)
    colorsSeen = [startColor]*5 # The previous 5 colors the camera has seen, from most recent (4) to oldest (0)

    # keeps turning the wheel until it's on the correct color
    while not (colorsSeen == [endColor]*5): 
        #rotate(x degrees) THIS IS A PLACEHOLDER
        colorsSeen.append(colorSensor.getColor()) # Records the current color
        del colorsSeen[0]

    # rotates the control panel a little bit more. Ideally, this puts the middle of the pie slice below the color sensor.
    for _ in range(5): 
        #rotate(x degrees) also a placeholder
        pass

    print("turned to color " + colorSensor.getColor())

# turns control panel certain number of rotations
def rotate(rotations):
    for _ in range(0, rotations * 8):
        nextColor()
    
    print("finished rotate(), on color " + colorSensor.getColor())

# Turns the control panel until it's on the requested color
def goto(color): 
    while colorSensor.getColor() != color:
        nextColor()

    print("finished goto(), on color " + colorSensor.getColor())
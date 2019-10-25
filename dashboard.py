import remi.gui as gui
import seamonsters as sea

class CompetitionDashboard(sea.Dashboard):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, css=True, **kwargs)

    def main(self, robot, appCallback):

        root = gui.VBox(gui.Label("Drive controls"), width = 600, margin = "0px auto")

        manualBox = gui.VBox()
        gearButtons = []
        speedButtons = []
        compressorButtons = []
        
        self.gearGroup = sea.ToggleButtonGroup()
        for mode in robot.driveGears.keys():
            button = gui.Button(mode)
            button.set_on_click_listener(robot.c_changeGear)
            gearButtons.append(button)
            self.gearGroup.addButton(button)
        
        self.speedGroup = sea.ToggleButtonGroup()
        for speed in robot.driveGears[robot.driveMode].keys():
            button = gui.Button(speed)
            button.set_on_click_listener(robot.c_changeSpeed)
            print("onclick: " + button.EVENT_ONCLICK)
            speedButtons.append(button)
            self.speedGroup.addButton(button)

        self.compressorGroup = sea.ToggleButtonGroup()
        for mode in ["start","stop"]:
            button = gui.Button(mode)
            button.set_on_click_listener(robot.c_compressor)
            compressorButtons.append(button)
            self.compressorGroup.addButton(button)
        
        gearBox = sea.hBoxWith(gui.Label("Gears:"),gearButtons)
        speedBox = sea.hBoxWith(gui.Label("Speed:"),speedButtons)
        compressorBox = sea.hBoxWith(gui.Label("Compressor:",),compressorButtons)

        manualBox.append(gearBox)
        manualBox.append(speedBox)
        manualBox.append(compressorBox)

        root.append(manualBox)

        appCallback(self)
        return root
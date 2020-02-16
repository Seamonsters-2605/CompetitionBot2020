# Competition Bot 2020

**2020 Features:**

- Universal drivetrain controller: Same control code can be configured for swerve, tank, mecanum, or omni drives in any wheel configuration.
- Position tracking: Uses wheel encoders and the NavX to track the robot’s position on the field accurately. This is integrated with the universal drivetrain controller, so it will work for any type of drivetrain.
- Path following: Using position tracking, the robot can navigate to points on the field.
- Custom web-based dashboard. The server is hosted on the roboRIO and shares data with the robot code. Works in any web browser without additional software.
  - Includes a map of the robot’s position on the field. Click to navigate to a point.
  - A sequence of autonomous actions can be assembled and saved before or during a match. The schedule can be altered in real time.
- All robot code uses coroutines.
  - A coroutine is a function that can pause its execution and resume later, allowing time to perform other actions such as other coroutines.
  - This makes it easy to build complex sequences that change over time, without complicated state management.
  - It is simple to assemble sequences of commands, and run actions in parallel. These are similar to the capabilities of the wpilib “Command” framework, but coroutine code is cleaner to read and write.
- Automated actions are integrated with manual control. Any part of the robot's actions during a match can be automated, and during a match we can alternate between autonomous and manual control.
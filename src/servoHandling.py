from itertools import chain

from roboCarHelper import map_value_to_new_scale
import pigpio

class ServoHandling:
    def __init__(self, servoPins, minAngles, maxAngles):
        self._pigpioPwm = pigpio.pi()

        self._pwmAbsoluteMin: int = 500  # value all the way to the right
        self._pwmAbsoluteMax: int = 2500  # value all the way to the left

        self._servoPins: dict = {
            "horizontal": servoPins[0],
            "vertical": servoPins[1]
        }

        self._pwmMinValues: dict = {
            "horizontal": map_value_to_new_scale(
                minAngles[0],
                self._pwmAbsoluteMin,
                self._pwmAbsoluteMax,
                1,
                -90,
                90
            ),
            "vertical": map_value_to_new_scale(
                minAngles[1],
                self._pwmAbsoluteMin,
                self._pwmAbsoluteMax,
                1,
                -90,
                90
            )
        }

        self._pwmMaxValues: dict = {
            "horizontal": map_value_to_new_scale(
                maxAngles[0],
                self._pwmAbsoluteMin,
                self._pwmAbsoluteMax,
                1,
                - 90,
                90
            ),
            "vertical": map_value_to_new_scale(
                maxAngles[1],
                self._pwmAbsoluteMin,
                self._pwmAbsoluteMax,
                1,
                - 90,
                90
            )
        }

        self._servoPwmNeutralValue: int = 1500  # neutral (0 degrees)

        self._currentPwmValue: dict = {
            "horizontal": 0,
            "vertical": 0
        }

        self._lookOffsetCommands: dict = {
            "look up": {
                "description": "Turns camera up",
                "plane": "vertical",
                "pwmValue": self._pwmMaxValues["vertical"]
            },
            "look down":
                {"description": "Turns camera down",
                 "plane": "vertical",
                 "pwmValue": self._pwmMinValues["vertical"]
                 },
            "look left":
                {"description": "Turns camera left",
                 "plane": "horizontal",
                 "pwmValue": self._pwmMaxValues["horizontal"]
                 },
            "look right": {
                "description": "Turns camera right",
                "plane": "horizontal",
                "pwmValue": self._pwmMinValues["horizontal"]
            }
        }

        self._lookCenterCommand: dict = {
            "look center": {
                "description": "Centers camera"
            }
        }

    def setup(self):
        for pin in list(self._servoPins.values()):
            self._pigpioPwm.set_mode(pin, pigpio.OUTPUT)
            self._pigpioPwm.set_PWM_frequency(pin, 50) # 50 hz is typical for servos

        self._center_servo_positions()

    def handle_voice_command(self, command):
        print(command)
        if command in list(self._lookOffsetCommands.keys()):
            self._move_servo(self._lookOffsetCommands[command]["plane"],
                             self._lookOffsetCommands[command]["pwmValue"]
                             )
        elif command in list(self._lookCenterCommand.keys()):
            self._center_servo_positions()

    def _center_servo_positions(self):
        for plane in list(self._servoPins.keys()):
            self._move_servo(plane, self._servoPwmNeutralValue)

    def _move_servo(self, plane, pwmValue):
        self._pigpioPwm.set_servo_pulsewidth(self._servoPins[plane], pwmValue) # move servo in given plane
        self._currentPwmValue[plane] = pwmValue # update the current pwm value for given plane

    """
    def get_servo_buttons(self):
        return self._controlsDictServo
    """

    """
        def handle_xbox_input(self, button, pressValue):
            if button == self._moveServoButton:
                self._prepare_for_servo_movement(pressValue)
                self._move_servo()
        """
    def get_servo_commands(self):
        #TODO: add this method to robocarhelper
        dictWithAllCommands = dict(chain(self._lookOffsetCommands.items(), self._lookCenterCommand.items()))
        allCommands = list(dictWithAllCommands.keys())

        return allCommands

    """
    def get_plane(self):
        return self._plane
    """
    def get_current_servo_angle(self):
        current_servo_angle = int(map_value_to_new_scale(
            self._servoPwmValue,
            self._minAngle,
            self._maxAngle,
            0,
            self._pwmMinServo,
            self._pwmMaxServo)
        )

        return current_servo_angle

    """
    def _move_servo(self):
        if self._servoValueChanged:
            ServoHandling.pigpioPwm.set_servo_pulsewidth(self._servoPin, self._servoPwmValue)
    """
    """
    def _get_servo_button_corresponding_to_axis(self, plane):
        if plane == "horizontal":
            return "RSB horizontal"
        elif plane == "vertical":
            return "RSB vertical"
    """
    """
    def _prepare_for_servo_movement(self, buttonPressValue):
        stickValue = round(buttonPressValue, 1)

        if stickValue == self._lastServoStickValue:
            self._servoValueChanged = False
        else:
            self._servoValueChanged = True
            self._servoPwmValue = map_value_to_new_scale(stickValue, self._pwmMinServo, self._pwmMaxServo, 1)
            self._lastServoStickValue = stickValue
    """
    def cleanup(self):
        for pin in list(self._servoPins.values()):
            self._pigpioPwm.set_PWM_dutycycle(pin, 0)
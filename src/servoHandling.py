from itertools import chain

from roboCarHelper import map_value_to_new_scale
import pigpio

class ServoHandling:
    def __init__(self, servoPins, minAngles, maxAngles):
        self._minAngles: dict = {
            "horizontal": minAngles[0],
            "vertical": minAngles[1]
        }

        self._maxAngles: dict = {
            "horizontal": maxAngles[0],
            "vertical": maxAngles[1]
        }

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
            "look centre": {
                "description": "Centers camera"
            }
        }

        self._exactAngleCommands: dict = self._get_exact_angle_commands()
        print(self._exactAngleCommands)

    def setup(self):
        for pin in list(self._servoPins.values()):
            self._pigpioPwm.set_mode(pin, pigpio.OUTPUT)
            self._pigpioPwm.set_PWM_frequency(pin, 50) # 50 hz is typical for servos

        self._center_servo_positions()

    def handle_voice_command(self, command):
        print(command)
        if command in self._lookOffsetCommands.keys:
            self._move_servo(self._lookOffsetCommands[command]["plane"],
                             self._lookOffsetCommands[command]["pwmValue"]
                             )
        elif command in self._lookCenterCommand:
            self._center_servo_positions()

    def get_servo_commands(self):
        #TODO: add this method to robocarhelper
        dictWithAllCommands = dict(chain(self._lookOffsetCommands.items(), self._lookCenterCommand.items()))
        allCommands = list(dictWithAllCommands.keys())

        return allCommands

    def _center_servo_positions(self):
        for plane in list(self._servoPins.keys()):
            self._move_servo(plane, self._servoPwmNeutralValue)

    def _move_servo(self, plane, pwmValue):
        self._pigpioPwm.set_servo_pulsewidth(self._servoPins[plane], pwmValue) # move servo in given plane
        self._currentPwmValue[plane] = pwmValue # update the current pwm value for given plane

    def _get_exact_angle_commands(self) -> dict:
        exactAngleCommands: dict = {}

        for angle in range(1, abs(self._minAngles["horizontal"]) + 1): # min angle is negative, so we take the absolute value
            exactAngleCommands[f"look {angle} degrees right"] = self._angle_to_pwm((-1) * angle, "horizontal")

        return exactAngleCommands

    def _angle_to_pwm(self, angle, plane) -> float:
        pwmValue = map_value_to_new_scale(
            angle,
            self._pwmMinValues[plane],
            self._pwmMaxValues[plane],
            1,
            self._minAngles[plane],
            self._maxAngles[plane]
        )

        return pwmValue

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

    def cleanup(self):
        self._center_servo_positions() # center camera when exiting
        for pin in list(self._servoPins.values()):
            self._pigpioPwm.set_PWM_dutycycle(pin, 0)
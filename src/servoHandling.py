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
        elif command in self._exactAngleCommands:
            self._move_servo(self._exactAngleCommands[command]["plane"],
                             self._exactAngleCommands[command]["pwmValue"]
                            )

    def get_servo_commands(self) -> list[str]:
        #TODO: add this method to robocarhelper
        combinedKeys: list = []
        for dict in [self._lookOffsetCommands, self._lookCenterCommand, self._exactAngleCommands]:
            combinedKeys.extend(list(dict.keys()))

        return combinedKeys

    def _center_servo_positions(self):
        for plane in list(self._servoPins.keys()):
            self._move_servo(plane, self._servoPwmNeutralValue)

    def _move_servo(self, plane, pwmValue):
        self._pigpioPwm.set_servo_pulsewidth(self._servoPins[plane], pwmValue) # move servo in given plane
        self._currentPwmValue[plane] = pwmValue # update the current pwm value for given plane

    def _get_exact_angle_commands(self) -> dict:
        exactAngleCommands: dict = {}

        # looking right commands
        for angle in range(self._minAngles["horizontal"], 0):
            exactAngleCommands[f"look {angle} degrees right"] = {
                "plane": "horizontal",
                "pwmValue": self._angle_to_pwm(angle, "horizontal")
            }

        # looking left commands
        for angle in range(1, self._maxAngles["horizontal"] + 1):
            exactAngleCommands[f"look {angle} degrees left"] = {
                "plane": "horizontal",
                "pwmValue": self._angle_to_pwm(angle, "horizontal")
            }

        # looking down commands
        for angle in range(self._minAngles["vertical"], 0):
            exactAngleCommands[f"look {angle} degrees down"] = {
                "plane": "vertical",
                "pwmValue": self._angle_to_pwm(angle, "vertical")
            }

        # looking up commands
        for angle in range(1, self._maxAngles["vertical"] + 1):
            exactAngleCommands[f"look {angle} degrees down"] = {
                "plane": "vertical",
                "pwmValue": self._angle_to_pwm(angle, "vertical")
            }

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
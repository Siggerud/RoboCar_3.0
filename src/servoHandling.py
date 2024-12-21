from roboCarHelper import RobocarHelper
import pigpio
from roboObject import RoboObject

class ServoHandling(RoboObject):
    def __init__(self, servoPins, minAngles, maxAngles, userCommands):
        self._minAngles: dict = {
            "horizontal": minAngles[0],
            "vertical": minAngles[1]
        }

        self._maxAngles: dict = {
            "horizontal": maxAngles[0],
            "vertical": maxAngles[1]
        }

        self._pigpioPwm = pigpio.pi()

        self._pwmAbsoluteMin: int = 500  # value all the way to the right or down
        self._pwmAbsoluteMax: int = 2500  # value all the way to the left or up

        self._servoPins: dict = {
            "horizontal": servoPins[0],
            "vertical": servoPins[1]
        }

        self._servoPwmNeutralValue: int = 1500  # neutral (0 degrees)

        self._currentPwmValue: dict = {
            "horizontal": 0,
            "vertical": 0
        }

        self._angleToPwmValues: dict = self._get_angle_mapped_to_pwm_values()
        self._pwmToAngleValues: dict = self._get_pwm_mapped_to_angle_values()

        basicCommands: dict = userCommands["basicCommands"]
        self._lookOffsetCommands: dict = {
            basicCommands["lookUpCommand"]: {
                "description": "Turns camera up",
                "plane": "vertical",
                "pwmValue": self._angleToPwmValues[self._maxAngles["vertical"]]
            },
            basicCommands["lookDownCommand"]:
                {"description": "Turns camera down",
                 "plane": "vertical",
                 "pwmValue": self._angleToPwmValues[self._minAngles["vertical"]]
                 },
            basicCommands["lookLeftCommand"]:
                {"description": "Turns camera left",
                 "plane": "horizontal",
                 "pwmValue": self._angleToPwmValues[self._maxAngles["horizontal"]]
                 },
            basicCommands["lookRightCommand"]: {
                "description": "Turns camera right",
                "plane": "horizontal",
                "pwmValue": self._angleToPwmValues[self._minAngles["horizontal"]]
            }
        }

        self._lookCenterCommand: dict = {
            basicCommands["lookCenterCommand"]: {
                "description": "Centers camera"
            }
        }

        variableAngleCommands: dict = userCommands["exactAngleCommands"]
        self._exactAngleCommands: dict = self._get_exact_angle_commands(variableAngleCommands)

        # mainly for printing at startup
        self._variableCommands: dict = {
            variableAngleCommands["lookRightExact"].replace("param", "angle"): {
                "description": "Turns camera specified angle to the right"
            },
            variableAngleCommands["lookLeftExact"].replace("param", "angle"): {
                "description": "Turns camera specified angle to the left"
            },
            variableAngleCommands["lookUpExact"].replace("param", "angle"): {
                "description": "Turns camera specified angle upwards"
            },
            variableAngleCommands["lookDownExact"].replace("param", "angle"): {
                "description": "Turns camera specified angle downwards"
            }
        }

    def setup(self):
        for pin in list(self._servoPins.values()):
            self._pigpioPwm.set_mode(pin, pigpio.OUTPUT)
            self._pigpioPwm.set_PWM_frequency(pin, 50) # 50 hz is typical for servos

        self._center_servo_positions()

    def handle_voice_command(self, command: str):
        if command in self._lookOffsetCommands:
            self._move_servo(self._lookOffsetCommands[command]["plane"],
                             self._lookOffsetCommands[command]["pwmValue"]
                             )
        elif command in self._lookCenterCommand:
            self._center_servo_positions()
        elif command in self._exactAngleCommands:
            self._move_servo(self._exactAngleCommands[command]["plane"],
                             self._exactAngleCommands[command]["pwmValue"]
                            )

    def print_commands(self):
        allDictsWithCommands: dict = {}
        allDictsWithCommands.update(self._lookOffsetCommands)
        allDictsWithCommands.update(self._lookCenterCommand)
        allDictsWithCommands.update(self._variableCommands)
        title: str = "Servo handling commands:"

        RobocarHelper.print_commands(title, allDictsWithCommands)

    def get_voice_commands(self) -> list[str]:
            return RobocarHelper.chain_together_dict_keys([self._lookOffsetCommands,
                                             self._lookCenterCommand,
                                             self._exactAngleCommands]
                                            )

    def get_command_validity(self, command: str) -> str:
        # check if angles stay unchanged
        if command in self._lookOffsetCommands:
            plane = self._lookOffsetCommands[command]["plane"]

            if self._currentPwmValue[plane] == self._lookOffsetCommands[command]["pwmValue"]:
                return "partially valid"

        elif command in self._exactAngleCommands:
            plane = self._exactAngleCommands[command]["plane"]

            if self._currentPwmValue[plane] == self._exactAngleCommands[command]["pwmValue"]:
                return "partially valid"

        elif command in self._lookCenterCommand:
            if self._currentPwmValue["horizontal"] == self._servoPwmNeutralValue and self._currentPwmValue["vertical"] == self._servoPwmNeutralValue:
                return "partially valid"

        return "valid"

    def _center_servo_positions(self):
        for plane in list(self._servoPins.keys()):
            self._move_servo(plane, self._servoPwmNeutralValue)

    def _move_servo(self, plane, pwmValue):
        self._pigpioPwm.set_servo_pulsewidth(self._servoPins[plane], pwmValue) # move servo in given plane
        self._currentPwmValue[plane] = pwmValue # update the current pwm value for given plane

    # map all possible angles to a dict
    def _get_angle_mapped_to_pwm_values(self) -> dict[int: float]:
        angleToPwmValues: dict = {}

        minAngle: int = min(self._minAngles.values())
        maxAngle: int = max(self._maxAngles.values())
        for angle in range(minAngle, maxAngle + 1):
            angleToPwmValues[angle] = self._angle_to_pwm(angle)

        return angleToPwmValues

    # map all possible pwm values to a dict
    def _get_pwm_mapped_to_angle_values(self) -> dict[float: int]:
        pwmToAngles: dict = {pwm: angle for angle, pwm in self._angleToPwmValues.items()}

        return pwmToAngles

    def _get_exact_angle_commands(self, userCommands: dict) -> dict:
        exactAngleCommands: dict = {}

        # looking right commands
        plane: str = "horizontal"
        angleRange: range = range(self._minAngles[plane], 0)
        command: str = userCommands["lookRightExact"]
        exactAngleCommands.update(
            self._get_angle_commands_for_given_direction(angleRange, command, plane)
        )

        # looking left commands
        plane: str = "horizontal"
        angleRange: range = range(1, self._maxAngles[plane] + 1)
        command: str = userCommands["lookLeftExact"]
        exactAngleCommands.update(
            self._get_angle_commands_for_given_direction(angleRange, command, plane)
        )

        # looking down commands
        plane: str = "vertical"
        angleRange: range = range(self._minAngles[plane], 0)
        command: str = userCommands["lookDownExact"]
        exactAngleCommands.update(
            self._get_angle_commands_for_given_direction(angleRange, command, plane)
        )

        # looking up commands
        plane: str = "vertical"
        angleRange: range = range(1, self._maxAngles[plane] + 1)
        command: str = userCommands["lookUpExact"]
        exactAngleCommands.update(
            self._get_angle_commands_for_given_direction(angleRange, command, plane)
        )

        return exactAngleCommands

    def _get_angle_commands_for_given_direction(self, range, command, plane) -> dict:
        exactAngleCommands: dict = {}

        for angle in range:
            userCommand = RobocarHelper.format_command(command, str(abs(angle))) # take the absolute value, because the user will always say a positive value
            exactAngleCommands[userCommand] = {
                "plane": plane,
                "pwmValue": self._angleToPwmValues[angle]
            }

        return exactAngleCommands

    def _angle_to_pwm(self, angle) -> float:
        pwmValue = RobocarHelper.map_value_to_new_scale(
                angle,
                self._pwmAbsoluteMin,
                self._pwmAbsoluteMax,
                1,
                - 90,
                90
            )

        return pwmValue

    def get_current_servo_angle(self, plane) -> int:
        return self._pwmToAngleValues[self._currentPwmValue[plane]]

    def cleanup(self):
        print("Cleaning up servo")
        self._center_servo_positions() # center camera when exiting
        for pin in list(self._servoPins.values()):
            self._pigpioPwm.set_PWM_dutycycle(pin, 0)
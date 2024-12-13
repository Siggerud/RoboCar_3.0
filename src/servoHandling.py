from roboCarHelper import map_value_to_new_scale, chain_together_dict_keys
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

        self._pwmAbsoluteMin: int = 500  # value all the way to the right or down
        self._pwmAbsoluteMax: int = 2500  # value all the way to the left or up

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

        self._angleToPwmValues: dict = self._get_angle_mapped_to_pwm_values()
        self._pwmToAngleValues: dict = self._get_pwm_mapped_to_angle_values()

        #TODO: make these read pwm values from angleToPwm dict instead and delete the pwmMax and min dicts
        self._lookOffsetCommands: dict = {
            "look up": {
                "description": "Turns camera up",
                "plane": "vertical",
                "pwmValue": self._angleToPwmValues[self._pwmMaxValues["vertical"]]
                #"pwmValue": self._pwmMaxValues["vertical"]
            },
            "look down":
                {"description": "Turns camera down",
                 "plane": "vertical",
                 "pwmValue": self._angleToPwmValues[self._pwmMinValues["vertical"]]
                 #"pwmValue": self._pwmMinValues["vertical"]
                 },
            "look left":
                {"description": "Turns camera left",
                 "plane": "horizontal",
                 "pwmValue": self._angleToPwmValues[self._pwmMaxValues["horizontal"]]
                 #"pwmValue": self._pwmMaxValues["horizontal"]
                 },
            "look right": {
                "description": "Turns camera right",
                "plane": "horizontal",
                "pwmValue": self._angleToPwmValues[self._pwmMinValues["horizontal"]]
                #"pwmValue": self._pwmMinValues["horizontal"]
            }
        }

        self._lookCenterCommand: dict = {
            "look centre": {
                "description": "Centers camera"
            }
        }

        self._exactAngleCommands: dict = self._get_exact_angle_commands()

    def setup(self):
        for pin in list(self._servoPins.values()):
            self._pigpioPwm.set_mode(pin, pigpio.OUTPUT)
            self._pigpioPwm.set_PWM_frequency(pin, 50) # 50 hz is typical for servos

        self._center_servo_positions()

    def handle_voice_command(self, command):
        print(command)
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

    def get_servo_commands(self) -> list[str]:
        return chain_together_dict_keys([self._lookOffsetCommands,
                                         self._lookCenterCommand,
                                         self._exactAngleCommands]
                                        )

    def _center_servo_positions(self):
        for plane in list(self._servoPins.keys()):
            self._move_servo(plane, self._servoPwmNeutralValue)

    def _move_servo(self, plane, pwmValue):
        self._pigpioPwm.set_servo_pulsewidth(self._servoPins[plane], pwmValue) # move servo in given plane
        self._currentPwmValue[plane] = pwmValue # update the current pwm value for given plane

    # map all possible angles to a dict
    def _get_angle_mapped_to_pwm_values(self) -> dict[int: float]:
        angleToPwmValues: dict = {}

        minAngle = min(self._minAngles.values())
        maxAngle = max(self._maxAngles.values())
        for angle in range(minAngle, maxAngle + 1):
            angleToPwmValues[angle] = self._angle_to_pwm(angle)

        return angleToPwmValues

    # map all possible pwm values to a dict
    def _get_pwm_mapped_to_angle_values(self) -> dict[float: int]:
        pwmToAngles: dict = {pwm: angle for angle, pwm in self._angleToPwmValues.items()}

        return pwmToAngles

    def _get_exact_angle_commands(self) -> dict:
        exactAngleCommands: dict = {}

        # looking right commands
        for angle in range(self._minAngles["horizontal"], 0):
            exactAngleCommands[f"{abs(angle)} degrees right"] = { # print the absolute value because the angle is negatie
                "plane": "horizontal",
                "pwmValue": self._angleToPwmValues[angle]
            }

        # looking left commands
        for angle in range(1, self._maxAngles["horizontal"] + 1):
            exactAngleCommands[f"{angle} degrees left"] = {
                "plane": "horizontal",
                "pwmValue": self._angleToPwmValues[angle]
            }

        # looking down commands
        for angle in range(self._minAngles["vertical"], 0):
            exactAngleCommands[f"{abs(angle)} degrees down"] = {
                "plane": "vertical",
                "pwmValue": self._angleToPwmValues[angle]
            }

        # looking up commands
        for angle in range(1, self._maxAngles["vertical"] + 1):
            exactAngleCommands[f"{angle} degrees up"] = {
                "plane": "vertical",
                "pwmValue": self._angleToPwmValues[angle]
            }

        return exactAngleCommands

    def _angle_to_pwm(self, angle) -> float:
        pwmValue = map_value_to_new_scale(
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
        self._center_servo_positions() # center camera when exiting
        for pin in list(self._servoPins.values()):
            self._pigpioPwm.set_PWM_dutycycle(pin, 0)
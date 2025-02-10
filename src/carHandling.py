import RPi.GPIO as GPIO
from roboCarHelper import RobocarHelper
from roboObject import RoboObject
from gpioValues import GpioValues

class CarHandling(RoboObject):
    def __init__(self,
                 leftBackward: int,
                 leftForward: int,
                 rightBackward: int,
                 rightForward: int,
                 enA: int,
                 enB: int,
                 pwmMinTT: int,
                 pwmMaxTT: int,
                 speedStep: int,
                 userCommands: dict):
        super().__init__(
            [leftBackward, leftForward, rightBackward, rightForward, enA, enB],
            {**userCommands["direction"], **userCommands["speed"]},
            pwmMinTT=pwmMinTT,
            pwmMaxTT=pwmMaxTT,
            speedStep=speedStep
        )

        self._leftBackward: int = leftBackward
        self._leftForward: int = leftForward
        self._rightBackward: int = rightBackward
        self._rightForward: int = rightForward
        self._enA: int = enA
        self._enB: int = enB

        self._pwmMinTT: int = pwmMinTT
        self._pwmMaxTT: int = pwmMaxTT

        self._speedStep: int = speedStep

        self._speed: int = self._pwmMinTT

        self._turnLeft: bool = False
        self._turnRight: bool = False
        self._goForward: bool = False
        self._goReverse: bool = False

        self._gpioThrottle = None

        self._pwmA = None
        self._pwmB = None

        self._direction: str = "Stopped"

        self._userCommands: dict = userCommands

        directionCommands: dict[str: str] = userCommands["direction"]
        self._direction_commands: dict[str: dict] = {
            directionCommands["turnLeftCommand"]: {"description": "Turns car left",
                                                   "gpioValues": GpioValues(False, True, True, False), "direction": "Left"},
            directionCommands["turnRightCommand"]: {"description": "Turns car right",
                                                    "gpioValues": GpioValues(True, False, False, True), "direction": "Right"},
            directionCommands["driveCommand"]: {"description": "Drives car forward",
                                                "gpioValues": GpioValues(False, False, True, True), "direction": "Forward"},
            directionCommands["reverseCommand"]: {"description": "Reverses car",
                                                  "gpioValues": GpioValues(True, True, False, False), "direction": "Reverse"},
            directionCommands["stopCommand"]: {"description": "Stops car", "gpioValues": GpioValues(False, False, False, False),
                                               "direction": "Stopped"},
        }

        speedCommands: dict[str: str] = userCommands["speed"]
        self._speed_commands: dict[str: dict] = {
            speedCommands["increaseSpeedCommand"]: {"description": "Increases car speed",
                                                    "commandDescription": "increaseSpeedCommand"},
            speedCommands["decreaseSpeedCommand"]: {"description": "Decrease car speed",
                                                    "commandDescription": "decreaseSpeedCommand"}
        }

        self._exact_speed_commands: dict = self._set_exact_speed_commands(speedCommands["exactSpeedCommand"])

        # mainly for printing at startup
        self._variableCommands: dict[str: dict] = {
            speedCommands["exactSpeedCommand"].replace("param", "speed"): {
                "description": "Sets speed to the specified speed value"
            }
        }

    def setup(self) -> None:
        GPIO.setup(self._leftBackward, GPIO.OUT)
        GPIO.setup(self._leftForward, GPIO.OUT)
        GPIO.setup(self._rightBackward, GPIO.OUT)
        GPIO.setup(self._rightForward, GPIO.OUT)
        GPIO.setup(self._enA, GPIO.OUT)
        GPIO.setup(self._enB, GPIO.OUT)

        self._pwmA = GPIO.PWM(self._enA, 100)
        self._pwmB = GPIO.PWM(self._enB, 100)

        self._pwmA.start(self._speed)
        self._pwmB.start(self._speed)

        self._gpioThrottle = {True: GPIO.HIGH, False: GPIO.LOW}

    def handle_voice_command(self, command: str) -> None:
        if command in self._direction_commands:
            newGpioValues = self._direction_commands[command]["gpioValues"]
            self._adjust_gpio_values(newGpioValues)
            self._adjust_direction_value(self._direction_commands[command]["direction"])
        elif command in self._speed_commands or command in self._exact_speed_commands:
            print("Adjusting speed...")
            self._adjust_speed(command)

    def print_commands(self) -> None:
        allDictsWithCommands: dict = {}
        allDictsWithCommands.update(self._direction_commands)
        allDictsWithCommands.update(self._speed_commands)
        allDictsWithCommands.update(self._variableCommands)
        title: str = "Car handling commands:"

        self._print_commands(title, allDictsWithCommands)

    def get_command_validity(self, command: str) -> str:
        # check if direction remains unchanged
        if command in self._direction_commands:
            if self._direction == self._direction_commands[command]["direction"]:
                return "partially valid"

        # check if speed remains unchanged
        elif command in self._exact_speed_commands:
            if self._speed == self._exact_speed_commands[command]:
                return "partially valid"

        # check if new speed increase/decrease is within valid range
        elif command in self._speed_commands:
            if command == self._userCommands["speed"]["increaseSpeedCommand"]:
                if (self._speed + self._speedStep) > self._pwmMaxTT:
                    return "partially valid"
            elif command == self._userCommands["speed"]["decreaseSpeedCommand"]:
                if (self._speed - self._speedStep) < self._pwmMinTT:
                    return "partially valid"

        return "valid"

    def cleanup(self) -> None:
        self._pwmA.stop()
        self._pwmB.stop()

    def get_voice_commands(self) -> list[str]:
        return RobocarHelper.chain_together_dict_keys([self._direction_commands,
                                                       self._speed_commands,
                                                       self._exact_speed_commands])

    @property
    def current_speed(self) -> int:
        return int(self._speed)

    @property
    def current_turn_value(self) -> str:
        return self._direction

    def _set_exact_speed_commands(self, userCommand: str) -> dict:
        speedCommands: dict = {}
        for speed in range(self._pwmMinTT, self._pwmMaxTT + 1):
            command = self._format_command(userCommand, str(speed))
            speedCommands[command] = speed

        return speedCommands

    def _adjust_direction_value(self, direction: str) -> None:
        self._direction = direction

    def _adjust_speed(self, command: str) -> None:
        adjustSpeed: bool = False

        if command == self._userCommands["speed"]["increaseSpeedCommand"]:
            self._speed += self._speedStep
            adjustSpeed = True
        elif command == self._userCommands["speed"]["decreaseSpeedCommand"]:
            self._speed -= self._speedStep
            adjustSpeed = True
        else:
            newSpeed = self._exact_speed_commands[command]
            if newSpeed != self._speed:
                adjustSpeed = True
                self._speed = newSpeed

        if adjustSpeed:
            self._change_duty_cycle()

    def _change_duty_cycle(self) -> None:
        for pwm in [self._pwmA, self._pwmB]:
            pwm.ChangeDutyCycle(self._speed)

    def _adjust_gpio_values(self, gpioValues: GpioValues) -> None:
        GPIO.output(self._leftForward, self._gpioThrottle[gpioValues.leftForward])
        GPIO.output(self._rightForward, self._gpioThrottle[gpioValues.rightForward])
        GPIO.output(self._leftBackward, self._gpioThrottle[gpioValues.leftBackward])
        GPIO.output(self._rightBackward, self._gpioThrottle[gpioValues.rightBackward])

    def _check_argument_validity(self, pins: list[int], userCommands: dict[str, str], **kwargs) -> None:
        super()._check_argument_validity(pins, userCommands, **kwargs)

        self._check_for_placeholder_in_command(userCommands["exactSpeedCommand"])

        # check that the pwm values are within valid range
        self._check_if_num_is_in_interval(kwargs["pwmMinTT"], 0, 100, "MinimumMotorPWM")
        self._check_if_num_is_in_interval(kwargs["pwmMaxTT"], 0, 100, "MaximumMotorPWM")

        # check that the speed step is within valid range
        self._check_if_num_is_in_interval(kwargs["speedStep"], 1, 100, "speed_step")

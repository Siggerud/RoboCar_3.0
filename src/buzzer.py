import RPi.GPIO as GPIO
from time import sleep
from roboCarHelper import RobocarHelper
from roboObject import RoboObject

class Buzzer(RoboObject):
    def __init__(self, buzzerPin: int, defaultHonkTime: float, maxHonkTime: float, userCommands: dict, **kwargs):
        super().__init__([buzzerPin], userCommands, defaultHonkTime=defaultHonkTime, maxHonkTime=maxHonkTime)
        
        self._buzzerPin: int = buzzerPin
        self._defaultHonkTime: float = defaultHonkTime
        self._maxHonkTime: float = maxHonkTime

        self._buzzCommand: dict = {userCommands["buzzCommand"]: {"description": "starts honking"}}
        self._buzzForSpecifiedTimeCommands: dict = self._set_honk_for_specified_time_commands(userCommands["buzzForSpecifiedTimeCommand"])

        # mainly for printing at startup
        self._variableCommands = {
            userCommands["buzzForSpecifiedTimeCommand"].replace("param", "time"): {
                "description": "Honks for the specified time"
            }
        }

    def setup(self):
        GPIO.setup(self._buzzerPin, GPIO.OUT)

    def get_command_validity(self, command) -> str:
        return "valid" # honking commands are always valid

    def handle_voice_command(self, command):
        if command in self._buzzCommand:
            honkTime = self._defaultHonkTime
        elif command in self._buzzForSpecifiedTimeCommands:
            print("Honking for a specified time")
            honkTime = self._buzzForSpecifiedTimeCommands[command]

        self._buzz(honkTime)

    def print_commands(self):
        allDictsWithCommands: dict = {}
        allDictsWithCommands.update(self._buzzCommand)
        allDictsWithCommands.update(self._variableCommands)
        title: str = "Honk commands:"

        self._print_commands(title, allDictsWithCommands)

    def get_voice_commands(self) -> list[str]:
        return RobocarHelper.chain_together_dict_keys([self._buzzCommand,
                                                       self._buzzForSpecifiedTimeCommands]
                                                      )

    def _buzz(self, honkTime):
        GPIO.output(self._buzzerPin, GPIO.HIGH)
        sleep(honkTime)
        GPIO.output(self._buzzerPin, GPIO.LOW)

    def _set_honk_for_specified_time_commands(self, userCommand: str) -> dict:
        honkTime: float = 0.1
        stepValue: float = 0.1
        honkCommands: dict = {}
        while honkTime <= (self._maxHonkTime + stepValue):
            command = self._format_command(userCommand, str(round(honkTime, 1)))
            honkCommands[command] = round(honkTime, 1) # round honkTime to avoid floating numbers with many decimals

            honkTime += stepValue

        return honkCommands

    def _check_argument_validity(self, pins, userCommands, **kwargs):
        super()._check_argument_validity(pins=pins, commands=userCommands)
        self._check_if_num_is_greater_than_or_equal_to_zero(kwargs["defaultHonkTime"], "default honk time")

        self._check_if_num_is_greater_than_or_equal_to_zero(kwargs["maxHonkTime"], "max honk time")

        self._check_for_placeholder_in_command(userCommands["buzzForSpecifiedTimeCommand"])



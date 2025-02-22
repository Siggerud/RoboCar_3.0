from time import sleep
from roboCarHelper import RobocarHelper
from roboObject import RoboObject
from buzzer import Buzzer

class BuzzerHandler(RoboObject):
    def __init__(self, buzzerPin: int, defaultHonkTime: float, maxHonkTime: float, userCommands: dict, **kwargs):
        super().__init__([buzzerPin], userCommands, defaultHonkTime=defaultHonkTime, maxHonkTime=maxHonkTime)
        
        self._buzzer: Buzzer = Buzzer(buzzerPin)
        self._defaultHonkTime: float = defaultHonkTime
        self._maxHonkTime: float = maxHonkTime

        self._buzzCommand: dict[str: dict] = {userCommands["buzzCommand"]: {"description": "Starts honking"}}
        self._buzzForSpecifiedTimeCommands: dict[str: float] = self._set_honk_for_specified_time_commands(userCommands["buzzForSpecifiedTimeCommand"])

        # mainly for printing at startup
        self._variableCommands: dict[str: dict] = {
            userCommands["buzzForSpecifiedTimeCommand"].replace("param", "time"): {
                "description": "Honks for the specified time"
            }
        }

    def setup(self) -> None:
        self._buzzer.setup()

    def get_command_validity(self, command: str) -> str:
        return "valid" # honking commands are always valid

    """
    Handles voice commands for the buzzer.

    This method processes the given voice command and triggers the buzzer to honk
    for a specified duration based on the command.

    Parameters:
    command (str): The voice command to be processed. It can be one of the predefined
                   commands to start honking or honk for a specified time.
    """
    def handle_voice_command(self, command: str) -> None:
        if command in self._buzzCommand:
            honkTime: float = self._defaultHonkTime
        elif command in self._buzzForSpecifiedTimeCommands:
            honkTime: float = self._buzzForSpecifiedTimeCommands[command]
        self._buzz(honkTime)

    def print_commands(self) -> None:
        allDictsWithCommands: dict = {**self._buzzCommand, **self._variableCommands}
        title: str = "Honk commands:"
        self._print_commands(title, allDictsWithCommands)

    def get_voice_commands(self) -> list[str]:
        return RobocarHelper.chain_together_dict_keys([self._buzzCommand,
                                                       self._buzzForSpecifiedTimeCommands]
                                                      )

    def _buzz(self, honkTime: float) -> None:
        self._buzzer.start_buzzing()
        sleep(honkTime)
        self._buzzer.stop_buzzing()

    def _set_honk_for_specified_time_commands(self, userCommand: str) -> dict[str, float]:
        honkTime: float = 0.1
        stepValue: float = 0.1
        honkCommands: dict = {}
        while honkTime <= (self._maxHonkTime + stepValue):
            command = self._format_command(userCommand, str(round(honkTime, 1)))
            honkCommands[command] = round(honkTime, 1) # round honkTime to avoid floating numbers with many decimals

            honkTime += stepValue

        return honkCommands

    def _check_argument_validity(self, pins: list[int], userCommands: dict[str, str], **kwargs) -> None:
        super()._check_argument_validity(pins, userCommands)
        self._check_if_num_is_greater_than_or_equal_to_number(kwargs["defaultHonkTime"], 0,"default honk time")

        self._check_if_num_is_greater_than_or_equal_to_number(kwargs["maxHonkTime"], 0,"max honk time")

        self._check_for_placeholder_in_command(userCommands["buzzForSpecifiedTimeCommand"])



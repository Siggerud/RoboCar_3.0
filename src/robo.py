from exceptions import InvalidPinException, OutOfRangeException, InvalidCommandException

class Robo:
    def __init__(self):
        self._boardPins: list = [3, 5, 7, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29, 31, 32, 33, 35, 36, 37, 38, 40]
        self._bcmPins: list = [2, 3, 4, 17, 18, 27, 22, 23, 24, 10, 9, 25, 11, 8, 7, 5, 6, 12, 13, 19, 16, 26, 20, 21]
        self._boardToBcmPins: dict = self._get_board_to_bcm_pins()

    def _check_if_pin_num_is_valid(self, pins: list):
        for pin in pins:
            if pin not in self._boardPins and pin not in self._bcmPins:
                raise InvalidPinException(f"Buzzerpin argument '{pin}' is not a valid pin number")

    def _check_if_num_is_greater_than_or_equal_to_zero(self, num, variableName: str):
        if num <= 0:
            raise OutOfRangeException(f"{variableName} should be greater than zero")

    def _check_command_length(self, commands: dict):
        for command in list(commands.keys()):
            if len(command.split()) < 2:
                raise InvalidCommandException(f"Command {command} is too short. Command should be minimum two words")

    def _check_for_placeholder_in_command(self, command: str):
        placeholder = "{param}"
        if placeholder not in command:
            raise InvalidCommandException(f"Command {command} is missing the {{param}} placeholder")

    def _get_board_to_bcm_pins(self) -> dict:
        boardToBcmPins: dict = {}

        for index, boardPin in enumerate(self._boardPins):
            boardToBcmPins[self._boardPins[index]] = self._bcmPins[index]

        return boardToBcmPins


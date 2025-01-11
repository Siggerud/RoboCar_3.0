from exceptions import InvalidPinException, OutOfRangeException, InvalidCommandException

class RoboObject:
    _boardPinsInUse: list = []

    def __init__(self, pins: list, commands: dict, **kwargs):
        self._boardPins: list = [3, 5, 7, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29, 31, 32, 33, 35, 36, 37, 38, 40]
        self._bcmPins: list = [2, 3, 4, 17, 18, 27, 22, 23, 24, 10, 9, 25, 11, 8, 7, 5, 6, 12, 13, 19, 16, 26, 20, 21]
        self._boardToBcmPins: dict = self._get_board_to_bcm_pins()

        self._check_argument_validity(pins, commands, **kwargs)

    def cleanup(self):
        pass

    def setup(self):
        pass

    def get_command_validity(self, command):
        pass

    def print_commands(self):
        pass

    def handle_voice_command(self, command):
        pass

    def _check_argument_validity(self, pins: list, commands: dict, **kwargs):
        self._check_if_pins_are_valid(pins)
        self._check_command_length(commands)

    def _check_if_num_is_in_interval(self, num, lowerBound, upperBound, variableName: str):
        if num < lowerBound or num > upperBound:
            raise OutOfRangeException(f"{variableName} should be between {lowerBound} and {upperBound}")

    def _check_if_pins_are_valid(self, pins: list):
        for pin in pins:
            # check that the pin number is a valid pin number
            if pin not in self._boardPins:
                raise InvalidPinException(f"Pin argument '{pin}' is not a valid pin number")

            # check that pin has not already been specified by another robo object class
            if pin in self._boardPinsInUse:
                raise InvalidPinException(f"Pin {pin} is already in use")

            self._add_pin_to_board_pins_in_use(pin)

    def _check_if_num_is_greater_than_or_equal_to_number(self, num, lowerBound, variableName: str):
        if num <= lowerBound:
            raise OutOfRangeException(f"{variableName} should be greater than zero")

    def _check_command_length(self, commands: dict):
        for command in list(commands.values()):
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

    def _print_commands(self, title, dicts):
        maxCommandLength = max(len(command) for command in dicts.keys()) + 1

        print(title)
        for command, v in dicts.items():
            print(f"{command.ljust(maxCommandLength)}: {v['description']}")
        print()

    def _format_command(self, command, param):
        return command.format(param=param)

    @classmethod
    def _add_pin_to_board_pins_in_use(cls, pin):
        cls._boardPinsInUse.append(pin)





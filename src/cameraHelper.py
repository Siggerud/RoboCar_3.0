from roboCarHelper import RobocarHelper

class CameraHelper:
    def __init__(self, userCommands, maxZoomValue):
        self._car = None
        self._servo = None

        self._angleText = ""
        self._speedText = ""
        self._turnText = ""

        self._zoomValue = 1.0

        self._minZoomValue = 1.0
        self._maxZoomValue = maxZoomValue

        self._hudActive = True

        self._directionValue_to_number = {
            "Stopped": 0,
            "Left": 1,
            "Right": 2,
            "Forward": 3,
            "Reverse": 4
        }

        self._hudCommands: dict = {
            userCommands["turnOnDisplayCommand"]: {"description": "Turns on HUD", "hudValue": True},
            userCommands["turnOffDisplayCommand"]: {"description": "Turns off HUD", "hudValue": False}
        }

        self._zoomCommands: dict = self._set_zoom_commands(userCommands["zoom"])
        print(self._zoomCommands)
        self._arrayDict = None

    def handle_voice_command(self, command):
        print(command)
        if command in self._hudCommands:
            self._set_hud_value(command)
        elif command in self._zoomCommands:
            self._set_zoom_value(command)

    def get_command_validity(self, command) -> str:
        if command in self._hudCommands: # check if display is already on or off
            if self._hudActive == self._hudCommands[command]["hudValue"]:
                return "partially valid"

        elif command in self._zoomCommands:
            if self._zoomValue == self._zoomCommands[command]: # check if zoom value is unchanged
                return "partially valid"

        return "valid"

    def add_car(self, car):
        self._car = car

    def add_servo(self, servo):
        self._servo = servo

    def update_control_values_for_video_feed(self, shared_array):
        if self._servo:
            shared_array[self._arrayDict["horizontal servo"]] = self._servo.get_current_servo_angle("horizontal")
            shared_array[self._arrayDict["vertical servo"]] = self._servo.get_current_servo_angle("vertical")

        if self._car:
            shared_array[self._arrayDict["speed"]] = self._car.get_current_speed()
            shared_array[self._arrayDict["direction"]] = self._directionValue_to_number[self._car.get_current_turn_value()]

        shared_array[self._arrayDict["HUD"]] = float(self._hudActive)
        shared_array[self._arrayDict["Zoom"]] = self._zoomValue

    def get_voice_commands(self) -> list:
        return RobocarHelper.chain_together_dict_keys([
            self._hudCommands,
            self._zoomCommands
        ])

    def get_HUD_active(self):
        return self._hudActive

    def get_zoom_value(self):
        return self._zoomValue

    def add_array_dict(self, arrayDict):
        self._arrayDict = arrayDict

    def _set_hud_value(self, command):
        self._hudActive = self._hudCommands[command]["hudValue"]

    def _set_zoom_value(self, command):
        self._zoomValue = self._zoomCommands[command]

    def _set_zoom_commands(self, command) -> dict:
        zoomValue: float = self._minZoomValue
        stepValue: float = 0.1
        zoomCommands: dict = {}
        while zoomValue <= (self._maxZoomValue + stepValue):
            userCommand = self._format_zoom_command(command, zoomValue)
            zoomCommands[userCommand] = round(zoomValue, 1) # round zoomValue to avoid floating numbers with many decimals

            zoomValue += stepValue

        return zoomCommands

    def _format_zoom_command(self, command, zoomValue):
        return command.format(zoomValue=str(round(zoomValue, 1)))


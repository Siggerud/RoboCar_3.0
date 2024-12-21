from roboCarHelper import RobocarHelper
from roboObject import RoboObject

class CameraHelper(RoboObject):
    def __init__(self, userCommands: dict, maxZoomValue: float, car=None, servo=None):
        self._car = car
        self._servo = servo
        print(car)
        print(servo)
        self._angleText: str = ""
        self._speedText: str = ""
        self._turnText: str = ""

        self._zoomValue: float = 1.0

        self._minZoomValue: float = 1.0
        self._maxZoomValue: float = maxZoomValue

        self._hudActive: bool = True

        self._directionValue_to_number: dict = {
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

        self._zoomCommands: dict = self._set_zoom_commands(userCommands["zoomCommand"])

        self._arrayDict: dict = self._set_array_dict()

        # mainly for printing at startup
        self._variableCommands: dict = {
            userCommands["zoomCommand"].replace("param", "zoom"): {
                "description": "Zooms camera to the specified zoom value"
            }
        }

    def setup(self):
        pass

    def handle_voice_command(self, command):
        print(command)
        if command in self._hudCommands:
            self._set_hud_value(command)
        elif command in self._zoomCommands:
            self._set_zoom_value(command)

    def print_commands(self):
        allDictsWithCommands: dict = {}
        allDictsWithCommands.update(self._hudCommands)
        allDictsWithCommands.update(self._variableCommands)
        title: str = "Camera commands:"

        RobocarHelper.print_commands(title, allDictsWithCommands)

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

    def get_array_dict(self) -> dict:
        return self._arrayDict

    def cleanup(self):
        pass

    def _set_array_dict(self) -> dict:
        arrayDict: dict = {}
        #cameraInputs: list = ["speed", "direction", "horizontal servo", "vertical servo", "HUD", "Zoom"]
        cameraInputs: list = []
        if self._car:
            cameraInputs.extend(["speed", "direction"])
        if self._servo:
            cameraInputs.extend(["horizontal servo", "vertical servo"])
        cameraInputs.extend(["HUD", "Zoom"])
        for index, cameraInput in enumerate(cameraInputs):
            arrayDict[cameraInput] = index

        return arrayDict

    def _set_hud_value(self, command):
        self._hudActive = self._hudCommands[command]["hudValue"]

    def _set_zoom_value(self, command):
        self._zoomValue = self._zoomCommands[command]

    def _set_zoom_commands(self, userCommand: str) -> dict:
        zoomValue: float = self._minZoomValue
        stepValue: float = 0.1
        zoomCommands: dict = {}
        while zoomValue <= (self._maxZoomValue + stepValue):
            command: str = RobocarHelper.format_command(userCommand, str(round(zoomValue, 1)))
            zoomCommands[command] = round(zoomValue, 1) # round zoomValue to avoid floating numbers with many decimals

            zoomValue += stepValue

        return zoomCommands


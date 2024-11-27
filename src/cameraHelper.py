from roboCarHelper import map_value_to_new_scale

class CameraHelper:
    def __init__(self):
        self._car = None
        self._servo = None

        self._angleText = ""
        self._speedText = ""
        self._turnText = ""

        self._zoomValue = 1.0
        self._lastStickValue = 0

        self._minZoomValue = 1.0
        self._maxZoomValue = 3.0

        self._zoomButtonMinValue = 0
        self._zoomButtonMaxValue = -1

        self._hudActive = True

        self._controlsDictCamera = {
            "Zoom": "LSB vertical",
            "HUD": "RB"
        }

        self._zoomButton = self._controlsDictCamera["Zoom"]
        self._hudButton = self._controlsDictCamera["HUD"]

        self._turnValue_to_number = {
            "-": 0,
            "Left": 1,
            "Right": 2
        }

        self._arrayDict = None

    def handle_xbox_input(self, button, pressValue):
        if button == self._zoomButton:
            self._set_zoom_value(pressValue)
        elif button == self._hudButton and pressValue: # check that button is pushed, not released
            self._set_hud_on_or_off()

    def add_car(self, car):
        self._car = car

    def add_servo(self, servo):
        self._servo = servo

    def update_control_values_for_video_feed(self, shared_array):
        if self._servo:
            shared_array[self._arrayDict["servo"]] = self._servo.get_current_servo_angle()

        if self._car:
            shared_array[self._arrayDict["speed"]] = self._car.get_current_speed()
            shared_array[self._arrayDict["turn"]] = self._turnValue_to_number[self._car.get_current_turn_value()]

        shared_array[self._arrayDict["HUD"]] = float(self._hudActive)
        shared_array[self._arrayDict["Zoom"]] = self._zoomValue

    def get_camera_buttons(self):
        return self._controlsDictCamera

    def get_HUD_active(self):
        return self._hudActive

    def get_zoom_value(self):
        return self._zoomValue

    def add_array_dict(self, arrayDict):
        self._arrayDict = arrayDict

    def _set_hud_on_or_off(self):
        self._hudActive = not self._hudActive

    def _set_zoom_value(self, buttonPressValue):
        if self._check_if_button_press_within_valid_range(buttonPressValue):
            stickValue = round(buttonPressValue, 1)
        else:
            stickValue = self._zoomButtonMinValue

        if stickValue != self._lastStickValue:
            self._lastStickValue = stickValue
            self._zoomValue = map_value_to_new_scale(stickValue,
                                                     self._minZoomValue,
                                                     self._maxZoomValue,
                                                     2,
                                                     self._zoomButtonMinValue,
                                                     self._zoomButtonMaxValue
                                                     )
    def _check_if_button_press_within_valid_range(self, buttonPressValue):
        if buttonPressValue >= self._zoomButtonMaxValue and buttonPressValue <= self._zoomButtonMinValue:
            return True
        return False
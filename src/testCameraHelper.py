import unittest
from unittest.mock import patch, MagicMock, Mock
from cameraHelper import CameraHelper
from multiprocessing import Array

# mock the import of pigpio and GPIO
MockPigpio = MagicMock()
MockRPi = MagicMock()
modules = {
    "pigpio": MockRPi,
    "RPi": MockRPi,
    "RPi.GPIO": MockRPi.GPIO
}
patcher = patch.dict("sys.modules", modules)
patcher.start()

from servoHandling import ServoHandling
from carHandling import CarHandling

class TestCameraHelper(unittest.TestCase):
    @patch("RPi.GPIO.setup")
    @patch("RPi.GPIO.PWM")
    def get_car(self, mock_pwm, mock_setup):
        return CarHandling(
            1,
            2,
            3,
            4,
            5,
            6,
            20,
            50
        )

    @patch("servoHandling.ServoHandling.pigpioPwm")
    def get_servo(self, mock_pi):
        return ServoHandling(1, "horizontal")

    def test_handle_xbox_input_changes_when_large_press_value_changed(self):
        button = "LSB vertical"
        pressValue1 = -0.57
        pressValue2 = -0.67

        helper = CameraHelper()
        helper.handle_xbox_input(button, pressValue1)
        zoomValueAfterFirstCall = helper.get_zoom_value()

        helper.handle_xbox_input(button, pressValue2)

        self.assertNotEqual(zoomValueAfterFirstCall, helper.get_zoom_value())

    def test_handle_xbox_input_changes_nothing_when_small_press_value_change(self):
        button = "LSB vertical"
        pressValue1 = -0.57
        pressValue2 = -0.64

        helper = CameraHelper()
        helper.handle_xbox_input(button, pressValue1)
        zoomValueAfterFirstCall = helper.get_zoom_value()
        helper.handle_xbox_input(button, pressValue2)

        # both these zoom values should round to the same number, and therefore not change the zoom value
        self.assertEqual(zoomValueAfterFirstCall, helper.get_zoom_value())

    def test_handle_xbox_input_change_nothing_when_out_of_range(self):
        button = "LSB vertical"
        pressValue = 0.1 # out of valid range for zooming

        helper = CameraHelper()
        zoomValueBeforeCall = helper.get_zoom_value()
        helper.handle_xbox_input(button, pressValue)

        self.assertEqual(zoomValueBeforeCall, helper.get_zoom_value())

    def test_handle_xbox_input_changes_nothing_when_hud_active_button_is_zero(self):
        button = "RB"
        pressValue = 0

        helper = CameraHelper()
        HUDvalueBeforeCall = helper.get_HUD_active()
        helper.handle_xbox_input(button, pressValue)

        self.assertEqual(HUDvalueBeforeCall, helper.get_HUD_active())

    def test_handle_xbox_input_changes_hud_active(self):
        button = "RB"
        pressValue = 1

        helper = CameraHelper()
        HUDvalueBeforeCall = helper.get_HUD_active()
        helper.handle_xbox_input(button, pressValue)

        # assert that the value for HUD has changed
        self.assertNotEqual(HUDvalueBeforeCall, helper.get_HUD_active())

    def test_handle_xbox_input_changes_zoom_value(self):
        button = "LSB vertical"
        pressValue = -0.5

        helper = CameraHelper()
        helper.handle_xbox_input(button, pressValue)

        self.assertEquals(2.0, helper.get_zoom_value())

    @patch.object(CarHandling, "get_current_turn_value", autospec=True)
    @patch.object(CarHandling, "get_current_speed", autospec=True)
    @patch.object(ServoHandling, "get_current_servo_angle", autospec=True)
    def test_update_control_values_for_video_feed(self, mock_angle, mock_speed, mock_turn):
        mock_angle.return_value = 3.0
        mock_speed.return_value = 40.0
        mock_turn.return_value = "Right"

        servo = self.get_servo()
        car = self.get_car()

        array = Array('d', (1.0, 2.0, 3.0, 4.0, 5.0))
        arrayDict = {"servo": 0, "HUD": 1, "Zoom": 2, "speed": 3, "turn": 4}

        helper = CameraHelper()
        helper.add_array_dict(arrayDict)
        helper.add_servo(servo)
        helper.add_car(car)
        helper.update_control_values_for_video_feed(array)

        # check that the method updates the array with expected values for servo and car
        self.assertEqual(3, array[0])
        self.assertEqual(40.0, array[3])
        self.assertEqual(2, array[4])

    def test_get_camera_buttons(self):
        helper = CameraHelper()

        result = helper.get_camera_buttons()["Zoom"]

        self.assertEqual("LSB vertical", result)

        result = helper.get_camera_buttons()["HUD"]

        self.assertEqual("RB", result)
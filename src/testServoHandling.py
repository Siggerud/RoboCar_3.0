import unittest
from unittest.mock import patch, MagicMock, Mock

# mock the import of pigpio
MockPigpio = MagicMock()
modules = {
    "pigpio": MockPigpio,
}
patcher = patch.dict("sys.modules", modules)
patcher.start()

import pigpio
from servoHandling import ServoHandling

@patch("servoHandling.ServoHandling.pigpioPwm")
class TestServoHandling(unittest.TestCase):
    # define GPIO pins
    servoPin = 26

    def test_setup(self, mock_pi):
        # initialize servo
        servo = ServoHandling(self.servoPin, "horizontal")
        servo.setup()

        # assert that methods have been called on mock object
        mock_pi.set_mode.assert_called_once_with(self.servoPin, pigpio.OUTPUT)
        mock_pi.set_PWM_frequency.assert_called_once_with(self.servoPin, 50)

    def test_handle_xbox_input_calls_pulsewidth(self, mock_pi):
        servo = ServoHandling(self.servoPin, "vertical")

        servo.handle_xbox_input("RSB vertical", 1)

        mock_pi.set_servo_pulsewidth.assert_called_once_with(self.servoPin, 500)

    def test_handle_xbox_does_not_call_pulsewidth_with_no_change(self, mock_pi):
        servo = ServoHandling(self.servoPin, "vertical")

        servo.handle_xbox_input("RSB vertical", 1)
        servo.handle_xbox_input("RSB vertical", 1)

        # assert method has only been called once
        mock_pi.set_servo_pulsewidth.assert_called_once()

    def test_cleanup(self, mock_pi):
        servo = ServoHandling(self.servoPin, "vertical")

        servo.cleanup()

        # assert that dutycycle is set to 0
        mock_pi.set_PWM_dutycycle.assert_called_once_with(self.servoPin, 0)

    def test_handle_xbox_input_does_not_call_when_wrong_button(self, mock_pi):
        # set servo to be vertical plane
        servo = ServoHandling(self.servoPin, "vertical")

        # call method with button for horizontal plane
        servo.handle_xbox_input("RSB horizontal", 1)

        mock_pi.set_servo_pulsewidth.assert_not_called()

    def test_get_servo_buttons(self, mock_pi):
        servo = ServoHandling(self.servoPin, "vertical")

        result = servo.get_servo_buttons()["Servo"]

        self.assertEquals("RSB vertical", result)

    def test_get_current_servo_angle(self, mock_pi):
        # initialize servo
        servo = ServoHandling(self.servoPin, "horizontal")

        mockServoValue = Mock()
        servo._servoPwmValue = mockServoValue

        with patch.object(servo, "_servoPwmValue", 1500):
            result = servo.get_current_servo_angle()

            self.assertEqual(0, result)

        with patch.object(servo, "_servoPwmValue", 1000):
            result = servo.get_current_servo_angle()

            self.assertEqual(45, result)

        with patch.object(servo, "_servoPwmValue", 2500):
            result = servo.get_current_servo_angle()

            self.assertEqual(-90, result)

        with patch.object(servo, "_servoPwmValue", 500):
            result = servo.get_current_servo_angle()

            self.assertEqual(90, result)


if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import patch, call, Mock, MagicMock

# mock the import of RPi.GPIO
MockRPi = MagicMock()
modules = {
    "RPi": MockRPi,
    "RPi.GPIO": MockRPi.GPIO
}
patcher = patch.dict("sys.modules", modules)
patcher.start()

from carHandling import CarHandling
import RPi.GPIO as GPIO

class TestCarHandling(unittest.TestCase):
    # define GPIO pins
    rightForward = 1
    rightBackward = 2
    leftForward = 3
    leftBackward = 4
    enA = 5
    enB = 6

    minPwm = 10
    maxPwm = 40

    def get_car(self):
        return CarHandling(
            self.leftBackward,
            self.leftForward,
            self.rightBackward,
            self.rightForward,
            self.enA,
            self.enB,
            self.minPwm,
            self.maxPwm
        )

    @patch("RPi.GPIO.PWM")
    @patch("RPi.GPIO.setup")
    @patch("RPi.GPIO.setmode")
    def test_setup(self, mock_setmode, mock_setup, mock_pwm):
        car = self.get_car()
        car.setup()

        carPins = [
            self.leftBackward,
            self.leftForward,
            self.rightBackward,
            self.rightForward,
            self.enA,
            self.enB
        ]

        calls = [
            call(pin, GPIO.OUT) for pin in carPins
        ]

        # check that GPIO.setup is called correctly for all pins
        mock_setup.assert_has_calls(calls, any_order=False)

        calls = [
            call(pin, 100) for pin in carPins[4:]
        ]

        #check that pwm is called with correct pins and frequency
        mock_pwm.assert_has_calls(calls, any_order=False)

    def test_get_car_buttons(self):
        car = self.get_car()

        result = car.get_car_buttons()["Right"]
        self.assertEqual("D-PAD right", result)

        result = car.get_car_buttons()["Reverse"]
        self.assertEqual("LT", result)

    @patch("RPi.GPIO.cleanup")
    def test_cleanup(self, mock_cleanup):
        car = self.get_car()

        pwmA = Mock()
        pwmB = Mock()

        # set the car PWM objects to be mocks, so we can track calls
        car._pwmA = pwmA
        car._pwmB = pwmB

        car.cleanup()

        # check that the stop method is run on the PWM objects
        pwmA.stop.assert_called_once()
        pwmB.stop.assert_called_once()

        # check that GPIO cleanup is run
        mock_cleanup.assert_called_once()

    @patch("RPi.GPIO.setmode")
    @patch("RPi.GPIO.PWM")
    @patch("RPi.GPIO.setup")
    @patch("RPi.GPIO.output")
    def test_handle_xbox_input_turns_car(self, mock_output, mock_setup, mock_pwm, mock_setmode):
        button = "D-PAD left"
        pressValue = 1

        pwmA = Mock()
        pwmB = Mock()

        car = self.get_car()
        car.setup()

        car._pwmA = pwmA
        car._pwmB = pwmB

        car.handle_xbox_input(button, pressValue)

        # assert that ChangeDutyCycle is called on both PWMs with max speed
        pwmA.ChangeDutyCycle.assert_called_once_with(self.maxPwm)
        pwmB.ChangeDutyCycle.assert_called_once_with(self.maxPwm)

        calls = [
            call(self.leftForward, GPIO.LOW),
            call(self.rightForward, GPIO.HIGH),
            call(self.leftBackward, GPIO.HIGH),
            call(self.rightBackward, GPIO.LOW)
        ]

        # assert HIGH and LOW calls to pins
        mock_output.assert_has_calls(calls, any_order=True)

    @patch("RPi.GPIO.setmode")
    @patch("RPi.GPIO.PWM")
    @patch("RPi.GPIO.setup")
    @patch("RPi.GPIO.output")
    def test_handle_xbox_input_stops_turning_car(self, mock_output, mock_setup, mock_pwm, mock_setmode):
        button = "D-PAD right"
        pressValue = 0

        car = self.get_car()
        car.setup()

        car.handle_xbox_input(button, pressValue)

        calls = [
            call(self.leftForward, GPIO.LOW),
            call(self.rightForward, GPIO.LOW),
            call(self.leftBackward, GPIO.LOW),
            call(self.rightBackward, GPIO.LOW)
        ]

        # assert HIGH and LOW calls to pins
        mock_output.assert_has_calls(calls, any_order=True)

    @patch("RPi.GPIO.setmode")
    @patch("RPi.GPIO.PWM")
    @patch("RPi.GPIO.setup")
    @patch("RPi.GPIO.output")
    def test_handle_xbox_input_turns_right_while_reversing(self, mock_output, mock_setup, mock_pwm, mock_setmode):
        button = "D-PAD right"
        pressValue = 1

        pwmA = Mock()
        pwmB = Mock()

        car = self.get_car()
        car.setup()

        # set goReverse to be true to simulate the car being in reverse mode
        car._goReverse = True

        car._pwmA = pwmA
        car._pwmB = pwmB

        car.handle_xbox_input(button, pressValue)

        # assert that ChangeDutyCycle is not called since the car should not do this for turns while in motion
        pwmA.ChangeDutyCycle.assert_not_called()
        pwmB.ChangeDutyCycle.assert_not_called()

        calls = [
            call(self.leftForward, GPIO.LOW),
            call(self.rightForward, GPIO.LOW),
            call(self.leftBackward, GPIO.HIGH),
            call(self.rightBackward, GPIO.LOW)
        ]

        # assert HIGH and LOW calls to pins
        mock_output.assert_has_calls(calls, any_order=True)

    @patch("RPi.GPIO.setmode")
    @patch("RPi.GPIO.PWM")
    @patch("RPi.GPIO.setup")
    @patch("RPi.GPIO.output")
    def test_handle_xbox_input_sets_correct_pwm_to_press_value(self, mock_output, mock_setup, mock_pwm, mock_setmode):
        button = "RT"
        pressValue = 0 # 50 % of max throttle

        car = self.get_car()
        car.setup()

        pwmA = Mock()
        pwmB = Mock()

        car._pwmA = pwmA
        car._pwmB = pwmB

        car.handle_xbox_input(button, pressValue)

        # assert that ChangeDutyCycle is called on both PWMs with value right between min and max value
        halfPowerPwm = round((self.maxPwm + self.minPwm) / 2, 2)

        pwmA.ChangeDutyCycle.assert_called_once_with(halfPowerPwm)
        pwmB.ChangeDutyCycle.assert_called_once_with(halfPowerPwm)

        calls = [
            call(self.leftForward, GPIO.HIGH),
            call(self.rightForward, GPIO.HIGH),
            call(self.leftBackward, GPIO.LOW),
            call(self.rightBackward, GPIO.LOW)
        ]

        # assert forward pins are called
        mock_output.assert_has_calls(calls, any_order=True)


if __name__ == '__main__':
    unittest.main()
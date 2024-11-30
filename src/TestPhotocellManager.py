import unittest
from unittest.mock import patch, MagicMock, call, Mock

# mock the import of RPi.GPIO
MockRPi = MagicMock()
modules = {
    "RPi": MockRPi,
    "RPi.GPIO": MockRPi.GPIO
}
patcher = patch.dict("sys.modules", modules)
patcher.start()

from PhotocellManager import PhotocellManager
import RPi.GPIO as GPIO

@patch("RPi.GPIO.setup")
@patch("RPi.GPIO.PWM")
class TestPhotocellManager(unittest.TestCase):
    lightPins = [31, 36]

    def get_photocell_manager(self):
        return PhotocellManager(self.lightPins)

    def test_setup(self, mock_pwm, mock_setup):
        pcManager = self.get_photocell_manager()
        pcManager.setup()

        mock_setup.assert_has_calls(
            [
                call(pin, GPIO.OUT) for pin in self.lightPins
            ],
            any_order=False
        )

        mock_pwm.assert_has_calls(
            [
                call(self.lightPins[0], 100),
                call().start(0),
                call(self.lightPins[1], 100),
                call().start(0)
            ],
            any_order=False
        )

    def test_adjust_lights_only_change_pwm_when_sensors_change(self, mock_pwm, mock_setup):
        pcManager = self.get_photocell_manager()
        pcManager.setup()

        mockPwm1 = Mock()
        mockPwm2 = Mock()

        pcManager._pwms[0] = mockPwm1
        pcManager._pwms[1] = mockPwm2

        # call the same function twice with the same value
        pcManager.adjust_lights(400)
        pcManager.adjust_lights(400)

        # changing of duty cycle should only occur once, since value only changed the first time
        mockPwm1.ChangeDutyCycle.assert_called_once()
        mockPwm2.ChangeDutyCycle.assert_called_once()

    def test_adjust_lights_changes_pwm_to_correct_values(self, mock_pwm, mock_setup):
        pcManager = self.get_photocell_manager()
        pcManager.setup()

        mockPwm1 = Mock()
        mockPwm2 = Mock()

        pcManager._pwms[0] = mockPwm1
        pcManager._pwms[1] = mockPwm2

        pcManager.adjust_lights(0)

        # a minimum sensor reading should give the highest value for light pwm
        mockPwm1.ChangeDutyCycle.assert_called_once_with(99)
        mockPwm2.ChangeDutyCycle.assert_called_once_with(99)

        pcManager.adjust_lights(1023)

        # a maximum sensor reading should give the lowest value for light pwm
        mockPwm1.ChangeDutyCycle.assert_called_with(0)
        mockPwm2.ChangeDutyCycle.assert_called_with(0)

    def test_cleanup(self, mock_pwm, mock_setup):
        pcManager = self.get_photocell_manager()
        pcManager.setup()

        mockPwm1 = Mock()
        mockPwm2 = Mock()

        pcManager._pwms[0] = mockPwm1
        pcManager._pwms[1] = mockPwm2

        pcManager.cleanup()

        mockPwm1.stop.assert_called_once()
        mockPwm2.stop.assert_called_once()


if __name__ == '__main__':
    unittest.main()
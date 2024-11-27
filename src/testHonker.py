import unittest
from unittest.mock import patch, MagicMock

# mock the import of RPi.GPIO
MockRPi = MagicMock()
modules = {
    "RPi": MockRPi,
    "RPi.GPIO": MockRPi.GPIO
}
patcher = patch.dict("sys.modules", modules)
patcher.start()

from honker import Honker
import RPi.GPIO as GPIO

@patch("RPi.GPIO.setup")
class TestHonker(unittest.TestCase):
    buzzerPin = 1

    def test_setup(self, mock_gpioSetup):
        honker = Honker(self.buzzerPin)
        honker.setup()

        # assert that the GPIO.setup method is called with expected parameters
        mock_gpioSetup.assert_called_once_with(self.buzzerPin, GPIO.OUT, initial=False)

    @patch("RPi.GPIO.output")
    def test_honker_does_not_honk_when_outside_treshold(self, mock_gpioOutput, mock_gpioSetup):
        honker = Honker(self.buzzerPin)

        honker.setup()

        # set treshold to be 15 cm
        honker.set_distance_treshold(15)

        distances = [16, 21, None]
        honker.prepare_for_honking(distances)
        honker.alert_if_too_close()

        # assert that the buzzer is not turned on
        mock_gpioOutput.assert_called_once_with(self.buzzerPin, False)

    @patch("RPi.GPIO.output")
    def test_honker_does_honk_when_inside_treshold(self, mock_gpioOutput, mock_gpioSetup):
        honker = Honker(self.buzzerPin)

        honker.setup()

        # set treshold to be 15 cm
        honker.set_distance_treshold(15)

        distances = [None, 21, 14]
        honker.prepare_for_honking(distances)
        honker.alert_if_too_close()

        # assert that the buzzer is not turned on
        mock_gpioOutput.assert_called_once_with(self.buzzerPin, True)

    @patch("RPi.GPIO.output")
    @patch("honker.time")
    def test_honker_beeps_again_after_given_time(self, mock_time, mock_gpioOutput, mock_gpioSetup):
        # mock the outputs of the time function
        mock_time.side_effect = [1, 2, 3]

        honker = Honker(self.buzzerPin)

        honker.setup()

        # set treshold to be 15 cm
        honker.set_distance_treshold(15)

        distances = [None, 21, 14]
        honker.prepare_for_honking(distances)

        # run the prepare_for_honking function twice to check if it turns off buzzer after a while
        honker.alert_if_too_close()
        honker.alert_if_too_close()

        # assert that buzzer will turn off after a given time
        mock_gpioOutput.assert_called_with(self.buzzerPin, False)

    @patch("RPi.GPIO.output")
    @patch("honker.time")
    def test_honker_beep_timing_does_beep_too_early(self, mock_time, mock_gpioOutput, mock_gpioSetup):
        # mock the outputs of the time function
        mock_time.side_effect = [1, 2.49]

        honker = Honker(self.buzzerPin)
        honker.setup()

        # set treshold to be 100 cm
        honker.set_distance_treshold(100)

        # set waiting times between honks
        honker.set_long_beep_time(2)
        honker.set_short_beep_time(1)

        distances = [50, None, 65]
        honker.prepare_for_honking(distances)

        honker.prepare_for_honking(distances)
        honker.alert_if_too_close()
        honker.alert_if_too_close()

        # the call on alert_if_too_close() should not turn off honk before 1.5 seconds have passed
        # in this case only 1.49 seconds have passed
        mock_gpioOutput.assert_called_with(self.buzzerPin, True)

    @patch("RPi.GPIO.output")
    @patch("honker.time")
    def test_honker_beep_timing_does_beep_too_early(self, mock_time, mock_gpioOutput, mock_gpioSetup):
        # mock the outputs of the time function
        mock_time.side_effect = [1, 2.51, 3]

        honker = Honker(self.buzzerPin)
        honker.setup()

        # set treshold to be 100 cm
        honker.set_distance_treshold(100)

        # set waiting times between honks
        honker.set_long_beep_time(2)
        honker.set_short_beep_time(1)

        distances = [50, None, 65]
        honker.prepare_for_honking(distances)

        honker.prepare_for_honking(distances)
        honker.alert_if_too_close()
        honker.alert_if_too_close()

        # the call on alert_if_too_close() should turn off honk when 1.5 seconds have passed
        # in this case 1.51 seconds have passed
        mock_gpioOutput.assert_called_with(self.buzzerPin, False)

    @patch("RPi.GPIO.output")
    @patch("honker.time")
    def test_honker_turns_off_beep_when_above_treshold(self, mock_time, mock_gpioOutput, mock_gpioSetup):
        # mock the outputs of the time function
        mock_time.side_effect = [1, 2, 3]

        honker = Honker(self.buzzerPin)
        honker.setup()

        # set treshold to be 100 cm
        honker.set_distance_treshold(100)

        # set waiting times between honks. We'll set a high beep interval here
        # so we'll know the changing of the beep will be interrupted by being above the treshold
        # and not too much time having passed
        honker.set_long_beep_time(1000)
        honker.set_short_beep_time(1)

        # give input of distances below the treshold
        lowDistances = [50, None, 65]
        honker.prepare_for_honking(lowDistances)

        honker.alert_if_too_close()

        # check that honk is turned on at first
        mock_gpioOutput.assert_called_once_with(self.buzzerPin, True)

        # give input of distances above the treshold
        highDistances = [250, None, None]
        honker.prepare_for_honking(highDistances)

        honker.alert_if_too_close()

        # check that honk is turned off now that it's outside the treshold
        mock_gpioOutput.assert_called_with(self.buzzerPin, False)

if __name__ == '__main__':
    unittest.main()

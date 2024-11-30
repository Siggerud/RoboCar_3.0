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

from Honker import Honker
import RPi.GPIO as GPIO

@patch("RPi.GPIO.setup")
class TestHonker(unittest.TestCase):
    buzzerPin = 1

    def get_honker_object(self):
        return Honker(self.buzzerPin)

    def test_init_calls(self, mock_setup):
        honker = self.get_honker_object()

        mock_setup.assert_called_with(self.buzzerPin, GPIO.OUT, initial=False)

    @patch("RPi.GPIO.output")
    def test_alert_if_too_close(self, mock_output, mock_setup):
        honker = self.get_honker_object()
        honker._withinAlarmDistance = False

        # call method
        honker.alert_if_too_close()

        mock_output.assert_called_with(self.buzzerPin, False)

        # change variables for different result
        honker._withinAlarmDistance = True
        honker._honkCurrentlyOn = True

        # call method
        honker.alert_if_too_close()

        mock_output.assert_called_with(self.buzzerPin, True)

        # change variable for different result
        honker._honkCurrentlyOn = False

        # call method
        honker.alert_if_too_close()

        mock_output.assert_called_with(self.buzzerPin, False)

    @patch.object(Honker, "_check_if_any_response_is_below_threshold", autospec=True)
    def test_set_honk_on_or_off(self, mock_checking, mock_setup):
        honker = self.get_honker_object()

        mock_checking.return_value = True

        # call method
        honker._set_honk_on_or_off([])

        assert(honker._withinAlarmDistance)
        mock_checking.assert_called_once()

        mock_checking.return_value = False

        honker._set_honk_on_or_off([])

        assert(not honker._withinAlarmDistance)
        mock_checking.assert_called()

    @patch("Honker.map_value_to_new_scale", autospec=True)
    @patch("Honker.time", autospec=True)
    def test_set_honk_timing(self, mock_time, mock_mapping, mock_setup):
        honker = self.get_honker_object()
        honker._withinAlarmDistance = False

        # call method
        honker._set_honk_timing()

        # assert that the mapping method is not called
        mock_mapping.assert_not_called()

        # set withinAlarmDistance to true to run more of the method
        honker._withinAlarmDistance = True
        honker._honkCurrentlyOn = True

        mock_time.return_value = 15
        mock_mapping.return_value = 10
        honker._lastHonkChangeTime = 7

        # call method
        honker._set_honk_timing()

        assert(honker._honkCurrentlyOn)
        assert(honker._lastHonkChangeTime == 7)

        # simulate more time having passed
        mock_time.return_value = 20

        # call method
        honker._set_honk_timing()

        assert(not honker._honkCurrentlyOn)
        assert(honker._lastHonkChangeTime == 20)

    def test_check_if_any_response_is_below_treshold(self, mock_setup):
        honker = self.get_honker_object()

        # check that it returns true when one value is below treshold
        sensorValues = [19, 302, None, 9.9, 18]
        result = honker._check_if_any_response_is_below_threshold(sensorValues)

        assert result

        # check that it returns false when noe values are below treshold
        sensorValues = [10.1, 10, None, 22]
        result = honker._check_if_any_response_is_below_threshold(sensorValues)

        assert(not result)

if __name__ == '__main__':
    unittest.main()

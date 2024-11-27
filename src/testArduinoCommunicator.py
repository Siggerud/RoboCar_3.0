import unittest
from unittest.mock import patch, MagicMock, Mock, call

# mock the import of RPi.GPIO
MockRPi = MagicMock()
modules = {
    "RPi": MockRPi,
    "RPi.GPIO": MockRPi.GPIO
}
patcher = patch.dict("sys.modules", modules)
patcher.start()

from arduinoCommunicator import ArduinoCommunicator, InvalidPortError
import RPi.GPIO as GPIO

@patch("RPi.GPIO.setmode")
@patch("arduinoCommunicator.Serial")
@patch("arduinoCommunicator.sleep")
class testArduinoCommunicator(unittest.TestCase):
    port = "/dev/ttyACM"
    baudrate = 200

    @patch("RPi.GPIO.cleanup")
    @patch("os.path.exists")
    def test_cleanup(self, mock_path, mock_cleanup, mock_sleep, mock_serial, mock_setmode):
        # mock the return value of Serial object to see what methods are called on it
        mockSerialInstance = mock_serial.return_value

        # set the check of the port to return true
        mock_path.return_value = True

        communicator = ArduinoCommunicator(self.port, self.baudrate)
        communicator.cleanup()

        mockSerialInstance.close.assert_called_once()
        mock_cleanup.assert_called_once()

    def test_port_checking(self, mock_sleep, mock_serial, mock_setmode):
        # a port/path that definitely is not a real port on the users computer
        fakePort = "this is not a port"

        with self.assertRaises(InvalidPortError):
            communicator = ArduinoCommunicator(fakePort, self.baudrate)

    @patch("arduinoCommunicator.Honker")
    @patch("os.path.exists")
    def test_input_to_honker_class(self, mock_path, mock_honker, mock_sleep, mock_serial, mock_setmode):
        # mock the return value of Serial object to mock the method calls on it
        mockSerialInstance = mock_serial.return_value

        # set the in_waiting attribute 1 to avoid an infinite loop
        mockSerialInstance.in_waiting = 1

        mockHonkerInstance = mock_honker.return_value

        # mock the reading of the arduino input
        mock_readline = Mock()
        mock_readline.decode.return_value = "5"
        mockSerialInstance.readline.return_value = mock_readline

        # set the check of the port to return true
        mock_path.return_value = True

        communicator = ArduinoCommunicator(self.port, self.baudrate)

        # activate the rear sensors
        communicator.activate_distance_sensors(1, False, True)
        communicator.setup()

        # simulate the reading from arduino
        communicator.start()

        mockHonkerInstance.prepare_for_honking.assert_called_once_with([None, 5])
        mockHonkerInstance.alert_if_too_close.assert_called_once()

    @patch("arduinoCommunicator.Honker")
    @patch("os.path.exists")
    @patch("arduinoCommunicator.time")
    def test_wait_times_between_readings(self, mock_time, mock_path, mock_honker, mock_sleep, mock_serial, mock_setmode):
        # mock the return value of Serial object to mock the method calls on it
        mockSerialInstance = mock_serial.return_value

        # set the in_waiting attribute 1 to avoid an infinite loop
        mockSerialInstance.in_waiting = 1

        mockHonkerInstance = mock_honker.return_value

        # mock the reading of the arduino input
        mock_readline = Mock()
        mock_readline.decode.return_value = "5"
        mockSerialInstance.readline.return_value = mock_readline

        # set the check of the port to return true
        mock_path.return_value = True

        mock_time.side_effect = [1, 2.99, 3.01, 5]

        waitTime = 2
        communicator = ArduinoCommunicator(self.port, self.baudrate, waitTime)

        # activate the distance sensors
        communicator.activate_distance_sensors(2, True, True)
        communicator.setup()

        # simulate the reading from arduino
        communicator.start()

        # assert that prepare_for_honking has been called once
        mockHonkerInstance.prepare_for_honking.assert_called_once()

        # call start again
        communicator.start()

        # assert that prepare_for_honking has still been called just once since
        # the wait time has not yet been exceeded
        mockHonkerInstance.prepare_for_honking.assert_called_once()

        # call start again
        communicator.start()

        # assert that that prepare_for_honking has now been called twice as the
        # wait time has been exceeded
        self.assertEqual(mockHonkerInstance.prepare_for_honking.call_count, 2)

    @patch("arduinoCommunicator.PhotocellManager")
    @patch("os.path.exists")
    def test_input_to_arduino(self, mock_path, mock_photocell, mock_sleep, mock_serial, mock_setmode):
        # mock the return value of Serial object to mock the method calls on it
        mockSerialInstance = mock_serial.return_value

        # set the in_waiting attribute 1 to avoid an infinite loop
        mockSerialInstance.in_waiting = 1

        # mock the reading of the arduino input
        mock_readline = Mock()
        mock_readline.decode.return_value = "5"
        mockSerialInstance.readline.return_value = mock_readline

        # set the check of the port to return true
        mock_path.return_value = True

        communicator = ArduinoCommunicator(self.port, self.baudrate)

        # activate the photocell lights
        communicator.activate_photocell_lights([1,2,3])
        communicator.setup()

        # simulate the reading from arduino
        communicator.start()

        # we expect the input to be a byte encoded sequence
        expectedInputToArduino = b'photocell\n'

        mockSerialInstance.write.assert_called_once_with(expectedInputToArduino)

    @patch("arduinoCommunicator.PhotocellManager")
    @patch("os.path.exists")
    def test_decoding_of_input_from_arduino(self, mock_path, mock_photocell, mock_sleep, mock_serial, mock_setmode):
        # mock the return value of Serial object to mock the method calls on it
        mockSerialInstance = mock_serial.return_value

        # set the in_waiting attribute 1 to avoid an infinite loop
        mockSerialInstance.in_waiting = 1

        # mock the reading of the arduino input to be a byte encoded sequence
        mockSerialInstance.readline.return_value = b'20.53'

        # mock the photocell manager
        mockPhotoCellInstance = mock_photocell.return_value

        # set the check of the port to return true
        mock_path.return_value = True

        communicator = ArduinoCommunicator(self.port, self.baudrate)

        # activate the photocell lights
        communicator.activate_photocell_lights([1, 2, 3])
        communicator.setup()

        # simulate the reading from arduino
        communicator.start()

        # check that the expected value is sent to the photocell manager
        expectedPhotocellReading = 20.53
        mockPhotoCellInstance.adjust_lights.assert_called_once_with(expectedPhotocellReading)
import unittest
from unittest.mock import patch, MagicMock, ANY, call
from multiprocessing import Array
import numpy as np
import numpy.testing as npt

# mock the import of picam2
MockPicam2 = MagicMock()
MockLibCam = MagicMock()
MockCv2 = MagicMock()
modules = {
    "picamera2": MockPicam2,
    "libcamera": MockLibCam,
    "cv2": MockCv2
}
patcher = patch.dict("sys.modules", modules)
patcher.start()

from camera import Camera
from libcamera import Transform

class TestCamera(unittest.TestCase):
        @patch("camera.Picamera2")
        def test_setup_calls_configuration_with_correct_resolution(self, mockPiCam):
            resolution = (1080, 720)
            rotation = False

            # this will be what self._picam2 in Camera will be set to
            mockPiCamInstance = mockPiCam.return_value

            # creating a mock return value for create_preview_config, so we can
            # check that configure() has been called with the value in setup
            mockPiCamInstance.create_preview_configuration.return_value = "mock_config"

            cam = Camera(resolution, rotation)
            cam.setup()

            # check that configure is called with the correct values
            mockPiCamInstance.create_preview_configuration.assert_called_once_with(
                {"size": (1080, 720), "format": "RGB888"},
                transform=Transform(vflip=False)
            )

            # check that the configure method is called with config data
            mockPiCamInstance.configure.assert_called_once_with(
                "mock_config"
            )
        @patch("camera.Picamera2")
        @patch("camera.cv2")
        def test_cleanup(self, mockCv2, mockPicam):
            mockPiCamInstance = mockPicam.return_value

            # setup camera
            cam = Camera((1080, 720), True)
            cam.setup()

            # close camera
            cam.cleanup()

            mockCv2.destroyAllWindows.assert_called_once()
            mockPiCamInstance.close.assert_called_once()

        @patch("camera.time")
        @patch("camera.Picamera2")
        @patch("camera.cv2")
        def test_output_of_control_values_is_not_called_according_to_HUD_value(self, mock_cv2, mock_piCam, mock_time):
            # set up camera
            cam = Camera((1080, 720), True)
            cam.setup()

            # set car and servo in camera
            cam.set_car_enabled()
            cam.set_servo_enabled()

            # add array dictionary
            arrayDict = {"servo": 0, "HUD": 1, "Zoom": 2, "speed": 3, "turn": 4}
            cam.add_array_dict(arrayDict)

            # set each time call to return a higher value to avoid a zero division error in the fps equation
            # I think this is because the test run so fast that looptime will be almost equal to 0
            mock_time.side_effect = [1,2,3,4]

            # simulate showing camera feed with HUD turned off
            array = Array('d', (0.0, 0.0, 2.0, 3.0, 1.0))
            cam.show_camera_feed(array)

            # check that the method to add text has NOT been called
            mock_cv2.putText.assert_not_called()

            # simulate showing camera feed with HUD turned on
            array = Array('d', (0.0, 1.0, 2.0, 3.0, 1.0))
            cam.show_camera_feed(array)

            # check that the method to add text has been called
            mock_cv2.putText.assert_called()

        @patch("camera.time")
        @patch("camera.cv2")
        def test_output_shows_correct_values(self, mock_cv2, mock_time):
            # set up camera
            cam = Camera((1080, 720), True)
            cam.setup()

            # set car and servo in camera
            cam.set_car_enabled()
            cam.set_servo_enabled()

            # add array dictionary
            arrayDict = {"servo": 0, "HUD": 1, "Zoom": 2, "speed": 3, "turn": 4}
            cam.add_array_dict(arrayDict)

            # setting return values of time to get an expected outcome of the fps equation
            mock_time.side_effect = [0.01, 0.02, 0.005, 0.01, 1, 2]

            # simulate showing camera feed with HUD turned on
            array = Array('d', (50.0, 1.0, 30.0, 20.0, 1.0))

            # call show_camera_feed three times to get the effects of the weightings in the fps equation
            cam.show_camera_feed(array)
            cam.show_camera_feed(array)
            cam.show_camera_feed(array)

            zoomText = "Zoom: 30.0x"
            angleText = "Angle: 50"
            speedText = "Speed: 20%"
            turnText = "Turn: Left"
            fpsText = "29 FPS"

            calls = [
                call(ANY, zoomText, ANY, ANY, ANY, ANY, ANY),
                call(ANY, angleText, ANY, ANY, ANY, ANY, ANY),
                call(ANY, speedText, ANY, ANY, ANY, ANY, ANY),
                call(ANY, turnText, ANY, ANY, ANY, ANY, ANY),
                call(ANY, fpsText, ANY, ANY, ANY, ANY, ANY)
            ]

            mock_cv2.putText.assert_has_calls(calls, any_order=False)

        @patch("camera.time")
        @patch("camera.cv2")
        def test_text_positions_with_all_text_enabled(self, mock_cv2, mock_time):
            # set up camera
            cam = Camera((1080, 720), True)
            cam.setup()

            # set car and servo in camera
            cam.set_car_enabled()
            cam.set_servo_enabled()

            # add array dictionary
            arrayDict = {"servo": 0, "HUD": 1, "Zoom": 2, "speed": 3, "turn": 4}
            cam.add_array_dict(arrayDict)

            # set each time call to return a higher value to avoid a zero division error in the fps equation
            # I think this is because the test run so fast that looptime will be almost equal to 0
            mock_time.side_effect = [1, 2]

            # simulate showing camera feed with HUD turned on
            array = Array('d', (50.0, 1.0, 30.0, 20.0, 1.0))
            cam.show_camera_feed(array)

            horizontalCoord = 10
            zoomTextPosition = (horizontalCoord, 705)
            angleTextPosition = (horizontalCoord, 675)
            speedTextPosition = (horizontalCoord, 645)
            turnTextPosition = (horizontalCoord, 615)
            fpsTextPosition = (horizontalCoord, 30) # fps has a designated position in the top left corner

            calls = [
                call(ANY, ANY, zoomTextPosition, ANY, ANY, ANY, ANY),
                call(ANY, ANY, angleTextPosition, ANY, ANY, ANY, ANY),
                call(ANY, ANY, speedTextPosition, ANY, ANY, ANY, ANY),
                call(ANY, ANY, turnTextPosition, ANY, ANY, ANY, ANY),
                call(ANY, ANY, fpsTextPosition, ANY, ANY, ANY, ANY)
            ]

            mock_cv2.putText.assert_has_calls(calls, any_order=False)

        @patch("camera.time")
        @patch("camera.cv2")
        def test_text_position_with_some_text_enabled(self, mock_cv2, mock_time):
            # set up camera
            cam = Camera((1080, 720), True)
            cam.setup()

            # set car, but not servo
            cam.set_car_enabled()

            # add array dictionary
            arrayDict = {"servo": 0, "HUD": 1, "Zoom": 2, "speed": 3, "turn": 4}
            cam.add_array_dict(arrayDict)

            # set each time call to return a higher value to avoid a zero division error in the fps equation
            # I think this is because the test run so fast that looptime will be almost equal to 0
            mock_time.side_effect = [1, 2]

            # simulate showing camera feed with HUD turned on
            array = Array('d', (50.0, 1.0, 30.0, 20.0, 1.0))
            cam.show_camera_feed(array)

            horizontalCoord = 10
            zoomTextPosition = (horizontalCoord, 705)
            speedTextPosition = (horizontalCoord, 675)
            turnTextPosition = (horizontalCoord, 645)
            fpsTextPosition = (horizontalCoord, 30)  # fps has a designated position in the top left corner

            calls = [
                call(ANY, ANY, zoomTextPosition, ANY, ANY, ANY, ANY),
                call(ANY, ANY, speedTextPosition, ANY, ANY, ANY, ANY),
                call(ANY, ANY, turnTextPosition, ANY, ANY, ANY, ANY),
                call(ANY, ANY, fpsTextPosition, ANY, ANY, ANY, ANY)
            ]

            mock_cv2.putText.assert_has_calls(calls, any_order=False)

        @patch("camera.Picamera2")
        @patch("camera.time")
        @patch("camera.cv2")
        def test_zoom(self, mock_cv2, mock_time, mock_picam):
            mockPiCamInstance = mock_picam.return_value

            displayWidth = 1080
            displayHeight = 720

            # setup camera
            cam = Camera((displayWidth, displayHeight), True)
            cam.setup()

            # add array dictionary
            arrayDict = {"servo": 0, "HUD": 1, "Zoom": 2, "speed": 3, "turn": 4}
            cam.add_array_dict(arrayDict)

            # set each time call to return a higher value to avoid a zero division error in the fps equation
            # I think this is because the test run so fast that looptime will be almost equal to 0
            mock_time.side_effect = [1, 2]

            # create random RGB image of size (1080, 720)
            image_array = np.random.randint(0, 256, size=(displayHeight, displayWidth, 3), dtype=np.uint8)

            # mock the image that the camera captures. This will be the input for the zoom function
            mockPiCamInstance.capture_array.return_value = image_array

            # the zoomed image should be sliced from the center points and halfway to the edges on a 2x zoom
            zoomedImage = image_array[180:540, 270:810]

            # simulate showing camera feed with zoom value equal to 2.0
            array = Array('d', (50.0, 0.0, 2.0, 20.0, 1.0))
            cam.show_camera_feed(array)

            # since there is some issues with array equality checking with the assert_called_with method, we unpack
            # the arguments called in the method and check them separately later
            calledArgs, calledKwargs = mock_cv2.resize.call_args

            # check that resize() was called
            mock_cv2.resize.assert_called()

            # check that the called arguments were as expected
            npt.assert_array_equal(calledArgs[0], zoomedImage)
            self.assertEqual((displayWidth, displayHeight), calledArgs[1])




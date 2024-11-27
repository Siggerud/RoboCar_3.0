import cv2
import os
os.environ["LIBCAMERA_LOG_LEVELS"] = "3" #disable info and warning logging
from picamera2 import Picamera2
from libcamera import Transform
from time import time

class Camera:
    def __init__(self, resolution, rotation=True):
        self._dispW, self._dispH = resolution
        self._centerX = int(self._dispW / 2)
        self._centerY = int(self._dispH / 2)
        self._rotation = rotation

        self._picam2 = None

        # text on video properties
        self._colour = (0, 255, 0)
        self._textPositions = self._set_text_positions()
        self._font = cv2.FONT_HERSHEY_SIMPLEX
        self._scale = 1
        self._thickness = 1

        self._angleText = None
        self._speedText = None
        self._turnText = None
        self._zoomValue = 1.0
        self._hudActive = True

        self._carEnabled = False
        self._servoEnabled = False

        self._fps = 0
        self._weightPrevFps = 0.9
        self._weightNewFps = 0.1
        self._fpsPos = (10, 30)

        self._arrayDict = None

        self._number_to_turnValue = {
            0: "-",
            1: "Left",
            2: "Right"
        }

    def setup(self):
        self._picam2 = Picamera2()

        # set resolution, format and rotation of camera feed
        config = self._picam2.create_preview_configuration(
            {"size": (self._dispW, self._dispH), "format": "RGB888"},
            transform=Transform(vflip=self._rotation)
        )
        self._picam2.configure(config)
        self._picam2.start()

    def show_camera_feed(self, shared_array):
        tStart = time() # start timer for calculating fps

        # get raw image
        im = self._picam2.capture_array()

        # read control values from external classes
        self._read_control_values_for_video_feed(shared_array)

        # resize image when zooming
        if self._zoomValue != 1.0:
            im = self._get_zoomed_image(im)

        # add control values to cam feed
        if self._hudActive:
            self._add_text_to_cam_feed(im)

        cv2.imshow("Camera", im)
        cv2.waitKey(1)

        # calculate fps
        self._calculate_fps(tStart)

    def cleanup(self):
        cv2.destroyAllWindows()
        self._picam2.close()

    def set_car_enabled(self):
        self._carEnabled = True

    def set_servo_enabled(self):
        self._servoEnabled = True

    def add_array_dict(self, arrayDict):
        self._arrayDict = arrayDict

    def _set_text_positions(self):
        spacingVertical = 30

        horizontalCoord = 10
        verticalCoord = self._dispH - 15

        positions = []
        for i in range(4):
            position = (horizontalCoord, verticalCoord - i * spacingVertical)
            positions.append(position)

        return positions

    def _calculate_fps(self, startTime):
        endTime = time()
        loopTime = endTime - startTime

        self._fps = self._weightPrevFps * self._fps + self._weightNewFps * (1 / loopTime)

    def _get_zoomed_image(self, image):
        halfZoomDisplayWidth = int(self._dispW / (2 * self._zoomValue))
        halfZoomDisplayHeight = int(self._dispH / (2 * self._zoomValue))

        regionOfInterest = image[self._centerY - halfZoomDisplayHeight:self._centerY + halfZoomDisplayHeight,
                           self._centerX - halfZoomDisplayWidth:self._centerX + halfZoomDisplayWidth]

        im = cv2.resize(regionOfInterest, (self._dispW, self._dispH), cv2.INTER_LINEAR)

        return im

    def _add_text_to_cam_feed(self, image):
        # add control values to camera feed
        counter = 0
        cv2.putText(image, "Zoom: " + str(self._zoomValue) + "x", self._get_origin(counter), self._font, self._scale,
                    self._colour,
                    self._thickness)
        counter += 1

        if self._angleText:
            cv2.putText(image, self._angleText, self._get_origin(counter), self._font, self._scale, self._colour,
                        self._thickness)
            counter += 1

        if self._speedText:
            cv2.putText(image, self._speedText, self._get_origin(counter), self._font, self._scale, self._colour,
                        self._thickness)
            counter += 1

        if self._turnText:
            cv2.putText(image, self._turnText, self._get_origin(counter), self._font, self._scale, self._colour,
                        self._thickness)
            counter += 1

        # display fps
        cv2.putText(image, self._get_fps(), self._fpsPos, self._font, self._scale, self._colour,
                    self._thickness)

    def _get_fps(self):
        return str(int(self._fps)) + " FPS"

    def _read_control_values_for_video_feed(self, shared_array):
        if self._carEnabled:
            self._speedText = "Speed: " + str(int(shared_array[self._arrayDict["speed"]])) + "%"
            self._turnText = "Turn: " + self._get_turn_value(shared_array[self._arrayDict["turn"]])
        if self._servoEnabled:
            self._angleText = "Angle: " + str(int(shared_array[self._arrayDict["servo"]]))

        self._hudActive = shared_array[self._arrayDict["HUD"]]
        self._zoomValue = shared_array[self._arrayDict["Zoom"]]

    def _get_turn_value(self, number):
        return self._number_to_turnValue[number]

    def _get_origin(self, count):
        return self._textPositions[count]
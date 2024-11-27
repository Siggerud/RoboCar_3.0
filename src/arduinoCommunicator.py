from os import path
from serial import Serial
from time import sleep, time
from honker import Honker
from photocellManager import PhotocellManager
import RPi.GPIO as GPIO

class ArduinoCommunicator:
    def __init__(self, port, baudrate, waitTime = 0.1):
        if not self._port_exists(port):
            raise InvalidPortError(f"Port {port} not found. Check connection.")

        self._serialObj = Serial(port, baudrate)
        sleep(3)  # give the serial object some time to start communication

        self._waitTime = waitTime

        self._frontSensorActive = False
        self._backSensorActive = False
        self._honker = None
        self._frontSensorReading = None
        self._backSensorReading = None

        self._photocellLightsActive = False
        self._photocellLightsManager = None
        self._photocellReading = None

        self._encodingType = 'utf-8'

        self._lastReadTime = None

    def setup(self):
        GPIO.setmode(GPIO.BOARD)

        if self._photocellLightsActive:
            self._photocellLightsManager.setup()

        if self._frontSensorActive or self._backSensorActive:
            self._honker.setup()

    def activate_distance_sensors(self, buzzerPin, front=True, back=True):
        self._frontSensorActive = front
        self._backSensorActive = back

        self._honker = Honker(buzzerPin)

    def activate_photocell_lights(self, lightPins):
        self._photocellLightsActive = True
        self._photocellLightsManager = PhotocellManager(lightPins)

    def start(self):
        # if it's been more than the specified wait time since last reading, then
        # do a new reading
        if not self._lastReadTime or (time() - self._lastReadTime) > self._waitTime:

            if self._frontSensorActive:
                self._frontSensorReading = self._send_command_and_read_response("front")

            if self._backSensorActive:
                self._backSensorReading = self._send_command_and_read_response("back")

            if self._photocellLightsActive:
                self._photocellReading = self._send_command_and_read_response("photocell")

            # run objects that only need to be updated per reading
            self._run_arduino_connected_objects_per_reading()

            self._lastReadTime = time()  # update last read time

        # run objects that need to be updated continuously
        self._run_arduino_connected_objects_continuously()

    def cleanup(self):
        self._serialObj.close()

        if self._photocellLightsManager:
            self._photocellLightsManager.cleanup()
        GPIO.cleanup()

    def _run_arduino_connected_objects_continuously(self):
        if self._frontSensorActive or self._backSensorActive:
            self._honker.alert_if_too_close()

    def _run_arduino_connected_objects_per_reading(self):
        # prepare honking values
        if self._frontSensorActive or self._backSensorActive:
            self._honker.prepare_for_honking(
                [self._frontSensorReading,
                 self._backSensorReading]
            )

        if self._photocellLightsActive:
            self._photocellLightsManager.adjust_lights(self._photocellReading)

    def _send_command_and_read_response(self, command):
        # send command to arduino
        self._serialObj.write(self._make_commands_arduino_readable(command))

        # wait for arduino response
        self._wait_for_arduino_input()

        # print out arduino response
        reading = float(self._make_arduino_response_readable(self._serialObj.readline()))

        return reading

    def _make_commands_arduino_readable(self, command):
        return (command + "\n").encode(self._encodingType)

    def _make_arduino_response_readable(self, response):
        return response.decode(self._encodingType).rstrip()

    def _wait_for_arduino_input(self):
        while self._serialObj.in_waiting <= 0:
            sleep(0.01)

    def _port_exists(self, portPath):
        return path.exists(portPath)

class InvalidPortError(Exception):
    pass





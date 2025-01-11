import RPi.GPIO as GPIO
from time import sleep
from roboObject import RoboObject

class SignalLights(RoboObject):
    def __init__(self, greenLightPin, yellowLightPin, redLightPin, blinkTime):
        super().__init__(
            [greenLightPin, yellowLightPin, redLightPin],
            {},
            blinkTime=blinkTime
        )

        self._lightPins: dict = {
            "green": greenLightPin,
            "yellow": yellowLightPin,
            "red": redLightPin
        }
        self._blinkTime: float = blinkTime

    def setup(self):
        for pin in self._lightPins.values():
            GPIO.setup(pin, GPIO.OUT)

        # blink three times in rapid sucession to signal startup
        self._blink_all_lights()

    def cleanup(self):
        self._blink_all_lights() # blink to signal that class is shutting down

    def blink(self, color):
        pin = self._lightPins[color]

        # turn on light
        GPIO.output(pin, GPIO.HIGH)
        sleep(self._blinkTime)

        # turn off light
        GPIO.output(pin, GPIO.LOW)

    def _blink_all_lights(self):
        timeBetweenBlinks: float = 0.1
        for _ in range(3):
            # turn on lights
            for pin in self._lightPins.values():
                GPIO.output(pin, GPIO.HIGH)

            sleep(self._blinkTime)

            # turn off lights
            for pin in self._lightPins.values():
                GPIO.output(pin, GPIO.LOW)

            sleep(timeBetweenBlinks)

    def _check_argument_validity(self, pins: list, userCommands: dict, **kwargs):
        super()._check_argument_validity(pins, userCommands, **kwargs)
        print("checking")
        self._check_if_num_is_in_interval(kwargs["blinkTime"], 0.1, 10, "blinkTime")



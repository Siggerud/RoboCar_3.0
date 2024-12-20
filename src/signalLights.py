import RPi.GPIO as GPIO
from time import sleep

class SignalLights:
    def __init__(self, greenLightPin, yellowLightPin, redLightPin):
        self._lightPins: dict = {
            "green": greenLightPin,
            "yellow": yellowLightPin,
            "red": redLightPin
        }
        self._blinkTime: int = 0.1

    def setup(self):
        for pin in self._lightPins.values():
            GPIO.setup(pin, GPIO.OUT)

        # blink three times in rapid sucession to signal startup
        self._blink_all_lights()


    def blink(self, color):
        pin = self._lightPins[color]
        GPIO.output(pin, GPIO.HIGH)
        sleep(self._blinkTime)
        GPIO.output(pin, GPIO.LOW)

    def _blink_all_lights(self):
        for _ in range(3):
            for pin in self._lightPins.values():
                GPIO.output(pin, GPIO.HIGH)

            sleep(self._blinkTime)

            for pin in self._lightPins.values():
                GPIO.output(pin, GPIO.LOW)

            sleep(self._blinkTime)



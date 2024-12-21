import RPi.GPIO as GPIO
from time import sleep

class SignalLights:
    def __init__(self, greenLightPin, yellowLightPin, redLightPin, blinkTime):
        self._lightPins: dict = {
            "green": greenLightPin,
            "yellow": yellowLightPin,
            "red": redLightPin
        }
        self._blinkTime: float = 0.2

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



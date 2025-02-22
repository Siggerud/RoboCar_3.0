import RPi.GPIO as GPIO
from gpioObject import GPIOObject

class Buzzer(GPIOObject):
    def __init__(self, pin, boardMode: str = "BOARD"):
        super().__init__(boardMode)
        self._buzzPin = pin

    def setup(self):
        super().setup([self._buzzPin])

    def start_buzzing(self):
        GPIO.output(self._buzzPin, GPIO.HIGH)

    def stop_buzzing(self):
        GPIO.output(self._buzzPin, GPIO.LOW)


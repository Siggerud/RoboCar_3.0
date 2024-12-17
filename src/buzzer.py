import RPi.GPIO as GPIO
from time import sleep

class Buzzer:
    def __init__(self, buzzerPin: int):
        self._buzzerPin: int = buzzerPin
        self._defaultHonkTime = 0.3 #TODO: add this to config
        self._buzzCommand: dict = {"honk now": {"description": "starts honking"}}

    def setup(self):
        GPIO.setup(self._buzzerPin, GPIO.OUT)

    def handle_voice_command(self, command):
        if command in self._buzzCommand:
            self._buzz()

    def get_voice_commands(self) -> list[str]:
        return list(self._buzzCommand.keys())

    def _buzz(self):
        GPIO.output(self._buzzerPin, GPIO.HIGH)
        sleep(self._defaultHonkTime)
        GPIO.output(self._buzzerPin, GPIO.LOW)



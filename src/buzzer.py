import RPi.GPIO as GPIO
from time import sleep
from roboCarHelper import RobocarHelper

class Buzzer:
    def __init__(self, buzzerPin: int):
        self._buzzerPin: int = buzzerPin
        self._defaultHonkTime = 0.3 #TODO: add this to config
        self._maxHonkTime = 2 #TODO: add this to config
        self._buzzCommand: dict = {"start horn": {"description": "starts honking"}}
        self._buzzForSpecifiedTimeCommands: dict = self._set_honk_for_specified_time_commands()
        print(self._buzzForSpecifiedTimeCommands)

    def setup(self):
        GPIO.setup(self._buzzerPin, GPIO.OUT)

    def handle_voice_command(self, command):
        if command in self._buzzCommand:
            honkTime = self._defaultHonkTime
        elif command in self._buzzForSpecifiedTimeCommands:
            print("Honking for a specified time")
            honkTime = self._buzzForSpecifiedTimeCommands[command]

        self._buzz(honkTime)

    def get_voice_commands(self) -> list[str]:
        return RobocarHelper.chain_together_dict_keys([self._buzzCommand,
                                                       self._buzzForSpecifiedTimeCommands]
                                                      )

    def _buzz(self, honkTime):
        GPIO.output(self._buzzerPin, GPIO.HIGH)
        sleep(honkTime)
        GPIO.output(self._buzzerPin, GPIO.LOW)

    def _set_honk_for_specified_time_commands(self) -> dict:
        honkTime: float = 0.1
        stepValue: float = 0.1
        honkCommands: dict = {}
        while honkTime <= self._maxHonkTime:
            honkCommands[f"start horn {round(honkTime, 1)}"] = round(honkTime, 1) # round honkTime to avoid floating numbers with many decimals

            honkTime += stepValue

        return honkCommands



from roboCarHelper import RobocarHelper
import RPi.GPIO as GPIO
from typing import Optional

class GPIOObject:
    def __init__(self, boardMode: str):
        self._boardMode: str = boardMode
        self._pinMap: dict[int: int] = {}

    def setup(self, outPins: list[int]) -> None:
        setBoardMode = self._get_board_mode()
        # map the pins to the correct board mode
        self._pinMap = self._set_pin_map(outPins, setBoardMode)

        for pin in outPins:
            GPIO.setup(self._pinMap[pin], GPIO.OUT)

    def _get_pwm_pin(self, pin: int, frequency: int) -> GPIO.PWM:
        return GPIO.PWM(self._pinMap[pin], frequency)

    def _set_pin_low(self, pin: int) -> None:
        GPIO.output(self._pinMap[pin], GPIO.LOW)

    def _set_pin_high(self, pin: int) -> None:
        GPIO.output(self._pinMap[pin], GPIO.HIGH)

    def _set_pin_map(self, outPins: list[int], setBoardMode: str) -> dict[int: int]:
        if self._boardMode == "BOARD" and setBoardMode == "BCM":
            return {pin: RobocarHelper.get_board_to_bcm_pins(pin) for pin in outPins}
        elif self._boardMode == "BCM" and setBoardMode == "BOARD":
            return {pin: RobocarHelper.get_bcm_to_board_pins(pin) for pin in outPins}
        else:
            return {pin: pin for pin in outPins}

    def _get_board_mode(self) -> Optional[str]:
        boardLayouts: dict[int, str] = {
            10: "BOARD",
            11: "BCM"
        }

        setMode = boardLayouts.get(GPIO.getmode())

        return setMode



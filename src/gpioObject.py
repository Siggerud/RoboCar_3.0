from roboCarHelper import RobocarHelper
import RPi.GPIO as GPIO
from typing import Optional

class GPIOObject:
    def __init__(self, boardMode: str):
        self._boardMode: str = boardMode

    def setup(self, outPins: list) -> None:
        setBoardMode = self._get_board_mode()

        for pin in outPins:
            if self._boardMode == "BOARD" and setBoardMode == "BCM":
                pin = RobocarHelper.get_board_to_bcm_pins(pin)
            elif self._boardMode == "BCM" and setBoardMode == "BOARD":
                pin = RobocarHelper.get_bcm_to_board_pins(pin)
            GPIO.setup(pin, GPIO.OUT)

    def _get_board_mode(self) -> Optional[str]:
        boardLayouts: dict[int, str] = {
            10: "BOARD",
            11: "BCM"
        }

        setMode = boardLayouts.get(GPIO.getmode())

        return setMode



from dataclasses import dataclass

@dataclass
class GpioValues:
    leftForward: bool
    rightForward: bool
    leftBackward: bool
    rightBackward: bool


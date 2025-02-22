import RPi.GPIO as GPIO
from gpioObject import GPIOObject

class MotorDriver(GPIOObject):
    def __init__(self,
                 leftBackward: int,
                 leftForward: int,
                 rightBackward: int,
                 rightForward: int,
                 enA: int,
                 enB: int,
                 boardMode: str = "BOARD"):
        super().__init__(boardMode)
        self._leftBackward: int = leftBackward
        self._leftForward: int = leftForward
        self._rightBackward: int = rightBackward
        self._rightForward: int = rightForward
        self._enA: int = enA
        self._enB: int = enB
        self._boardMode: str = boardMode

        self._pwmA = None
        self._pwmB = None

    def setup(self, startSpeed):
        super().setup([self._leftBackward,
                       self._leftForward,
                       self._rightBackward,
                       self._rightForward,
                       self._enA,
                       self._enB]
                      )

        self._pwmA = GPIO.PWM(self._enA, 100)
        self._pwmB = GPIO.PWM(self._enB, 100)

        self._pwmA.start(startSpeed)
        self._pwmB.start(startSpeed)

    @property
    def pins(self):
        return [self._leftBackward, self._leftForward, self._rightBackward, self._rightForward, self._enA, self._enB]

    def change_speed(self, speed):
        for pwm in [self._pwmA, self._pwmB]:
            pwm.ChangeDutyCycle(speed)

    def drive(self):
        GPIO.output(self._leftForward, GPIO.HIGH)
        GPIO.output(self._rightForward, GPIO.HIGH)
        GPIO.output(self._leftBackward, GPIO.LOW)
        GPIO.output(self._rightBackward, GPIO.LOW)

    def reverse(self):
        GPIO.output(self._leftForward, GPIO.LOW)
        GPIO.output(self._rightForward, GPIO.LOW)
        GPIO.output(self._leftBackward, GPIO.HIGH)
        GPIO.output(self._rightBackward, GPIO.HIGH)

    def turn_left(self):
        GPIO.output(self._leftForward, GPIO.HIGH)
        GPIO.output(self._rightForward, GPIO.LOW)
        GPIO.output(self._leftBackward, GPIO.LOW)
        GPIO.output(self._rightBackward, GPIO.HIGH)

    def turn_right(self):
        GPIO.output(self._leftForward, GPIO.LOW)
        GPIO.output(self._rightForward, GPIO.HIGH)
        GPIO.output(self._leftBackward, GPIO.HIGH)
        GPIO.output(self._rightBackward, GPIO.LOW)

    def stop(self):
        GPIO.output(self._leftForward, GPIO.LOW)
        GPIO.output(self._rightForward, GPIO.LOW)
        GPIO.output(self._leftBackward, GPIO.LOW)
        GPIO.output(self._rightBackward, GPIO.LOW)

    def cleanup(self) -> None:
        self._pwmA.stop()
        self._pwmB.stop()

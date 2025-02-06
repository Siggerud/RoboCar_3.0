import pigpio
from roboCarHelper import RobocarHelper
from time import sleep

class Servo:
    pi = pigpio.pi()

    def __init__(self, pin: int):
        self._servoPin: int = pin

        self._pwmAbsoluteMin: int = 500  # value all the way to the right or down
        self._pwmAbsoluteMax: int = 2500  # value all the way to the left or up

        self._angleToPwm: dict = self._get_angle_mapped_to_pwm_values()

        self._current_angle: int = 0

    def setup(self) -> None:
        self.pi.set_mode(self._servoPin, pigpio.OUTPUT)
        self.move_to_angle(0)

    def cleanup(self) -> None:
        self.pi.set_servo_pulsewidth(self._servoPin, 0)
        sleep(0.05)

    def move_to_angle(self, angle: int) -> None:
        self.pi.set_servo_pulsewidth(self._servoPin, self._angleToPwm[angle])
        self._current_angle = angle

    def get_current_angle(self) -> int:
        return self._current_angle

    def _get_angle_mapped_to_pwm_values(self) -> dict[int: float]:
        minAngle: int = -90
        maxAngle: int = 90
        return {angle: self._angle_to_pwm(angle) for angle in range(minAngle, maxAngle + 1)}

    def _angle_to_pwm(self, angle: int) -> float:
        pwmValue: float = RobocarHelper.map_value_to_new_scale(
                angle,
                self._pwmAbsoluteMin,
                self._pwmAbsoluteMax,
                1,
                - 90,
                90
            )

        return pwmValue

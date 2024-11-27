from roboCarHelper import map_value_to_new_scale
import pigpio

class ServoHandling:

    pigpioPwm = pigpio.pi()
    pwmMinServo = 2500
    pwmMaxServo = 500

    def __init__(self, servoPin, plane, minAngle=-90, maxAngle=90):
        self._servoPin = servoPin
        self._plane = plane
        self._minAngle = minAngle
        self._maxAngle = maxAngle

        self._lastServoStickValue = 0
        self._servoValueChanged = False

        self._servoPwmValue = 1500 # neutral (0 degrees)
        self._pwmMinServo = map_value_to_new_scale(
            minAngle,
            ServoHandling.pwmMinServo,
            ServoHandling.pwmMaxServo,
            1,
            - 90,
            90
        )
        self._pwmMaxServo = map_value_to_new_scale(
            maxAngle,
            ServoHandling.pwmMinServo,
            ServoHandling.pwmMaxServo,
            1,
            - 90,
            90
        )

        self._controlsDictServo = {
            "Servo": self._get_servo_button_corresponding_to_axis(plane)
        }

        self._moveServoButton = self._controlsDictServo["Servo"]

    def setup(self):
        ServoHandling.pigpioPwm.set_mode(self._servoPin, pigpio.OUTPUT)
        ServoHandling.pigpioPwm.set_PWM_frequency(self._servoPin, 50) # 50 hz is typical for servos

    def handle_xbox_input(self, button, pressValue):
        if button == self._moveServoButton:
            self._prepare_for_servo_movement(pressValue)
            self._move_servo()

    def get_servo_buttons(self):
        return self._controlsDictServo

    def get_plane(self):
        return self._plane

    def get_current_servo_angle(self):
        current_servo_angle = int(map_value_to_new_scale(
            self._servoPwmValue,
            self._minAngle,
            self._maxAngle,
            0,
            self._pwmMinServo,
            self._pwmMaxServo)
        )

        return current_servo_angle

    def _move_servo(self):
        if self._servoValueChanged:
            ServoHandling.pigpioPwm.set_servo_pulsewidth(self._servoPin, self._servoPwmValue)

    def _get_servo_button_corresponding_to_axis(self, plane):
        if plane == "horizontal":
            return "RSB horizontal"
        elif plane == "vertical":
            return "RSB vertical"

    def _prepare_for_servo_movement(self, buttonPressValue):
        stickValue = round(buttonPressValue, 1)

        if stickValue == self._lastServoStickValue:
            self._servoValueChanged = False
        else:
            self._servoValueChanged = True
            self._servoPwmValue = map_value_to_new_scale(stickValue, self._pwmMinServo, self._pwmMaxServo, 1)
            self._lastServoStickValue = stickValue

    def cleanup(self):
        ServoHandling.pigpioPwm.set_PWM_dutycycle(self._servoPin, 0)
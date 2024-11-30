import RPi.GPIO as GPIO
from roboCarHelper import map_value_to_new_scale

class PhotocellManager:
    def __init__(self, lightPins):
        self._lightPins = lightPins
        self._pwms = []

        self._minLightSensorValue = 0
        self._maxLightSensorValue = 1023

        self._minPwmValue = 0
        self._maxPwmValue = 99
        self._currentPwmValue = 0
        self._lastPwmValue = 0

    def setup(self):
        pwmFrequency = 100
        for pin in self._lightPins:
            GPIO.setup(pin, GPIO.OUT)

            pwm = GPIO.PWM(pin, pwmFrequency)
            self._pwms.append(pwm)

            pwm.start(0)

    def adjust_lights(self, lightSensorValue):
        self._prepare_for_light_adjustment(lightSensorValue)

        if self._currentPwmValue != self._lastPwmValue: # adjust lights if sensor value has changed
            for pwm in self._pwms:
                pwm.ChangeDutyCycle(self._currentPwmValue)

            self._lastPwmValue = self._currentPwmValue # update last pwm value to current

    def cleanup(self):
        for pwm in self._pwms:
            pwm.stop()

    def _prepare_for_light_adjustment(self, lightSensorValue):
        # the car lights pwm value have an inverse relationship to the light sensor value
        self._currentPwmValue = map_value_to_new_scale(
            lightSensorValue,
            self._minPwmValue,
            self._maxPwmValue,
            0,
            self._maxLightSensorValue,
            self._minLightSensorValue
        )




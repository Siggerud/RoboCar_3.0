import RPi.GPIO as GPIO
from time import time
from roboCarHelper import map_value_to_new_scale

class Honker:
    def __init__(self, buzzerPin):
        self._buzzerPin = buzzerPin
        self._withinAlarmDistance = False

        self._distanceTreshold = 10
        self._currentLowestDistance = None

        self._honkCurrentlyOn = False
        self._lastHonkChangeTime = time()

        self._lowEndTimeBetweenEachHonk = 0.4
        self._highEndTimeBetweenEachHonk = 0.01

    def setup(self):
        GPIO.setup(self._buzzerPin, GPIO.OUT, initial=self._withinAlarmDistance)

    def prepare_for_honking(self, sensors):
        self._set_honk_on_or_off(sensors) # check if car is within treshold distance
        self._set_honk_timing() # update frequency of alarm beeping

    def alert_if_too_close(self):
        if not self._withinAlarmDistance:
            honk = False
        else:
            honk = self._honkCurrentlyOn

        GPIO.output(self._buzzerPin, honk)

    def _set_honk_on_or_off(self, sensors):
        if self._check_if_any_response_is_below_threshold(sensors):
            self._withinAlarmDistance = True
        else:
            self._withinAlarmDistance = False

    def _set_honk_timing(self):
        if self._withinAlarmDistance:
            # time between each honk is determined by the distance to the obstacle
            timeBetweenEachHonk = map_value_to_new_scale(
                self._currentLowestDistance,
                self._lowEndTimeBetweenEachHonk,
                self._highEndTimeBetweenEachHonk,
                1,
                self._distanceTreshold,
                0
            )

            # if time passed is longer than the wait time between the trigger
            # to change, then change
            if (time() - self._lastHonkChangeTime) > timeBetweenEachHonk:
                self._honkCurrentlyOn = not self._honkCurrentlyOn
                self._lastHonkChangeTime = time()  # update time of last change

    def _check_if_any_response_is_below_threshold(self, sensorValues):
        sensorValues = [sensor for sensor in sensorValues if sensor] # remove None values
        self._currentLowestDistance = min(sensorValues)
        if self._currentLowestDistance < self._distanceTreshold:
            return True

        return False
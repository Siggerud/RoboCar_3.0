from mpu6050 import mpu6050
from time import sleep
from math import atan, pi
from roboCarHelper import RobocarHelper

class Stabilizer:
    def __init__(self, address: int = 0x68):
        self._mpu6050 = mpu6050(address)
        self._rollAngle = 0
        self._pitchAngle = 0

        #TODO: add axis inputs to config file
        self._pitchAxis = "y"
        self._rollAxis = "x"

    def stabilize(self):
        # Read the sensor data
        accelerometer_data = self._mpu6050.get_accel_data(g=True)  # get value in gravity units

        # Print the sensor data
        rollAccel = self._set_value_equal_to_1_if_greater(accelerometer_data[self._rollAxis])
        pitchAccel = self._set_value_equal_to_1_if_greater(accelerometer_data[self._pitchAxis])
        yawAccel = self._set_value_equal_to_1_if_greater(accelerometer_data["z"])

        # Calculate the latest angles
        newRollAngle = self._calculate_angles_in_degrees(rollAccel, yawAccel)
        newPitchAngle = self._calculate_angles_in_degrees(pitchAccel, yawAccel)

        # Apply low pass filter to the angles to limit the effect of acceleration noise
        # on the reading of gravity vectors
        confidenceFactor = 0.3

        self._rollAngle = RobocarHelper.low_pass_filter(newRollAngle, self._rollAngle, confidenceFactor)
        self._pitchAngle = RobocarHelper.low_pass_filter(newPitchAngle, self._pitchAngle, confidenceFactor)

        print(f"xAngle: {self._rollAngle}, yAngle: {self._pitchAngle}")

        # Wait for 1 second
        sleep(0.1)

    def _set_value_equal_to_1_if_greater(self, accelValue):
        if accelValue > 1:
            return 1
        return accelValue

    def _calculate_angles_in_degrees(self, opposite, adjacent):
        return atan(opposite / adjacent) * 180 / pi


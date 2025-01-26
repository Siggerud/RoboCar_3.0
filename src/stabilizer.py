from mpu6050 import mpu6050
from time import sleep
from math import atan, pi
from roboCarHelper import RobocarHelper

class Stabilizer:
    def __init__(self, address: int = 0x68):
        self._mpu6050 = mpu6050(address)
        self._xAngle = 0
        self._yAngle = 0

    def stabilize(self):
        # Read the sensor data
        accelerometer_data = self._mpu6050.get_accel_data(g=True)  # get value in gravity units

        # Print the sensor data
        xAccel = self._set_value_equal_to_1_if_greater(accelerometer_data["x"])
        yAccel = self._set_value_equal_to_1_if_greater(accelerometer_data["y"])
        zAccel = self._set_value_equal_to_1_if_greater(accelerometer_data["z"])

        # Calculate the latest angles
        newXAngle = self._calculate_angles_in_degrees(xAccel, zAccel)
        newYAngle = self._calculate_angles_in_degrees(yAccel, zAccel)

        # Apply low pass filter to the angles to limit the effect of acceleration noise
        # on the reading of gravity vectors
        confidenceFactor = 0.3

        self._xAngle = RobocarHelper.low_pass_filter(newXAngle, self._xAngle, confidenceFactor)
        self._yAngle = RobocarHelper.low_pass_filter(newYAngle, self._yAngle, confidenceFactor)

        print(f"xAngle: {self._xAngle}, yAngle: {self._yAngle}")

        # Wait for 1 second
        sleep(0.1)

    def _set_value_equal_to_1_if_greater(self, accelValue):
        if accelValue > 1:
            return 1
        return accelValue

    def _calculate_angles_in_degrees(self, opposite, adjacent):
        return atan(opposite / adjacent) * 180 / pi


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

        # Calculate the angle and convert from radian to degrees
        self._xAngle = RobocarHelper.low_pass_filter(self._calculate_angles_in_degrees(xAccel, zAccel), self._xAngle)
        self._yAngle = RobocarHelper.low_pass_filter(self._calculate_angles_in_degrees(yAccel, zAccel), self._xAngle)

        print(f"xAngle: {self._xAngle}, yAngle: {self._yAngle}")

        # Wait for 1 second
        sleep(1)

    def _set_value_equal_to_1_if_greater(self, accelValue):
        if accelValue > 1:
            return 1
        return accelValue

    def _calculate_angles_in_degrees(self, opposite, adjacent):
        return atan(opposite / adjacent) * 180 / pi


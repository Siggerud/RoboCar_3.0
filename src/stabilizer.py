from mpu6050 import mpu6050
from time import sleep
from math import atan, pi

class Stabilizer:
    def __init__(self, address: int = 0x68):
        self._mpu6050 = mpu6050(address)

    def stabilize(self):
        # Read the sensor data
        accelerometer_data = self._mpu6050.get_accel_data(g=True) # get value in gravity units

        # Print the sensor data
        xAccel = self._set_value_equal_to_1_if_greater(accelerometer_data["x"])
        yAccel = self._set_value_equal_to_1_if_greater(accelerometer_data["y"])
        zAccel = self._set_value_equal_to_1_if_greater(accelerometer_data["z"])

        # Calculate the angle and convert from radian to degrees
        xAngle = atan(xAccel / zAccel) * 180 / pi
        yAngle = atan(yAccel / zAccel) * 180 / pi

        print(f"xAngle: {xAngle}, yAngle: {yAngle}")

        # Wait for 1 second
        sleep(1)

    def _set_value_equal_to_1_if_greater(self, accelValue):
        if accelValue > 1:
            return 1
        return accelValue


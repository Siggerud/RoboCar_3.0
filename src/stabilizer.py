from mpu6050 import mpu6050
from time import sleep, time
from math import atan, pi
from roboCarHelper import RobocarHelper

class Stabilizer:
    def __init__(self, address: int = 0x68):
        self._mpu6050 = mpu6050(address)
        self._rollAccelAngle = 0
        self._pitchAccelAngle = 0

        self._time = 0
        self._tLoop = 0

        self._rollComp = 0
        self._pitchComp = 0

        self._errorRoll = 0
        self._errorPitch = 0

        self._confidenceFactor = 0.92
        self._errorFactor = 0.01


    def stabilize(self):
        tStart = time()
        # Read the sensor data
        accelerometer_data = self._mpu6050.get_accel_data(g=True)  # get value in gravity units

        # unpack the accelerometer data
        rollAccel = self._set_value_equal_to_1_if_greater(accelerometer_data["y"])
        pitchAccel = self._set_value_equal_to_1_if_greater(accelerometer_data["x"])
        yawAccel = self._set_value_equal_to_1_if_greater(accelerometer_data["z"])

        # Calculate the latest angles based on accelerometer data
        self._rollAccelAngle = self._calculate_angles_in_degrees(rollAccel, yawAccel)
        self._pitchAccelAngle = self._calculate_angles_in_degrees(pitchAccel, yawAccel)

        # Read the gyro data
        gyro_data = self._mpu6050.get_gyro_data()

        # unpack the gyro data
        xGyro = gyro_data["x"]
        yGyro = gyro_data["y"]

        # Calculate the latest angles deltas based on gyro data
        rollGyroAngleDelta = xGyro * self._tLoop
        pitchGyroAngleDelta = yGyro * self._tLoop

        # calculate the complimentary angles based on data from both the accelerometer and the gyro data. We use
        # the low pass filter as a complimentary filter in this case
        self._rollComp = RobocarHelper.low_pass_filter((self._rollComp + rollGyroAngleDelta), self._rollAccelAngle, self._confidenceFactor) + self._errorRoll * self._errorFactor
        self._pitchComp = RobocarHelper.low_pass_filter((self._pitchComp + pitchGyroAngleDelta), self._pitchAccelAngle, self._confidenceFactor) + self._errorPitch * self._errorFactor

        # calculate the steady state error values
        self._errorRoll = self._errorRoll + (self._rollAccelAngle - self._rollComp) * self._tLoop
        self._errorPitch = self._errorPitch + (self._pitchAccelAngle - self._pitchComp) * self._tLoop

        print(f"rollA: {round(self._rollAccelAngle, 2)}, rollC: {round(self._rollComp, 2)}, pitchA: {round(self._pitchAccelAngle, 2)}, pitchC: {round(self._pitchComp, 2)}")

        tStop = time()
        self._tLoop = tStop - tStart

    def _set_value_equal_to_1_if_greater(self, accelValue):
        if accelValue > 1:
            return 1
        return accelValue

    def _calculate_angles_in_degrees(self, opposite, adjacent):
        return atan(opposite / adjacent) * 180 / pi


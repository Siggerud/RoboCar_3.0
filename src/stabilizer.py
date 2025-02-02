from mpu6050 import mpu6050
from time import sleep, time
from math import atan, pi
from roboCarHelper import RobocarHelper


class Stabilizer:
    def __init__(self, rollAxis: str, pitchAxis: str, offsets: dict[str: float]):
        self._mpu6050 = mpu6050(0x68)
        self._rollAxis: str = rollAxis
        self._pitchAxis: str = pitchAxis
        self._yawAxis: str = "z"

        self._offsetRoll = offsets[rollAxis]
        self._offsetPitch = offsets[pitchAxis]

        self._rollAccelAngle: float = 0
        self._pitchAccelAngle: float = 0

        self._time: float = 0
        self._tLoop: float = 0

        self._rollComp: float = 0
        self._pitchComp: float = 0

        self._errorRoll: float = 0
        self._errorPitch: float = 0

        self._confidenceFactor: float = 0.92
        self._errorFactor: float = 0.01

        self._count = 0

    def stabilize(self):
        tStart: float = time()
        # Read the sensor data
        accelerometer_data: dict[str: float] = self._mpu6050.get_accel_data(g=True)  # get value in gravity units

        # unpack the accelerometer data
        rollAccel: float = self._set_value_equal_to_1_if_greater(accelerometer_data[self._rollAxis])
        pitchAccel: float = self._set_value_equal_to_1_if_greater(accelerometer_data[self._pitchAxis])
        yawAccel: float = self._set_value_equal_to_1_if_greater(accelerometer_data[self._yawAxis])

        # Calculate the latest angles based on accelerometer data and subtract the offsets
        self._rollAccelAngle = self._calculate_angles_in_degrees(rollAccel, yawAccel) - self._offsetRoll
        self._pitchAccelAngle = self._calculate_angles_in_degrees(pitchAccel, yawAccel) - self._offsetPitch

        # Read the gyro data
        gyro_data: dict[str: float] = self._mpu6050.get_gyro_data()

        # unpack the gyro data
        xGyro: float = gyro_data[self._pitchAxis]
        yGyro: float = gyro_data[self._rollAxis]

        # Calculate the latest angles deltas based on gyro data
        rollGyroAngleDelta: float = xGyro * self._tLoop
        pitchGyroAngleDelta: float = yGyro * self._tLoop

        # calculate the complimentary angles based on data from both the accelerometer and the gyro data. We use
        # the low pass filter as a complimentary filter in this case
        self._rollComp = RobocarHelper.low_pass_filter((self._rollComp + rollGyroAngleDelta), self._rollAccelAngle, self._confidenceFactor) + self._errorRoll * self._errorFactor
        self._pitchComp = RobocarHelper.low_pass_filter((self._pitchComp + pitchGyroAngleDelta), self._pitchAccelAngle, self._confidenceFactor) + self._errorPitch * self._errorFactor

        # calculate the steady state error values
        self._errorRoll = self._errorRoll + (self._rollAccelAngle - self._rollComp) * self._tLoop
        self._errorPitch = self._errorPitch + (self._pitchAccelAngle - self._pitchComp) * self._tLoop
        self._count += 1
        if self._count % 50 == 0:
            print(f"rollA: {round(self._rollAccelAngle, 2)}, rollC: {round(self._rollComp, 2)}, pitchA: {round(self._pitchAccelAngle, 2)}, pitchC: {round(self._pitchComp, 2)}")

        tStop: float = time()
        self._tLoop = tStop - tStart

    #TODO: make a test of this method
    def _set_value_equal_to_1_if_greater(self, accelValue: float) -> float:
        if accelValue > 1:
            return 1
        return accelValue

    def _calculate_angles_in_degrees(self, opposite: float, adjacent: float) -> float:
        return atan(opposite / adjacent) * 180 / pi

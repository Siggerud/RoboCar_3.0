from mpu6050 import mpu6050
from time import sleep

class Stabilizer:
    def __init__(self, address: int = 0x68):
        self._mpu6050 = mpu6050(address)

    def stabilize(self):
        # Read the sensor data
        accelerometer_data = self._mpu6050.get_accel_data()

        # Print the sensor data
        if accelerometer_data["x"] > 0.5:
            print("tilting car backward")
        elif accelerometer_data["x"] < -0.5:
            print("tilting car forward")

        if accelerometer_data["y"] > 0.5:
            print("tilting car to the right")
        elif accelerometer_data["y"] < -0.5:
            print("tilting car to the left")

        # Wait for 1 second
        sleep(1)

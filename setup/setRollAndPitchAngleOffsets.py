from mpu6050 import mpu6050
from math import atan, pi
from configparser import ConfigParser

mpu = mpu6050(0x68)

print("Place the car on a horizontal surface...")
answer: str = input("Press y when car is on horizontal surface, and q to quit\n")
if answer == "q":
    print("Quitting setup of offset angles")
    exit()

print("\nGetting offset angles...")
xAccel: float = mpu.get_accel_data()["x"]
yAccel: float = mpu.get_accel_data()["y"]
zAccel: float = mpu.get_accel_data()["z"]

offsetX: float  = atan(xAccel / zAccel) / 2 / pi * 360
offsetY: float  = atan(yAccel / zAccel) / 2 / pi * 360

print(f"Found offsets: x-axis {offsetX}°, y-axis {offsetY}")
answer: str = input("Do you want to write these values to the config file? (y/n)\n")
if answer == "n":
    print("Quitting setup of offset angles")
    exit()

print("\nWriting offsets to config file...")
config = ConfigParser()
config.read("../src/config.ini")
config["Stabilizer"]["offset_x"] = str(round(offsetX, 3))
config["Stabilizer"]["offset_y"] = str(round(offsetY, 3))
with open("../src/config.ini", "w") as configFile:
    config.write(configFile)
print(f"offset_x value set to {offsetX} and offset_y value set to {offsetY}")

from adafruit_servokit import ServoKit

class Pca9685:
    def __init__(self):
        self.kit = ServoKit(channels=8)




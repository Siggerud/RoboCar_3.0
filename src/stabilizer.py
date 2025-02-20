from motionTrackingDevice import MotionTrackingDevice
from adafruit_servokit import ServoKit

class Stabilizer:
    def __init__(self, motionTrackingDevice: MotionTrackingDevice, rollTreshold: int, pitchTreshold: int):
        self._motionTrackingDevice = motionTrackingDevice
        self._rollTreshold = rollTreshold
        self._pitchTreshold = pitchTreshold
        self._count = 0

        self._kit = ServoKit(channels=16)

        self._overRollTreshold = False
        self._overPitchTreshold = False
        self._maxRoll = 0
        self._maxPitch = 0

    def stabilize(self):
        self._count += 1
        rollAngle, pitchAngle = self._motionTrackingDevice.get_roll_and_pitch()
        if self._count % 50 == 0:
            print(f"Roll angle: {rollAngle}, Pitch angle: {pitchAngle}")
            print(f"Max roll: {self._maxRoll}, Max pitch: {self._maxPitch}")
            print()

        if abs(rollAngle) > self._rollTreshold:
            if self._overRollTreshold == False:
                print("Roll angle is too high")
                self._kit.servo[0].angle = 45
                self._kit.servo[1].angle = 45
                self._overRollTreshold = True
        else:
            if self._overRollTreshold == True:
                print("Roll angle back to ok levels")
                self._kit.servo[0].angle = 90
                self._kit.servo[1].angle = 90
                self._overRollTreshold = False

        if abs(pitchAngle) > self._pitchTreshold:
            if self._overPitchTreshold == False:
                self._kit.servo[2].angle = 45
                self._kit.servo[3].angle = 45
                print("Pitch angle is too high")
                self._overPitchTreshold = True
        else:
            if self._overPitchTreshold == True:
                print("Pitch angle back to ok levels")
                self._kit.servo[2].angle = 90
                self._kit.servo[3].angle = 90
                self._overPitchTreshold = False






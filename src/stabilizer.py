from motionTrackingDevice import MotionTrackingDevice

class Stabilizer:
    def __init__(self, motionTrackingDevice: MotionTrackingDevice, rollTreshold: int, pitchTreshold: int):
        self._motionTrackingDevice = motionTrackingDevice
        self._rollTreshold = rollTreshold
        self._pitchTreshold = pitchTreshold
        self._count = 0
        self._overRollTreshold = False
        self._overPitchTreshold = False
        self._maxRoll = 0
        self._maxPitch = 0

    def stabilize(self):
        self._count += 1
        rollAngle, pitchAngle = self._motionTrackingDevice.get_roll_and_pitch()
        if self._count % 10 == 0:
            print(f"Roll angle: {self._maxRoll}, Pitch angle: {self._maxPitch}")
        if count > 100:
            if abs(rollAngle) > self._maxRoll:
                self._maxRoll = abs(rollAngle)

            if abs(pitchAngle) > self._maxPitch:
                self._maxPitch = abs(pitchAngle)

        # if abs(rollAngle) > self._rollTreshold:
        #     if self._overRollTreshold == False:
        #         print("Roll angle is too high")
        #         self._overRollTreshold = True
        # else:
        #     self._overRollTreshold = False
        # if abs(pitchAngle) > self._pitchTreshold:
        #     if self._overPitchTreshold == False:
        #         print("Pitch angle is too high")
        #         self._overPitchTreshold = True
        # else:
        #     self._overPitchTreshold = False






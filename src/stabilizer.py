from motionTrackingDevice import MotionTrackingDevice

class Stabilizer:
    def __init__(self, motionTrackingDevice: MotionTrackingDevice, rollTreshold: int, pitchTreshold: int):
        self._motionTrackingDevice = motionTrackingDevice
        self._rollTreshold = rollTreshold
        self._pitchTreshold = pitchTreshold
        self._count = 0
        self._overRollTreshold = False
        self._overPitchTreshold = False

    def stabilize(self):
        self._count += 1
        rollAngle, pitchAngle = self._motionTrackingDevice.get_roll_and_pitch()
        if self._count % 10 == 0:
            print(f"Roll angle: {rollAngle}, Pitch angle: {pitchAngle}")
        if abs(rollAngle) > self._rollTreshold:
            if overRollTreshold == False:
                print("Roll angle is too high")
                self._overRollTreshold = True
        else:
            self._overRollTreshold = False
        if abs(pitchAngle) > self._pitchTreshold:
            if overPitchTreshold == False:
                print("Pitch angle is too high")
                self._overPitchTreshold = True
        else:
            self._overPitchTreshold = False






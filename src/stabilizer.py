from motionTrackingDevice import MotionTrackingDevice

class Stabilizer:
    def __init__(self, motionTrackingDevice: MotionTrackingDevice, rollTreshold: int, pitchTreshold: int):
        self._motionTrackingDevice = motionTrackingDevice
        self._rollTreshold = rollTreshold
        self._pitchTreshold = pitchTreshold
        self._count = 0

    def stabilize(self):
        self._count += 1
        rollAngle, pitchAngle = self._motionTrackingDevice.get_roll_and_pitch()

        if abs(rollAngle) > self._rollTreshold:
            print("Roll angle is too high")
        elif abs(pitchAngle) > self._pitchTreshold:
            print("Pitch angle is too high")





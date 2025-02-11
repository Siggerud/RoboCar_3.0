from motionTrackingDevice import MotionTrackingDevice

class Stabilizer:
    def __init__(self, motionTrackingDevice: MotionTrackingDevice):
        self._motionTrackingDevice = motionTrackingDevice
        self._count = 0

    def stabilize(self):
        self._count += 1
        rollAngle, pitchAngle = self._motionTrackingDevice.get_roll_and_pitch()
        if self._count % 50 == 0:
            print(f"Roll angle: {rollAngle}")
            print(f"Pitch angle: {pitchAngle}")




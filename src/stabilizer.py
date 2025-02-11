from motionTrackingDevice import MotionTrackingDevice

class Stabilizer:
    def __init__(self, motionTrackingDevice: MotionTrackingDevice):
        self._motionTrackingDevice = motionTrackingDevice

    def stabilize(self):
        rollAngle, pitchAngle = self._motionTrackingDevice.get_roll_and_pitch()

        print(f"Roll angle: {rollAngle}")
        print(f"Pitch angle: {pitchAngle}")




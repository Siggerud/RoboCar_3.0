from kalmanAngle import KalmanAngle
import smbus
from time import sleep, time
import math

class MPU6050Handler:
    def __init__(self):
        self._kalmanX = KalmanAngle()
        self._kalmanY = KalmanAngle()

        self._restrictPitch = True
        self._radToDeg = 57.2957786
        self._kalAngleX = 0
        self._kalAngleY = 0

        self._bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
        self._deviceAddress = 0x68

        self._PWR_MGMT_1   = 0x6B
        self._SMPLRT_DIV   = 0x19
        self._CONFIG       = 0x1A
        self._GYRO_CONFIG  = 0x1B
        self._INT_ENABLE   = 0x38
        self._ACCEL_XOUT_H = 0x3B
        self._ACCEL_YOUT_H = 0x3D
        self._ACCEL_ZOUT_H = 0x3F
        self._GYRO_XOUT_H  = 0x43
        self._GYRO_YOUT_H  = 0x45
        self._GYRO_ZOUT_H  = 0x47

        # write to sample rate register
        self._bus.write_byte_data(self._deviceAddress, self._SMPLRT_DIV, 7)

        # Write to power management register
        self._bus.write_byte_data(self._deviceAddress, self._PWR_MGMT_1, 1)

        # Write to Configuration register
        # Setting DLPF (last three bit of 0X1A to 6 i.e '110' It removes the noise due to vibration.) https://ulrichbuschbaum.wordpress.com/2015/01/18/using-the-mpu6050s-dlpf/
        self._bus.write_byte_data(self._deviceAddress, self._CONFIG, int('0000110', 2))

        # Write to Gyro configuration register
        self._bus.write_byte_data(self._deviceAddress, self._GYRO_CONFIG, 24)

        # Write to interrupt enable register
        self._bus.write_byte_data(self._deviceAddress, self._INT_ENABLE, 1)

        sleep(1)

        self._accX = 0
        self._accY = 0
        self._accZ = 0

        self._roll = 0
        self._pitch = 0

        self._gyroXAngle = 0
        self._gyroYAngle = 0

        self._timer = time()
        self._flag = 0

    def get_angles(self):
        if (self._flag > 100):  # Problem with the connection
            print("There is a problem with the connection")
            self._flag = 0
        try:
            # Read Accelerometer raw value
            self._accX = self._read_raw_data(self._ACCEL_XOUT_H)
            self._accY = self._read_raw_data(self._ACCEL_YOUT_H)
            self._accZ = self._read_raw_data(self._ACCEL_ZOUT_H)

            # Read Gyroscope raw value
            gyroX = self._read_raw_data(self._GYRO_XOUT_H)
            gyroY = self._read_raw_data(self._GYRO_YOUT_H)

            dt = time() - self._timer
            self._timer = time()

            roll = math.atan2(self._accY, self._accZ) * self._radToDeg
            pitch = math.atan(-self._accX / math.sqrt((self._accY ** 2) + (self._accZ ** 2))) * self._radToDeg

            gyroXRate = gyroX / 131
            gyroYRate = gyroY / 131

            if ((roll < -90 and self._kalAngleX > 90) or (roll > 90 and self._kalAngleX < -90)):
                self._kalmanX.setAngle(roll)
                self._kalAngleX = roll
                self._gyroXAngle = roll
            else:
                self._kalAngleX = self._kalmanX.getAngle(roll, gyroXRate, dt)
            if (abs(self._kalAngleX) > 90):
                gyroYRate = -gyroYRate
                self._kalAngleY = self._kalmanY.getAngle(pitch, gyroYRate, dt)

            if ((pitch < -90 and self._kalAngleY > 90) or (pitch > 90 and self._kalAngleY < -90)):
                self._kalmanY.setAngle(pitch)
                self._kalAngleY = pitch
                self._gyroYAngle = pitch
            else:
                self._kalAngleY = self._kalmanY.getAngle(pitch, gyroYRate, dt)

            if (abs(self._kalAngleY) > 90):
                gyroXRate = -gyroXRate
                self._kalAngleX = self._kalmanX.getAngle(roll, gyroXRate, dt)

            # angle = (rate of change of angle) * change in time
            self._gyroXAngle = gyroXRate * dt
            self._gyroYAngle = gyroYRate * dt

            if ((self._gyroXAngle < -180) or (self._gyroXAngle > 180)):
                self._gyroXAngle = self._kalAngleX
            if ((self._gyroYAngle < -180) or (self._gyroYAngle > 180)):
                self._gyroYAngle = self._kalAngleY

            print("Angle X: " + str(self._kalAngleX) + "   " + "Angle Y: " + str(self._kalAngleY))
            # print(str(roll)+"  "+str(gyroXAngle)+"  "+str(compAngleX)+"  "+str(kalAngleX)+"  "+str(pitch)+"  "+str(gyroYAngle)+"  "+str(compAngleY)+"  "+str(kalAngleY))
            sleep(0.1)

        except Exception as exc:
            self._flag += 1

    def _read_raw_data(self, addr):
        high = self._bus.read_byte_data(self._deviceAddress, addr)
        low = self._bus.read_byte_data(self._deviceAddress, addr + 1)

        value = ((high << 8) | low)

        if value > 32768:
            value = value - 65536
        return value





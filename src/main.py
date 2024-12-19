from carHandling import CarHandling
from camera import Camera
from cameraHelper import CameraHelper
from servoHandling import ServoHandling
from carControl import CarControl, X11ForwardingError
from roboCarHelper import RobocarHelper
from configparser import ConfigParser
import os
from multiprocessing import Array, Value
from audioHandler import AudioHandler, MicrophoneNotConnected
from buzzer import Buzzer

def setup_camera(parser):
    if not parser["Components.enabled"].getboolean("Camera"):
        return None

    cameraSpecs = parser["Camera.specs"]

    resolutionWidth = cameraSpecs.getint("ResolutionWidth")
    resolutionHeight = cameraSpecs.getint("ResolutionHeight")

    resolution = (resolutionWidth, resolutionHeight)
    camera = Camera(resolution)

    return camera

def setup_buzzer(parser) -> Buzzer:
    buzzerPin = parser["buzzer.pin"].getint("Buzzer")

    return Buzzer(buzzerPin)

def setup_servo(parser):
    if not parser["Components.enabled"].getboolean("Servo"):
        return None

    servoDataVertical = parser[f"Servo.handling.specs.horizontal"]

    servoPinHorizontal = servoDataVertical.getint("ServoPin")
    minAngleHorizontal = servoDataVertical.getint("MinAngle")
    maxAngleHorizontal = servoDataVertical.getint("MaxAngle")

    servoPinHorizontal = RobocarHelper.convert_from_board_number_to_bcm_number(servoPinHorizontal)

    servoDataVertical = parser[f"Servo.handling.specs.vertical"]

    servoPinVertical = servoDataVertical.getint("ServoPin")
    minAngleVertical = servoDataVertical.getint("MinAngle")
    maxAngleVertical = servoDataVertical.getint("MaxAngle")

    servoPinVertical = RobocarHelper.convert_from_board_number_to_bcm_number(servoPinVertical)

    servo = ServoHandling(
        (servoPinHorizontal, servoPinVertical),
        (minAngleHorizontal, minAngleVertical),
        (maxAngleHorizontal, maxAngleVertical)
    )

    return servo


def setup_car(parser):
    if not parser["Components.enabled"].getboolean("CarHandling"):
        return None

    carHandlingPins = parser["Car.handling.pins"]

    # define GPIO pins
    rightForward = carHandlingPins.getint("RightForward")
    rightBackward = carHandlingPins.getint("RightBackward")
    leftForward = carHandlingPins.getint("LeftForward")
    leftBackward = carHandlingPins.getint("LeftBackward")
    enA = carHandlingPins.getint("EnA")
    enB = carHandlingPins.getint("EnB")
    minPwmTT = carHandlingPins.getint("MinimumMotorPWM")
    maxPwmTT = carHandlingPins.getint("MaximumMotorPWM")

    # define car handling
    car = CarHandling(
        leftBackward,
        leftForward,
        rightBackward,
        rightForward,
        enA,
        enB,
        minPwmTT,
        maxPwmTT
    )

    return car

# set up parser to read input values
parser = ConfigParser()
parser.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

# setup car
car = setup_car(parser)

# define servos aboard car
servo = setup_servo(parser)

# setup honk
honk = setup_buzzer(parser)

# setup camera
camera = setup_camera(parser)

# add objects to camerahelper
cameraHelper = CameraHelper()
cameraHelper.add_car(car)
cameraHelper.add_servo(servo)

# set up car controller
try:
    carController = CarControl(car, servo, camera, cameraHelper, honk)
except (X11ForwardingError) as e:
    RobocarHelper.print_startup_error(e)
    exit()

# start car
carController.start()

#TODO: set up audioHandler by config file
# initialize audio handler
try:
    exitCommand = "cancel program"
    audioHandler = AudioHandler(carController.get_commands_to_numbers(), exitCommand)
except MicrophoneNotConnected as e:
    RobocarHelper.print_startup_error(e)
    exit()

shared_value = carController.get_shared_value()
shared_flag = carController.get_flag()

# keep process running until keyboard interrupt
try:
    while not shared_flag.value:
        audioHandler.set_audio_command(shared_value, shared_flag)

except KeyboardInterrupt:
    shared_flag.value = True # set event to stop all active processes
finally:
    print("finished!")








from CarHandling import CarHandling
from ArduinoCommunicator import ArduinoCommunicator, InvalidPortError
from camera import Camera
from CameraHelper import CameraHelper
from servoHandling import ServoHandling
from carControl import CarControl, X11ForwardingError
from xboxControl import NoControllerDetected
from roboCarHelper import print_startup_error, convert_from_board_number_to_bcm_number
from time import sleep
from configparser import ConfigParser
import os

def setup_camera(parser):
    if not parser["Components.enabled"].getboolean("Camera"):
        return None

    cameraSpecs = parser["Camera.specs"]

    resolutionWidth = cameraSpecs.getint("ResolutionWidth")
    resolutionHeight = cameraSpecs.getint("ResolutionHeight")

    resolution = (resolutionWidth, resolutionHeight)
    camera = Camera(resolution)

    return camera


def setup_arduino_communicator(parser):
    if not parser["Components.enabled"].getboolean("ArduinoCommunicator"):
        return None

    arduinoCommunicatorData = parser["Arduino.specs"]

    port = arduinoCommunicatorData.get("Port")
    baudrate = arduinoCommunicatorData.getint("Baudrate", 9600)

    try:
        arduinoCommunicator = ArduinoCommunicator(port, baudrate)
    except InvalidPortError as e:
        print_startup_error(e)
        exit()

    buzzerPin = parser["Distance.buzzer.pin"].getint("Buzzer")

    if parser["Components.enabled"].getboolean("DistanceBuzzer"):
        arduinoCommunicator.activate_distance_sensors(buzzerPin)

    if parser["Components.enabled"].getboolean("ProgressiveLights"):
        progressiveLightPins = []
        lightPins = parser["Progressive.light.pins"]
        for key in lightPins:
            progressiveLightPins.append(lightPins.getint(key))

        arduinoCommunicator.activate_photocell_lights(progressiveLightPins)

    return arduinoCommunicator


def setup_servo(parser, plane):
    if plane == "horizontal":
        if not parser["Components.enabled"].getboolean("ServoHorizontal"):
            return None
    elif plane == "vertical":
        if not parser["Components.enabled"].getboolean("ServoVertical"):
            return None

    servoData = parser[f"Servo.handling.specs.{plane}"]

    servoPin = servoData.getint("ServoPin")
    minAngle = servoData.getint("MinAngle")
    maxAngle = servoData.getint("MaxAngle")

    servoPin = servoPin
    servoPin = convert_from_board_number_to_bcm_number(servoPin)

    servo = ServoHandling(
        servoPin,
        plane,
        minAngle,
        maxAngle
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

# set up car controller
try:
    carController = CarControl()
except (X11ForwardingError, NoControllerDetected) as e:
    print_startup_error(e)
    exit()

car = setup_car(parser)

arduinoCommunicator = setup_arduino_communicator(parser)

# define servos aboard car
servoHorizontal = setup_servo(parser, "horizontal")
servoVertical = setup_servo(parser, "vertical")

# setup camera
camera = setup_camera(parser)

# add components
if car:
    carController.add_car(car)
if servoHorizontal:
    carController.add_servo(servoHorizontal)

if servoVertical:
    carController.add_servo(servoVertical)

if arduinoCommunicator:
    carController.add_arduino_communicator(arduinoCommunicator)

if camera:
    cameraHelper = CameraHelper()
    cameraHelper.add_car(car)
    cameraHelper.add_servo(servoHorizontal)

    carController.add_camera(camera)
    carController.add_camera_helper(cameraHelper)

# start car
carController.start()

flag = carController.shared_flag

# keep process running until keyboard interrupt
try:
    while not flag.value:  # listen for any processes setting the event
        sleep(0.5)
except KeyboardInterrupt:
    flag.value = True # set event to stop all active processes
finally:
    print("finished!")








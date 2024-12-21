from carHandling import CarHandling
from camera import Camera
from cameraHelper import CameraHelper
from servoHandling import ServoHandling
from carControl import CarControl, X11ForwardingError
from roboCarHelper import RobocarHelper
from configparser import ConfigParser
import os
from signalLights import SignalLights
from audioHandler import AudioHandler, MicrophoneNotConnected
from buzzer import Buzzer

def setup_signal_lights(parser):
    signalPins = parser["Signal.light.pins"]

    greenLightPin = signalPins.getint("Green")
    yellowLightPin = signalPins.getint("Yellow")
    redLightPin = signalPins.getint("Red")

    return SignalLights(greenLightPin, yellowLightPin, redLightPin)

def setup_camera(parser):
    cameraSpecs = parser["Camera.specs"]

    resolutionWidth = cameraSpecs.getint("ResolutionWidth")
    resolutionHeight = cameraSpecs.getint("ResolutionHeight")

    resolution = (resolutionWidth, resolutionHeight)
    camera = Camera(resolution)

    return camera

def setup_camera_helper(parser):
    cameraCommands = parser["Camera.commands"]
    commands: dict = {
        "turnOnDisplayCommand": cameraCommands["turn_on_display"],
        "turnOffDisplayCommand": cameraCommands["turn_off_display"],
        "zoomCommand": cameraCommands["zoom"]
    }

    cameraSpecs = parser["Camera.specs"]
    maxZoomValue = cameraSpecs.getint("max_zoom_value")

    return CameraHelper(commands, maxZoomValue)


def setup_buzzer(parser) -> Buzzer:
    buzzerPin = parser["Buzzer.pin"].getint("Buzzer")

    return Buzzer(buzzerPin)

def setup_servo(parser):
    servoDataHorizontal = parser["Servo.handling.specs.horizontal"]

    servoPinHorizontal: int = RobocarHelper.convert_from_board_number_to_bcm_number(servoDataHorizontal.getint("ServoPin"))
    minAngleHorizontal: int = servoDataHorizontal.getint("MinAngle")
    maxAngleHorizontal: int = servoDataHorizontal.getint("MaxAngle")

    servoDataHorizontal = parser[f"Servo.handling.specs.vertical"]

    servoPinVertical: int = RobocarHelper.convert_from_board_number_to_bcm_number(servoDataHorizontal.getint("ServoPin"))
    minAngleVertical: int = servoDataHorizontal.getint("MinAngle")
    maxAngleVertical: int = servoDataHorizontal.getint("MaxAngle")

    servoCommands = parser["Servo.commands"]

    basicCommands: dict = {
        "lookUpCommand": servoCommands["look_up"],
        "lookDownCommand": servoCommands["look_down"],
        "lookLeftCommand": servoCommands["look_left"],
        "lookRightCommand": servoCommands["look_right"],
        "lookCenterCommand": servoCommands["look_center"]
    }

    exactAngleCommands: dict = {
        "lookUpExact": servoCommands["look_up_exact"],
        "lookDownExact": servoCommands["look_down_exact"],
        "lookLeftExact": servoCommands["look_left_exact"],
        "lookRightExact": servoCommands["look_right_exact"]
    }

    commands: dict = {
        "basicCommands": basicCommands,
        "exactAngleCommands": exactAngleCommands
    }

    servo = ServoHandling(
        (servoPinHorizontal, servoPinVertical),
        (minAngleHorizontal, minAngleVertical),
        (maxAngleHorizontal, maxAngleVertical),
        commands
    )

    return servo


def setup_car(parser):
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

# setup camerahelper
cameraHelper = setup_camera_helper(parser)

# add objects to camerahelper
cameraHelper.add_car(car)
cameraHelper.add_servo(servo)

# setup signal lights
signalLights = setup_signal_lights(parser)

# set up car controller
try:
    carController = CarControl(car, servo, camera, cameraHelper, honk, signalLights)
except (X11ForwardingError) as e:
    RobocarHelper.print_startup_error(e)
    exit()

# start car
carController.start()

#TODO: set up audioHandler by config file
# initialize audio handler
queue = carController.queue
try:
    exitCommand = "cancel program"
    audioHandler = AudioHandler(exitCommand, queue)
except MicrophoneNotConnected as e:
    RobocarHelper.print_startup_error(e)
    exit()

shared_flag = carController.get_flag()


# keep process running until keyboard interrupt
try:
    while not shared_flag.value:
        audioHandler.set_audio_command(shared_flag)

except KeyboardInterrupt:
    shared_flag.value = True # set event to stop all active processes
finally:
    # allow all processes to finish
    carController.cleanup()
    print("finished!")








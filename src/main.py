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
    signalSpecs = parser["Signal.light.specs"]

    greenLightPin: int = signalSpecs.getint("green_pin")
    yellowLightPin: int = signalSpecs.getint("yellow_pin")
    redLightPin: int = signalSpecs.getint("red_pin")

    blinkTime: float = float(signalSpecs["blink_time"])

    return SignalLights(greenLightPin, yellowLightPin, redLightPin, blinkTime)

def setup_camera(parser):
    cameraSpecs = parser["Camera.specs"]

    resolutionWidth: int = cameraSpecs.getint("ResolutionWidth")
    resolutionHeight: int = cameraSpecs.getint("ResolutionHeight")

    resolution: tuple = (resolutionWidth, resolutionHeight)
    camera = Camera(resolution)

    return camera

def setup_camera_helper(parser, *args):
    cameraCommands = parser["Camera.commands"]
    commands: dict = {
        "turnOnDisplayCommand": cameraCommands["turn_on_display"],
        "turnOffDisplayCommand": cameraCommands["turn_off_display"],
        "zoomCommand": cameraCommands["zoom"]
    }

    cameraSpecs = parser["Camera.specs"]
    maxZoomValue = float(cameraSpecs["max_zoom_value"])

    return CameraHelper(commands, maxZoomValue, *args)


def setup_buzzer(parser) -> Buzzer:
    buzzerSpecs = parser["Buzzer.specs"]
    pin: int = buzzerSpecs.getint("pin")
    defaultHonkTime = float(buzzerSpecs["default_buzz_time"])
    maxHonkTime = float(buzzerSpecs["max_buzz_time"])

    buzzCommands = parser["Buzzer.commands"]
    commands: dict = {
        "buzzCommand": buzzCommands["buzz"],
        "buzzForSpecifiedTimeCommand": buzzCommands["buzz_for_specified_time"]
    }

    return Buzzer(pin, defaultHonkTime, maxHonkTime, commands)

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

def setup_audio_handler(parser):
    audioSpecs = parser["Audio.specs"]
    language: str = audioSpecs["language"]

    exitCommand: str = parser["Global.commands"]["exit"]

    try:
        audioHandler = AudioHandler(exitCommand, language)
    except MicrophoneNotConnected as e:
        RobocarHelper.print_startup_error(e)
        exit()

    return audioHandler

def setup_car(parser):
    carHandlingSpecs = parser["Car.handling.specs"]

    # define GPIO pins
    rightForward: int = carHandlingSpecs.getint("RightForward")
    rightBackward: int = carHandlingSpecs.getint("RightBackward")
    leftForward: int = carHandlingSpecs.getint("LeftForward")
    leftBackward: int = carHandlingSpecs.getint("LeftBackward")
    enA: int = carHandlingSpecs.getint("EnA")
    enB: int = carHandlingSpecs.getint("EnB")

    # define pwm values
    minPwmTT: int = carHandlingSpecs.getint("MinimumMotorPWM")
    maxPwmTT: int = carHandlingSpecs.getint("MaximumMotorPWM")

    speedStep: int = carHandlingSpecs.getint("speed_step")

    # define car commands
    carHandlingCommands = parser["Car.handling.commands"]
    directionCommands: dict = {
        "turnLeftCommand": carHandlingCommands["turn_left"],
        "turnRightCommand": carHandlingCommands["turn_right"],
        "driveCommand": carHandlingCommands["drive"],
        "reverseCommand": carHandlingCommands["reverse"],
        "stopCommand": carHandlingCommands["stop"]
    }

    speedCommands: dict = {
        "increaseSpeedCommand": carHandlingCommands["increase_speed"],
        "decreaseSpeedCommand": carHandlingCommands["decrease_speed"],
        "exactSpeedCommand": carHandlingCommands["exact_speed"]
    }

    commands: dict = {
        "direction": directionCommands,
        "speed": speedCommands
    }

    # define car handling
    car = CarHandling(
        leftBackward,
        leftForward,
        rightBackward,
        rightForward,
        enA,
        enB,
        minPwmTT,
        maxPwmTT,
        speedStep,
        commands
    )

    return car

def setup_car_controller(parser):
    # setup car
    car = setup_car(parser)

    # define servos aboard car
    servo = setup_servo(parser)

    # setup honk
    honk = setup_buzzer(parser)

    # setup camera
    camera = setup_camera(parser)

    # setup camerahelper
    cameraHelper = setup_camera_helper(parser, car, servo)

    # enable objects in camera class
    camera.set_car_enabled()
    camera.set_servo_enabled()
    camera.add_array_dict(cameraHelper.get_array_dict())

    # setup signal lights
    signalLights = setup_signal_lights(parser)

    exitCommand = parser["Global.commands"]["exit"]

    # set up car controller
    try:
        carController = CarControl(car, servo, camera, cameraHelper, honk, signalLights, exitCommand)
    except (X11ForwardingError) as e:
        RobocarHelper.print_startup_error(e)
        exit()

    return carController


# set up parser to read input values
parser = ConfigParser()
parser.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

carController = setup_car_controller(parser)

audioHandler = setup_audio_handler(parser)
audioHandler.setup(carController.get_queue())

# start car
carController.start()

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








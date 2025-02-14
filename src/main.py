from carHandling import CarHandling
from camera import Camera
from cameraHelper import CameraHelper
from cameraServoHandling import CameraServoHandling
from carControl import CarControl, X11ForwardingError
from commandHandler import CommandHandler
from roboCarHelper import RobocarHelper
from configparser import ConfigParser
from servo import Servo
from motorDriver import MotorDriver
from os import path
from signalLights import SignalLights
from audioHandler import AudioHandler, MicrophoneException
from buzzer import Buzzer
from exceptions import OutOfRangeException, InvalidCommandException, InvalidPinException


# TODO: add all exceptions in the same file
def print_error_message_and_exit(errorMessage):
    RobocarHelper.print_startup_error(errorMessage)
    exit()


def setup_signal_lights(parser):
    signalSpecs = parser["Signal.light.specs"]

    try:
        greenLightPin: int = signalSpecs.getint("green_pin")
        yellowLightPin: int = signalSpecs.getint("yellow_pin")
        redLightPin: int = signalSpecs.getint("red_pin")

        blinkTime: float = float(signalSpecs["blink_time"])
    except ValueError as e:
        print_error_message_and_exit(e)

    try:
        signalLights = SignalLights(greenLightPin, yellowLightPin, redLightPin, blinkTime)
    except (OutOfRangeException, InvalidPinException) as e:
        print_error_message_and_exit(e)

    return signalLights


def setup_camera(parser):
    cameraSpecs = parser["Camera.specs"]

    try:
        resolutionWidth: int = cameraSpecs.getint("Resolution_width")
        resolutionHeight: int = cameraSpecs.getint("Resolution_height")
    except ValueError as e:
        print_error_message_and_exit(e)

    resolution: tuple = (resolutionWidth, resolutionHeight)
    camera = Camera(resolution)

    return camera


def setup_camera_helper(parser, *args):
    cameraCommands = parser["Camera.commands"]

    hudCommands: dict = {
        "turnOnDisplayCommand": cameraCommands["turn_on_display"],
        "turnOffDisplayCommand": cameraCommands["turn_off_display"]
    }

    zoomCommands: dict = {
        "zoomExactCommand": cameraCommands["zoom"],
        "zoomInCommand": cameraCommands["zoom_in"],
        "zoomOutCommand": cameraCommands["zoom_out"]
    }

    commands: dict = {
        "hudCommands": hudCommands,
        "zoomCommands": zoomCommands
    }

    cameraSpecs = parser["Camera.specs"]

    try:
        maxZoomValue = float(cameraSpecs["max_zoom_value"])
        zoomIncrement = float(cameraSpecs["zoom_step"])
    except ValueError as e:
        print_error_message_and_exit(e)

    try:
        cameraHelper = CameraHelper(commands, maxZoomValue, zoomIncrement, *args)
    except (OutOfRangeException, InvalidCommandException) as e:
        print_error_message_and_exit(e)

    return cameraHelper


def setup_buzzer(parser) -> Buzzer:
    buzzerSpecs = parser["Buzzer.specs"]

    try:
        pin: int = buzzerSpecs.getint("pin")
        defaultHonkTime: float = buzzerSpecs.getfloat("default_buzz_time")
        maxHonkTime: float = buzzerSpecs.getfloat("max_buzz_time")
    except ValueError as e:
        print_error_message_and_exit(e)

    buzzCommands = parser["Buzzer.commands"]
    commands: dict = {
        "buzzCommand": buzzCommands["buzz"],
        "buzzForSpecifiedTimeCommand": buzzCommands["buzz_for_specified_time"]
    }

    try:
        buzzer = Buzzer(pin, defaultHonkTime, maxHonkTime, commands)
    except (OutOfRangeException, InvalidCommandException, InvalidPinException) as e:
        print_error_message_and_exit(e)

    return buzzer


def setup_servo(parser):
    servoDataHorizontal = parser["Servo.handling.specs.horizontal"]

    try:
        servoPinHorizontal: int = servoDataHorizontal.getint("servo_pin")
        minAngleHorizontal: int = servoDataHorizontal.getint("min_angle")
        maxAngleHorizontal: int = servoDataHorizontal.getint("max_angle")

        servoDataHorizontal = parser[f"Servo.handling.specs.vertical"]

        servoPinVertical: int = servoDataHorizontal.getint("servo_pin")
        minAngleVertical: int = servoDataHorizontal.getint("min_angle")
        maxAngleVertical: int = servoDataHorizontal.getint("max_angle")

    except ValueError as e:
        print_error_message_and_exit(e)

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

    horizontalServo: Servo = Servo(servoPinHorizontal)
    verticalServo: Servo = Servo(servoPinVertical)

    try:
        servo = CameraServoHandling(
            horizontalServo,
            verticalServo,
            [minAngleHorizontal, minAngleVertical],
            [maxAngleHorizontal, maxAngleVertical],
            commands
        )
    except (OutOfRangeException, InvalidCommandException, InvalidPinException) as e:
        print_error_message_and_exit(e)

    return servo


def setup_audio_handler(parser):
    audioSpecs = parser["Audio.specs"]
    language: str = audioSpecs["language"]
    microphoneName: str = audioSpecs["microphone_name"]

    exitCommand: str = parser["Global.commands"]["exit"]

    try:
        audioHandler = AudioHandler(exitCommand, language, microphoneName)
    except MicrophoneException as e:
        print_error_message_and_exit(e)

    return audioHandler


def setup_car(parser):
    carHandlingSpecs = parser["Car.handling.specs"]

    try:
        # define GPIO pins
        rightForward: int = carHandlingSpecs.getint("right_forward")
        rightBackward: int = carHandlingSpecs.getint("right_backward")
        leftForward: int = carHandlingSpecs.getint("left_forward")
        leftBackward: int = carHandlingSpecs.getint("left_backward")
        enA: int = carHandlingSpecs.getint("enA")
        enB: int = carHandlingSpecs.getint("enB")

        # define pwm values
        minPwmTT: int = carHandlingSpecs.getint("minimum_motor_PWM")
        maxPwmTT: int = carHandlingSpecs.getint("maximum_motor_PWM")

        speedStep: int = carHandlingSpecs.getint("speed_step")
    except ValueError as e:
        print_error_message_and_exit(e)

    # define car commands
    carHandlingCommands = parser["Car.handling.commands"]
    directionCommands: dict = {
        "turnLeftCommand": carHandlingCommands["turn_left"],
        "turnRightCommand": carHandlingCommands["turn_right"],
        "driveCommand": carHandlingCommands["drive"],
        "reverseCommand": carHandlingCommands["reverse"],
        "stopCommand": carHandlingCommands["stop"],
        "neutralCommand": carHandlingCommands["neutral"]
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

    motorDriver: MotorDriver = MotorDriver(
        leftBackward,
        leftForward,
        rightBackward,
        rightForward,
        enA,
        enB
    )

    try:
        # define car handling
        car = CarHandling(
            motorDriver,
            minPwmTT,
            maxPwmTT,
            speedStep,
            commands
        )
    except (OutOfRangeException, InvalidCommandException, InvalidPinException) as e:
        print_error_message_and_exit(e)

    return car


def setup_command_handler(parser, camera):
    # setup car
    car = setup_car(parser)

    # define servos aboard car
    servo = setup_servo(parser)

    # setup honk
    honk = setup_buzzer(parser)

    # enable objects in camera class
    camera.set_car_enabled()
    camera.set_servo_enabled()

    # setup camerahelper
    cameraHelper = setup_camera_helper(parser, car, servo)
    cameraHelper.set_array_dict(camera.array_dict)

    # setup signal lights
    signalLights = setup_signal_lights(parser)

    exitCommand = parser["Global.commands"]["exit"]

    # set up command handler
    commandHandler = CommandHandler(car, servo, cameraHelper, honk, signalLights, exitCommand)

    return commandHandler


# set up parser to read input values
parser = ConfigParser()
parser.read(path.join(path.dirname(__file__), 'config.ini'))

# setup camera
camera = setup_camera(parser)

# setup command handler
commandHandler = setup_command_handler(parser, camera)

audioHandler = setup_audio_handler(parser)
audioHandler.setup(commandHandler.queue)

# setup car controller
try:
    carController = CarControl(camera, commandHandler, audioHandler)
except X11ForwardingError as e:
    print_error_message_and_exit(e)

# start car
carController.start()

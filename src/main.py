from carHandling import CarHandling
from camera import Camera
from cameraHelper import CameraHelper
from cameraServoHandling import CameraServoHandling
from carControl import CarControl, X11ForwardingError
from roboCarHelper import RobocarHelper
from configparser import ConfigParser
from os import path
from signalLights import SignalLights
from audioHandler import AudioHandler, MicrophoneException
from buzzer import Buzzer
from stabilizer import Stabilizer, StabilizerException
from exceptions import OutOfRangeException, InvalidCommandException, InvalidPinException

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
        resolutionWidth: int = cameraSpecs.getint("ResolutionWidth")
        resolutionHeight: int = cameraSpecs.getint("ResolutionHeight")
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
        servoPinHorizontal: int = servoDataHorizontal.getint("ServoPin")
        minAngleHorizontal: int = servoDataHorizontal.getint("MinAngle")
        maxAngleHorizontal: int = servoDataHorizontal.getint("MaxAngle")

        servoDataHorizontal = parser[f"Servo.handling.specs.vertical"]

        servoPinVertical: int = servoDataHorizontal.getint("ServoPin")
        minAngleVertical: int = servoDataHorizontal.getint("MinAngle")
        maxAngleVertical: int = servoDataHorizontal.getint("MaxAngle")

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

    try:
        servo = CameraServoHandling(
            [servoPinHorizontal, servoPinVertical],
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
    except ValueError as e:
        print_error_message_and_exit(e)

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

    try:
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
    except (OutOfRangeException, InvalidCommandException, InvalidPinException) as e:
        print_error_message_and_exit(e)

    return car

def setup_stabilizer():
    stabilizerSpecs = parser["Stabilizer"]
    rollAxis: str = stabilizerSpecs["roll_axis"]
    pitchAxis: str = stabilizerSpecs["pitch_axis"]

    try:
        offsetX: float = stabilizerSpecs.getfloat("offset_x")
        offsetY: float = stabilizerSpecs.getfloat("offset_y")
    except ValueError as e:
        print_error_message_and_exit(e)

    offsets: dict[str: float] = {
        "x": offsetX,
        "y": offsetY
    }

    try:
        stabilizer = Stabilizer(rollAxis, pitchAxis, offsets)
    except StabilizerException as e:
        print_error_message_and_exit(e)

    return stabilizer

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

    # setup stabilizer
    stabilizer = setup_stabilizer()

    exitCommand = parser["Global.commands"]["exit"]

    # set up car controller
    try:
        carController = CarControl(car, servo, camera, cameraHelper, honk, signalLights, stabilizer, exitCommand)
    except (X11ForwardingError) as e:
        print_error_message_and_exit(e)

    return carController


# set up parser to read input values
parser = ConfigParser()
parser.read(path.join(path.dirname(__file__), 'config.ini'))

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








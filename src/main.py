from carHandling import CarHandling
from camera import Camera
from cameraHelper import CameraHelper
from servoHandling import ServoHandling
from carControl import CarControl, X11ForwardingError
from roboCarHelper import RobocarHelper
from configparser import ConfigParser
import os
from multiprocessing import Array
from audioHandler import AudioHandler

def setup_camera(parser):
    if not parser["Components.enabled"].getboolean("Camera"):
        return None

    cameraSpecs = parser["Camera.specs"]

    resolutionWidth = cameraSpecs.getint("ResolutionWidth")
    resolutionHeight = cameraSpecs.getint("ResolutionHeight")

    resolution = (resolutionWidth, resolutionHeight)
    camera = Camera(resolution)

    return camera

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

def clean_up_spoken_words(spokenWords):
    if "°" in spokenWords: # change out degree symbol
        # sometimes the ° sign is right next to the number of degrees, so we need to add some space around it
        splitWords = spokenWords.split("°")
        strippedWords = [word.strip() for word in splitWords]
        rejoinedWords = " ° ".join(strippedWords)

        spokenWords = rejoinedWords.replace("°", "degrees")

    print("Text: " + spokenWords)

    return spokenWords.lower().strip()

# set up parser to read input values
parser = ConfigParser()
parser.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

car = setup_car(parser)

# define servos aboard car
servo = setup_servo(parser)

# setup camera
camera = setup_camera(parser)

# add objects to camerahelper
cameraHelper = CameraHelper()
cameraHelper.add_car(car)
cameraHelper.add_servo(servo)

# set up car controller
try:
    carController = CarControl(car, servo, camera, cameraHelper)
except (X11ForwardingError) as e:
    RobocarHelper.print_startup_error(e)
    exit()

shared_array = Array(
    'd', [
        0.0, #speed
        0.0, #turn
        0.0, #horizontal servo
        0.0, #vertical servo
        0.0, #HUD
        1.0 #zoom
    ]
)

shared_value = Array(
    'i', [0, # command
          0 # boolean to signal if a new command has been given
          ]
)
carController.add_voice_value(shared_value)

carController.add_array(shared_array)


# start car
carController.start()

#TODO: set up audioHandler by config file
# initialize audio handler
audioHandler = AudioHandler(carController.get_commands_to_numbers())

flag = carController.shared_flag

# keep process running until keyboard interrupt
try:
    while not flag.value:
        audioHandler.set_audio_command(shared_value)

except KeyboardInterrupt:
    flag.value = True # set event to stop all active processes
finally:
    print("finished!")








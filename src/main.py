from carHandling import CarHandling
from camera import Camera
from cameraHelper import CameraHelper
from servoHandling import ServoHandling
from carControl import CarControl, X11ForwardingError
from xboxControl import NoControllerDetected
from roboCarHelper import print_startup_error, convert_from_board_number_to_bcm_number
from time import sleep
from configparser import ConfigParser
import os
import speech_recognition as sr
import sounddevice # to avoid lots of ALSA error
from multiprocessing import Array, Value

def setup_camera(parser):
    if not parser["Components.enabled"].getboolean("Camera"):
        return None

    cameraSpecs = parser["Camera.specs"]

    resolutionWidth = cameraSpecs.getint("ResolutionWidth")
    resolutionHeight = cameraSpecs.getint("ResolutionHeight")

    resolution = (resolutionWidth, resolutionHeight)
    camera = Camera(resolution)

    return camera


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

if camera:
    cameraHelper = CameraHelper()
    cameraHelper.add_car(car)
    cameraHelper.add_servo(servoHorizontal)

    carController.add_camera(camera)
    carController.add_camera_helper(cameraHelper)

shared_array = Array(
    'd', [
        0.0, #speed
        0.0, #turn
        0.0, # servo
        0.0, #HUD
        1.0 #zoom
    ]
)

shared_value = Array(
    'i', [0, # command
          1 # new command - boolean
          ]
)
carController.add_voice_value(shared_value)

carController.add_array(shared_array)


# start car
carController.start()

flag = carController.shared_flag


# keep process running until keyboard interrupt
try:
    # Initialize recognizer class (for recognizing the speech)
    r = sr.Recognizer()

    listenTime = 3
    while not flag.value:  # listen for any processes setting the event
        spokenWords = ""

        # Reading Microphone as source
        # listening the speech and store in audio_text variable
        with sr.Microphone(device_index=1) as source:
            r.adjust_for_ambient_noise(source)
            while not flag.value:
                # recoginze_() method will throw a request
                # error if the API is unreachable,
                # hence using exception handling

                print("Talk")
                while True:
                    audio_text = r.listen(source, timeout=None, phrase_time_limit=3)
                    try:
                        # using google speech recognition
                        spokenWords = r.recognize_google(audio_text)
                        print("Text: " + spokenWords)
                        break
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition; {e}")
                        break

                try:
                    shared_value[0] = carController.get_commands_to_numbers()[spokenWords.lower().strip()]
                    shared_value[1] = 1 # set 1 to signal that a new command is given
                except KeyError:
                    continue


except KeyboardInterrupt:
    flag.value = True # set event to stop all active processes
finally:
    print("finished!")








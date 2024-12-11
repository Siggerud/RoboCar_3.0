from carHandling import CarHandling
from camera import Camera
from cameraHelper import CameraHelper
from servoHandling import ServoHandling
from carControl import CarControl, X11ForwardingError
from roboCarHelper import print_startup_error, convert_from_board_number_to_bcm_number
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


def setup_servo(parser):
    if not parser["Components.enabled"].getboolean("Servo"):
        return None

    servoDataVertical = parser[f"Servo.handling.specs.horizontal"]

    servoPinHorizontal = servoDataVertical.getint("ServoPin")
    minAngleHorizontal = servoDataVertical.getint("MinAngle")
    maxAngleHorizontal = servoDataVertical.getint("MaxAngle")

    servoPinHorizontal = convert_from_board_number_to_bcm_number(servoPinHorizontal)

    servoDataVertical = parser[f"Servo.handling.specs.vertical"]

    servoPinVertical = servoDataVertical.getint("ServoPin")
    minAngleVertical = servoDataVertical.getint("MinAngle")
    maxAngleVertical = servoDataVertical.getint("MaxAngle")

    servoPinVertical = convert_from_board_number_to_bcm_number(servoPinVertical)

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

# set up car controller
try:
    carController = CarControl()
except (X11ForwardingError) as e:
    print_startup_error(e)
    exit()

car = setup_car(parser)


# define servos aboard car
servo = setup_servo(parser)

# setup camera
camera = setup_camera(parser)

# add components
if car:
    carController.add_car(car)
if servo:
    carController.add_servo(servo)

if camera:
    cameraHelper = CameraHelper()
    cameraHelper.add_car(car)
    #cameraHelper.add_servo(servoHorizontal)

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
    #TODO: make an audio capture class
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
                        break
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition; {e}")
                        break

                spokenWords = clean_up_spoken_words(spokenWords)

                try:
                    shared_value[0] = carController.get_commands_to_numbers()[spokenWords]
                    shared_value[1] = 1 # set 1 to signal that a new command is given
                except KeyError:
                    continue


except KeyboardInterrupt:
    flag.value = True # set event to stop all active processes
finally:
    print("finished!")








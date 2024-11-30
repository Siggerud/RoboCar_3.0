import speech_recognition as sr
from time import sleep
import sounddevice # this is to suppress excessive ALSA and jack logging
#import RPi.GPIO as GPIO


# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()
#r.dynamic_energy_threshold = False
#r.energy_threshold = 200  # Experiment with values between 300 and 1500
listenTime = 3

# setup GPIO pins
#greenLightPin = 36
#redLightPin = 31
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(greenLightPin, GPIO.OUT)
#GPIO.setup(redLightPin, GPIO.OUT)

#GPIO.output(greenLightPin, False)
#GPIO.output(redLightPin, False)

def get_audio():
    # Initialize recognizer class (for recognizing the speech)
    r = sr.Recognizer()
    # r.dynamic_energy_threshold = False
    # r.energy_threshold = 200  # Experiment with values between 300 and 1500
    listenTime = 3
    spokenWords = ""

    try:
        # Reading Microphone as source
        # listening the speech and store in audio_text variable

        with sr.Microphone(device_index=1) as source:
            r.adjust_for_ambient_noise(source)
            while True:
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

                if spokenWords.lower() == "light up green":
                    print("green")
                    #GPIO.output(greenLightPin, True)
                    #GPIO.output(redLightPin, False)
                elif spokenWords.lower() == "light up red":
                    print("red")
                    #GPIO.output(redLightPin, True)
                    #GPIO.output(greenLightPin, False)
                elif spokenWords.lower() == "turn off lights":
                    print("off")
                    #GPIO.output(redLightPin, False)
                    #GPIO.output(greenLightPin, False)
                elif spokenWords.lower() == "turn on lights":
                    print("on")
                    #GPIO.output(redLightPin, True)
                    #GPIO.output(greenLightPin, True)
                elif spokenWords.lower() == "cancel program":
                    break

            sleep(0.5)
    finally:
        print("finished")
        #GPIO.cleanup()


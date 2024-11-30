import speech_recognition as sr
from time import sleep
import sounddevice # this is to suppress excessive ALSA and jack logging

class AudioManager:
    def __init__(self):
        self._listenTime = None #TODO: make this a config variable
        self._deviceIndex = 1 #TODO: make this a config variable
        self._recognizer = sr.Recognizer()
        self._source = None

    def listen_for_command(self):
        with sr.Microphone(device_index=self._deviceIndex) as source:
            self._recognizer.adjust_for_ambient_noise(source)
            audio_text = self._recognizer.listen(source, timeout=None, phrase_time_limit=self._listenTime)
            try:
                # using google speech recognition
                spokenWords: str = self._recognizer.recognize_google(audio_text)
                print("Text: " + spokenWords)
            except sr.UnknownValueError:
                print("Couldn't understand that")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition; {e}")


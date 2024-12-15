import speech_recognition as sr
import sounddevice # to avoid lots of ALSA error

class AudioHandler:
    def __init__(self, commandsToNumbers, deviceIndex):
        self._recognizer = sr.Recognizer()
        self._commandsToNumbers = commandsToNumbers
        self._deviceIndex = deviceIndex #TODO: add this to config

    def set_audio_command(self, shared_value):
        spokenWords = ""

        # Reading Microphone as source
        # listening the speech and store in audio_text variable
        with sr.Microphone(device_index=self._deviceIndex) as source:
            self._recognizer.adjust_for_ambient_noise(source)

            # recoginze_() method will throw a request
            # error if the API is unreachable,
            # hence using exception handling

            print("Talk")
            while True:
                audio_text = self._recognizer.listen(source, timeout=None, phrase_time_limit=3)
                try:
                    # using google speech recognition
                    spokenWords = self._recognizer.recognize_google(audio_text)
                    break
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition; {e}")
                    break

            spokenWords = self._clean_up_spoken_words(spokenWords)

            try:
                shared_value[0] = self._commandsToNumbers[spokenWords]
                shared_value[1] = 1  # set 1 to signal that a new command is given
            except KeyError:
                pass


    def _clean_up_spoken_words(self, spokenWords):
        if "°" in spokenWords:  # change out degree symbol
            # sometimes the ° sign is right next to the number of degrees, so we need to add some space around it
            splitWords = spokenWords.split("°")
            strippedWords = [word.strip() for word in splitWords]
            rejoinedWords = " ° ".join(strippedWords)

            spokenWords = rejoinedWords.replace("°", "degrees")

        print("Text: " + spokenWords)

        return spokenWords.lower().strip()
import speech_recognition as sr
import sounddevice # to avoid lots of ALSA error

class AudioHandler:
    def __init__(self, exitCommand, language):
        self._exitCommand = exitCommand
        self._recognizer = sr.Recognizer()
        self._languageCode = self._get_language_code(language)
        self._deviceIndex = self._get_device_index()
        self._queue = None

    def setup(self, queue):
        self._queue = queue

    def set_audio_command(self, flag):
        spokenWords = ""

        # Reading Microphone as source
        # listening the speech and store in audio_text variable
        with sr.Microphone(device_index=self._deviceIndex) as source:
            self._recognizer.adjust_for_ambient_noise(source)

            print("Talk")
            while True:
                audio_text = self._recognizer.listen(source, timeout=None, phrase_time_limit=3)
                try:
                    # using google speech recognition
                    spokenWords = self._recognizer.recognize_google(audio_text, language=self._languageCode)
                    break
                except sr.UnknownValueError:
                    # if nothing intelligible is picked up, then try again
                    continue
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition; {e}")
                    break

            spokenWords = self._clean_up_spoken_words(spokenWords)

            # set flag value to true if command is exit command
            if spokenWords == self._exitCommand:
                flag.value = True

            # set the command in IPC
            self._queue.put(spokenWords)

    def _clean_up_spoken_words(self, spokenWords):
        if "°" in spokenWords:  # change out degree symbol
            # sometimes the ° sign is right next to the number of degrees, so we need to add some space around it
            splitWords = spokenWords.split("°")
            strippedWords = [word.strip() for word in splitWords]
            rejoinedWords = " ° ".join(strippedWords)

            spokenWords = rejoinedWords.replace("°", "degrees")

        print("Text: " + spokenWords)

        return spokenWords.lower().strip()

    def _get_device_index(self) -> int:
        connectedMicrophones = sr.Microphone.list_microphone_names()
        for index, microphone in enumerate(connectedMicrophones):
            if microphone == "pulse":
                return index

        raise MicrophoneNotConnected("Microphone is not connected")

    def _get_language_code(self, language) -> str:
        languagesToLanguageCodes: dict = {
            "Afrikaans": "af-ZA",
            "Arabic": "ar-SA",
            "Bulgarian": "bg-BG",
            "Catalan": "ca-ES",
            "Czech": "cs-CZ",
            "Danish": "da-DK",
            "German": "de-DE",
            "Greek": "el-GR",
            "English (Australia)": "en-AU",
            "English (Canada)": "en-CA",
            "English (India)": "en-IN",
            "English (New Zealand)": "en-NZ",
            "English (South Africa)": "en-ZA",
            "English (United Kingdom)": "en-GB",
            "English (United States)": "en-US",
            "Norwegian Bokmål(Norway)": "no-NO",
            "Spanish (Argentina)": "es-AR",
            "Spanish (Bolivia)": "es-BO",
            "Spanish (Chile)": "es-CL",
            "Spanish (Colombia)": "es-CO",
            "Spanish (Costa Rica)": "es-CR",
            "Spanish (Ecuador)": "es-EC",
            "Spanish (El Salvador)": "es-SV",
            "Spanish (Spain)": "es-ES",
            "Spanish (United States)": "es-US",
            "Spanish (Guatemala)": "es-GT",
            "Spanish (Honduras)": "es-HN",
            "Spanish (Mexico)": "es-MX",
            "Spanish (Nicaragua)": "es-NI",
            "Spanish (Panama)": "es-PA",
            "Spanish (Paraguay)": "es-PY"
        }

        return languagesToLanguageCodes[language]


class MicrophoneNotConnected(Exception):
    pass

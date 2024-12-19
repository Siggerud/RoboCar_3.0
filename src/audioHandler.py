import speech_recognition as sr
import sounddevice # to avoid lots of ALSA error

class AudioHandler:
    def __init__(self, commandsToNumbers, exitCommand):
        self._commandsToNumbers = commandsToNumbers
        self._exitCommand = exitCommand
        self._recognizer = sr.Recognizer()
        self._deviceIndex = self._get_device_index()

    def set_audio_command(self, shared_value, flag):
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
                    spokenWords = self._recognizer.recognize_google(audio_text)
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
            else:
                # set the command in IPC
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

    def _get_device_index(self) -> int:
        connectedMicrophones = sr.Microphone.list_microphone_names()
        for index, microphone in enumerate(connectedMicrophones):
            if microphone == "pulse":
                return index

        raise MicrophoneNotConnected("Microphone is not connected")

class MicrophoneNotConnected(Exception):
    pass

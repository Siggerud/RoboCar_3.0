import speech_recognition as sr
import sounddevice # import sounddevice to avoid lots of text output from ALSA
import subprocess
from time import sleep

deviceIndex = int(input("Enter the device index: "))
sleepTime = 3
# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()
r.dynamic_energy_threshold = True
r.energy_threshold = 400  # Experiment with values between 300 and 1500

with sr.Microphone(device_index=deviceIndex) as source:
    print(f"Get ready to talk in {sleepTime} seconds...")
    sleep(sleepTime)
    print("Talk")
    audio_text = r.listen(source)
    # Save audio to a file for debugging
    with open("output.wav", "wb") as f:
        f.write(audio_text.get_wav_data())

print(f"Playing back the audio to you in {sleepTime} seconds...")
sleep(sleepTime)
subprocess.run(["aplay", "output.wav", "-q"])
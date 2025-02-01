import speech_recognition as sr
import sounddevice
import subprocess

deviceIndex = int(input("Enter the device index: "))

# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()
r.dynamic_energy_threshold = True
r.energy_threshold = 400  # Experiment with values between 300 and 1500

with sr.Microphone(device_index=deviceIndex) as source:
    print("Talk")
    audio_text = r.listen(source)
    # Save audio to a file for debugging
    with open("output.wav", "wb") as f:
        f.write(audio_text.get_wav_data())

subprocess.run(["aplay", "output.wav"])
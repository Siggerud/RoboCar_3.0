import RPi.GPIO as GPIO
import subprocess
from time import sleep
from configparser import ConfigParser
from os import path

GPIO.setmode(GPIO.BOARD)

# set up parser to read input values
parser = ConfigParser()
parser.read(path.join(path.dirname(__file__), 'config.ini'))

# get pin for start button
try:
    pin = parser["Start.button"].getint("pin")
except ValueError:
    print("Invalid start button pin value")
    exit()

# get repo path
repoPath = parser["Repo.path"]["path"]
if not path.exists(repoPath):
    print("Invalid repo path")
    exit()

GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        print("Waiting for button press...")
        GPIO.wait_for_edge(pin, GPIO.FALLING)
        sleep(0.3) # wait for a little while to avoid double registrations of button press
        subprocess.run(['python', repoPath])

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
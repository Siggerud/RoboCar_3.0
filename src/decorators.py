import functools
import RPi.GPIO as GPIO

def GPIOProcess(func):
    @functools.wraps(func)
    def wrapper_GPIOProcess(*args, **kwargs):
        GPIO.setmode(GPIO.BOARD)
        func(*args, **kwargs)
        GPIO.cleanup()
        return func(*args, **kwargs)
    return wrapper_GPIOProcess
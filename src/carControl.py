import subprocess
from multiprocessing import Process, Array, Value
import RPi.GPIO as GPIO
from time import sleep

class CarControl:
    def __init__(self, camera, commandHandler):
        self._check_if_X11_connected()

        self._camera = camera
        self._commandHandler = commandHandler

        self._processes: list = []

        self.shared_array = self._get_shared_array(self._camera.get_array_dict())

        self.shared_flag = Value('b', False)

    def get_flag(self) -> Value:
        return self.shared_flag

    def start(self) -> None:
        # start processes
        self._activate_camera()
        self._activate_voice_command_handling()

    def cleanup(self) -> None:
        # close all processes
        for process in self._processes:
            process.join()

    def _get_shared_array(self, shared_array_dict) -> Array:
        # initialize the array list with the same size as the dict that corresponds to the array
        arrayList: list = [0.0] * len(shared_array_dict.keys())

        # zoom and hud should be initialized to 1.0
        arrayList[shared_array_dict["HUD"]] = 1.0
        arrayList[shared_array_dict["Zoom"]] = 1.0

        return Array('d', arrayList)

    def _activate_camera(self) -> None:
        process = Process(target=self._start_camera, args=(self.shared_array, self.shared_flag))
        self._processes.append(process)
        process.start()

    def _activate_voice_command_handling(self) -> None:
        process = Process(
            target=self._GPIO_Process,
            args=(self._start_listening_for_voice_commands, self.shared_flag, self.shared_array)
        )
        self._processes.append(process)
        process.start()

    def _GPIO_Process(self, func, *args) -> None:
        GPIO.setmode(GPIO.BOARD) # set GPIO mode as BOARD for all classes using GPIO pins
        GPIO.setwarnings(False) # disable GPIO warnings
        func(*args) # call parameter method
        GPIO.cleanup() # cleanup all classes using GPIO pins

    def _start_listening_for_voice_commands(self, flag, shared_array) -> None:
        self._commandHandler.print_start_up_message()
        try:
            self._commandHandler.execute_commands(flag, shared_array)
        except KeyboardInterrupt:
            flag.value = True
        finally:
            self._commandHandler.cleanup()

    def _start_camera(self, shared_array, flag) -> None:
        try:
            self._camera.show_camera_feed(flag, shared_array)
        except KeyboardInterrupt:
            flag.value = True
        finally:
            self._camera.cleanup()

    def _check_if_X11_connected(self) -> None:
        treshold: int = 5
        numOfTries: int = 0
        sleepTime: int = 5
        try:
            while numOfTries < treshold:
                result = subprocess.run(["xset", "q"], capture_output=True, text=True)
                returnCode: int = result.returncode
                numOfTries += 1
                if not returnCode:
                    print("Succesful connection to forwarded X11 server\n")
                    return
                else:
                    print(f"Failed to connect to X11 server. Trying again in {sleepTime} seconds...\n"
                          f"Number of retries: {treshold - numOfTries}\n")
                    sleep(sleepTime)
        except KeyboardInterrupt:
            raise X11ForwardingError("User aborted connecting to forwarded X11 server")

        raise X11ForwardingError("X11 forwarding not detected.")


class X11ForwardingError(Exception):
    pass


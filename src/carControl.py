import subprocess
from multiprocessing import Process, Array, Value, Queue
import RPi.GPIO as GPIO

class CarControl:
    def __init__(self, car, servo, camera, cameraHelper, honk, signalLights, exitCommand):
        if not self._check_if_X11_connected():
            raise X11ForwardingError("X11 forwarding not detected.")

        self._car = car
        self._servo = servo
        self._camera = camera
        self._cameraHelper = cameraHelper
        self._honk = honk
        self._signalLights = signalLights

        self._processes: list = []
        self._exitCommand: str = exitCommand

        self._commandToObjects: dict[str: object] = self._get_all_objects_mapped_to_commands()

        self._commandValidityToSignalColor: dict = {
            "valid": "green",
            "partially valid": "yellow",
            "invalid": "red"
        }

        self.shared_array = Array(
            'd', [
                0.0, #speed
                0.0, #direction
                0.0, #horizontal servo
                0.0, #vertical servo
                1.0, #HUD
                1.0 #zoom
            ]
        )

        self.shared_flag = Value('b', False)
        self._queue = Queue()

    def get_flag(self) -> Value:
        return self.shared_flag

    def get_queue(self) -> Queue:
        return self._queue

    def start(self):
        # TODO: print commands
        self._car.print_commands()

        # TODO: make this dependent on what is enabled in camerahelper class
        self._get_camera_ready() # this needs to be first method called
        self._activate_camera()

        self._activate_voice_command_handling()

    def cleanup(self):
        # close all threads
        for process in self._processes:
            process.join()

    def _get_camera_ready(self):
        self._set_shared_array_dict()

        if self._car:
            self._camera.set_car_enabled()

        if self._servo:
            self._camera.set_servo_enabled()

    def _set_shared_array_dict(self):
        arrayDict: dict = {}
        cameraInputs: list = ["speed", "direction", "horizontal servo", "vertical servo", "HUD", "Zoom"]
        for index, cameraInput in enumerate(cameraInputs):
            arrayDict[cameraInput] = index

        self._camera.add_array_dict(arrayDict)
        self._cameraHelper.add_array_dict(arrayDict)

    def _activate_camera(self):
        process = Process(target=self._start_camera, args=(self.shared_array, self.shared_flag))
        self._processes.append(process)
        process.start()

    def _activate_voice_command_handling(self):
        process = Process(
            target=self._GPIO_Process,
            args=(self._start_listening_for_voice_commands, self.shared_flag)
        )
        self._processes.append(process)
        process.start()

    def _GPIO_Process(self, func, *args):
        GPIO.setmode(GPIO.BOARD) # set GPIO mode as BOARD for all classes using GPIO pins
        GPIO.setwarnings(False) # disable GPIO warnings
        func(*args) # call parameter method
        GPIO.cleanup() # cleanup all classes using GPIO pins

    def _start_listening_for_voice_commands(self, flag):
        # setup objects
        self._car.setup()
        self._servo.setup()
        self._honk.setup()
        self._signalLights.setup()

        while not flag.value:
            command: str = self._queue.get()

            if command == self._exitCommand:
                break

            try:
                commandValidity: str = self._commandToObjects[command].get_command_validity(command)
            except KeyError:
                commandValidity: str = "invalid"

            # signal if the command was valid, partially valid or invalid
            signalColor = self._commandValidityToSignalColor[commandValidity]
            self._signalLights.blink(signalColor)

            # execute command if it is valid
            if commandValidity == "valid":
                self._commandToObjects[command].handle_voice_command(command)
                self._cameraHelper.update_control_values_for_video_feed(self.shared_array)

        # cleanup objects
        self._servo.cleanup()
        self._car.cleanup()
        self._signalLights.cleanup()

    def _start_camera(self, shared_array, flag):
        self._camera.setup()

        while not flag.value:
            self._camera.show_camera_feed(shared_array)

        self._camera.cleanup()

    def _get_all_objects_mapped_to_commands(self) -> dict:
        objectsToCommands: dict = {}

        #TODO: loop through list of objects instead

        # add car commands
        objectsToCommands.update(self._add_object_to_commands(self._car))

        # add servo commands
        objectsToCommands.update(self._add_object_to_commands(self._servo))

        # add camera commands
        objectsToCommands.update(self._add_object_to_commands(self._cameraHelper))

        # add honk commands
        objectsToCommands.update(self._add_object_to_commands(self._honk))

        return objectsToCommands

    def _add_object_to_commands(self, roboObject) -> dict:
        objectToCommands: dict = {}
        for command in roboObject.get_voice_commands():
            objectToCommands[command] = roboObject

        return objectToCommands

    def _check_if_X11_connected(self):
        result = subprocess.run(["xset", "q"], capture_output=True, text=True)
        returnCode = result.returncode

        if not returnCode:
            print("Succesful connection to forwarded X11 server\n")

        return not returnCode


class X11ForwardingError(Exception):
    pass


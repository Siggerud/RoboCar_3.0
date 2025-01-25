import subprocess
from multiprocessing import Process, Array, Value, Queue
import RPi.GPIO as GPIO
from stabilizer import Stabilizer

class CarControl:
    def __init__(self, car, servo, camera, cameraHelper, honk, signalLights, exitCommand):
        if not self._check_if_X11_connected():
            raise X11ForwardingError("X11 forwarding not detected.")

        self._car = car
        self._servo = servo
        self._cameraHelper = cameraHelper
        self._honk = honk
        self._roboObjects: list = [
            self._car,
            self._servo,
            self._cameraHelper,
            self._honk
        ]

        #TODO: move this to main and add to config file
        self._stabilizer = Stabilizer()

        self._camera = camera
        self._signalLights = signalLights

        self._processes: list = []
        self._exitCommand: str = exitCommand

        self._commandToObjects: dict[str: object] = self._get_all_objects_mapped_to_commands()

        self._commandValidityToSignalColor: dict = {
            "valid": "green",
            "partially valid": "yellow",
            "invalid": "red"
        }

        self.shared_array = self._get_shared_array(self._cameraHelper.get_array_dict())

        self.shared_flag = Value('b', False)
        self._queue = Queue()

    def get_flag(self) -> Value:
        return self.shared_flag

    def get_queue(self) -> Queue:
        return self._queue

    def start(self) -> None:
        self._print_start_up_message()

        self._get_camera_ready() # this needs to be first method called
        self._activate_camera()

        self._activate_voice_command_handling()

    def cleanup(self) -> None:
        # close all threads
        for process in self._processes:
            process.join()

    def _get_camera_ready(self) -> None:
        self._set_shared_array_dict()

    def _get_shared_array(self, shared_array_dict) -> Array:
        # initialize the array list with the same size as the dict that corresponds to the array
        arrayList: list = [0.0] * len(shared_array_dict.keys())

        # zoom and hud should be initialized to 1.0
        arrayList[shared_array_dict["HUD"]] = 1.0
        arrayList[shared_array_dict["Zoom"]] = 1.0

        return Array('d', arrayList)

    def _print_start_up_message(self) -> None:
        for roboObject in self._roboObjects:
            roboObject.print_commands()

        print(f"Exit command : {self._exitCommand}")
        print()

    def _set_shared_array_dict(self) -> None:
        arrayDict: dict = {}
        cameraInputs: list = ["speed", "direction", "horizontal servo", "vertical servo", "HUD", "Zoom"]
        for index, cameraInput in enumerate(cameraInputs):
            arrayDict[cameraInput] = index

    def _activate_camera(self) -> None:
        process = Process(target=self._start_camera, args=(self.shared_array, self.shared_flag))
        self._processes.append(process)
        process.start()

    def _start_car_stabilization(self, flag) -> None:
        process = Process(
            target=self._stabilize_car,
            args=(self.shared_flag, )
        )
        self._processes.append(process)
        process.start()

    def _activate_voice_command_handling(self) -> None:
        process = Process(
            target=self._GPIO_Process,
            args=(self._start_listening_for_voice_commands, self.shared_flag)
        )
        self._processes.append(process)
        process.start()

    def _GPIO_Process(self, func, *args) -> None:
        GPIO.setmode(GPIO.BOARD) # set GPIO mode as BOARD for all classes using GPIO pins
        GPIO.setwarnings(False) # disable GPIO warnings
        func(*args) # call parameter method
        GPIO.cleanup() # cleanup all classes using GPIO pins

    def _stabilize_car(self, flag) -> None:
        while not flag.value:
            self._stabilizer.stabilize()

    def _start_listening_for_voice_commands(self, flag) -> None:
        # setup objects
        for roboObject in self._roboObjects:
            roboObject.setup()

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
        for roboObject in self._roboObjects:
            roboObject.cleanup()

    def _start_camera(self, shared_array, flag) -> None:
        self._camera.setup()

        while not flag.value:
            self._camera.show_camera_feed(shared_array)

        self._camera.cleanup()

    def _get_all_objects_mapped_to_commands(self) -> dict:
        objectsToCommands: dict = {}

        # add commands from all robot objects
        for roboObject in self._roboObjects:
            objectsToCommands.update(self._add_object_to_commands(roboObject))

        return objectsToCommands

    def _add_object_to_commands(self, roboObject) -> dict:
        objectToCommands: dict = {}
        for command in roboObject.get_voice_commands():
            objectToCommands[command] = roboObject

        return objectToCommands

    def _check_if_X11_connected(self) -> int:
        result = subprocess.run(["xset", "q"], capture_output=True, text=True)
        returnCode = result.returncode

        if not returnCode:
            print("Succesful connection to forwarded X11 server\n")

        return not returnCode


class X11ForwardingError(Exception):
    pass


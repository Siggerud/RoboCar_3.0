import subprocess
from multiprocessing import Process, Array, Value, Queue
from time import sleep
import RPi.GPIO as GPIO

class CarControl:
    def __init__(self, car, servo, camera, cameraHelper, honk):
        if not self._check_if_X11_connected():
            raise X11ForwardingError("X11 forwarding not detected.")

        self._car = car
        self._servo = servo

        self._camera = camera
        self._cameraHelper = cameraHelper
        self._honk = honk

        self._processes = []
        self._exitCommand = "cancel program" #TODO: make this a variable that is read from config for both audio and carcontroller class

        self._commandToObjects: dict[str: object] = self._get_all_objects_mapped_to_commands()
        self._commands_to_numbers: dict[str: int] = self._get_commands_to_numbers()
        self._numbers_to_commands: dict[int: str] = self._get_numbers_to_commands()

        self.shared_array = Array(
            'd', [
                0.0, #speed
                0.0, #turn
                0.0, #horizontal servo
                0.0, #vertical servo
                0.0, #HUD
                1.0 #zoom
            ]
        )
        self._shared_value = Array(
            'i', [0, # command
                  0 # boolean to signal if a new command has been given
                  ]
        )
        self.shared_flag = Value('b', False)
        self.queue = Queue()

    def get_shared_value(self) -> Array:
        return self._shared_value

    def get_flag(self) -> Value:
        return self.shared_flag

    def get_commands_to_numbers(self) -> dict[str: int]:
        return self._commands_to_numbers

    def start(self):
        # TODO: print commands

        # TODO: make this dependent on what is enabled in camerahelper class
        if self._camera:
            self._get_camera_ready() # this needs to be first method called

            self._activate_camera()

        self._activate_voice_command_handling()

    def cleanup(self):
        # close all threads
        for process in self._processes:
            process.join()

    def _get_camera_ready(self):
        self._set_shared_array_and_array_dict()

        if self._car:
            self._camera.set_car_enabled()

        if self._servo:
            self._camera.set_servo_enabled()

    def _set_shared_array_and_array_dict(self):
        arrayDict: dict = {}
        cameraInputs: list = ["speed", "turn", "horizontal servo", "vertical servo", "HUD", "Zoom"]
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
            args=(self._start_listening_for_voice_commands, self._shared_value, self.shared_flag)
        )
        self._processes.append(process)
        process.start()

    def _get_commands_to_numbers(self) -> dict:
        commandsToNumbers: dict = {}

        # add commands from all objects
        for index, command in enumerate(list(self._commandToObjects.keys())):
            commandsToNumbers[command] = index

        return commandsToNumbers

    def _get_numbers_to_commands(self) -> dict:
        numbersToCommands: dict = {num: command for command, num in self._commands_to_numbers.items()}

        return numbersToCommands

    def _GPIO_Process(self, func, *args):
        GPIO.setmode(GPIO.BOARD)
        func(*args)
        GPIO.cleanup()

    def _start_listening_for_voice_commands(self, shared_value, flag):
        # setup objects
        self._car.setup()
        self._servo.setup()
        self._honk.setup()

        while not flag.value:
            #newCommand = bool(shared_value[1]) # check if there's a new command
            #if newCommand:
            #command: str = self._get_voice_command(self._shared_value[0])
            command = self.queue.get()

            if command == self._exitCommand:
                break

            self._commandToObjects[command].handle_voice_command(command)
            #self._shared_value[1] = 0 # signal that command is read

            self._cameraHelper.update_control_values_for_video_feed(self.shared_array)

            sleep(0.5)

        # cleanup objects
        self._servo.cleanup()
        self._car.cleanup()

    def _get_voice_command(self, num: int) -> str:
        return self._numbers_to_commands[num]

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

    """
    def _exit_program(self, flag):
        flag.value = True
        print("Exiting program...")
    """
    def _check_if_X11_connected(self):
        result = subprocess.run(["xset", "q"], capture_output=True, text=True)
        returnCode = result.returncode

        if not returnCode:
            print("Succesful connection to forwarded X11 server")

        return not returnCode


class X11ForwardingError(Exception):
    pass


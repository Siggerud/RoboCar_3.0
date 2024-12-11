import subprocess
from multiprocessing import Process, Value
from time import sleep

class CarControl:
    def __init__(self, car, servo, camera, cameraHelper):
        if not self._check_if_X11_connected():
            raise X11ForwardingError("X11 forwarding not detected.")

        self._car = car
        self._servo = servo

        self._camera = camera
        self._cameraHelper = cameraHelper

        self._processes = []

        self._exitCommand: str = "cancel program"  # TODO: make this an input to the class

        self._commandToObjects: dict[str: object] = self._get_all_objects_mapped_to_commands()
        self._commands_to_numbers: dict[str: int] = self._get_commands_to_numbers()
        self._numbers_to_commands: dict[int: str] = self._get_numbers_to_commands()

        self.shared_array = None
        self._shared_value = None
        self.shared_flag = Value('b', False)

    def add_array(self, array):
        self.shared_array = array

    def get_commands_to_numbers(self) -> dict[str: int]:
        return self._commands_to_numbers

    def start(self):
        # TODO: print commands

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
        #arrayInput = []
        arrayDict = {}
        counter = 0
        if self._car:
            arrayDict["speed"] = counter
            #arrayInput.append(0.0)
            counter += 1

            arrayDict["turn"] = counter
            #arrayInput.append(0.0)
            counter += 1

        if self._servo:
            arrayDict["servo"] = counter
            #arrayInput.append(0.0)
            counter += 1

        arrayDict["HUD"] = counter
        #arrayInput.append(0.0)
        counter += 1

        arrayDict["Zoom"] = counter
        #arrayInput.append(1.0)

        #self.shared_array = Array('d', arrayInput)

        self._camera.add_array_dict(arrayDict)
        self._cameraHelper.add_array_dict(arrayDict)

    def _activate_camera(self):
        process = Process(target=self._start_camera, args=(self.shared_array, self.shared_flag))
        self._processes.append(process)
        process.start()

    def _activate_voice_command_handling(self):
        process = Process(
            target=self._start_listening_for_voice_commands,
            args=(self._shared_value, self.shared_flag)
        )
        self._processes.append(process)
        process.start()

    def _get_commands_to_numbers(self) -> dict:
        commandsToNumbers: dict = {}

        # add commands from all objects
        for index, command in enumerate(list(self._commandToObjects.keys())):
            commandsToNumbers[command] = index

        # add exit command to dictionary
        commandsToNumbers[self._exitCommand] = index + 1

        return commandsToNumbers

    def _get_numbers_to_commands(self) -> dict:
        numbersToCommands: dict = {num: command for command, num in self._commands_to_numbers.items()}

        return numbersToCommands

    def _start_listening_for_voice_commands(self, shared_value, flag):
        # setup objects
        self._car.setup()
        self._servo.setup()

        while not flag.value:
            newCommand = bool(shared_value[1]) # check if there's a new command
            if newCommand:
                command: str = self._get_voice_command(self._shared_value[0])
                if command == self._exitCommand:
                    self._exit_program(flag)
                    break

                self._commandToObjects[command].handle_voice_command(command)
                self._shared_value[1] = 0 # signal that command is read

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

        # add car commands
        objectsToCommands.update(self._add_object_to_commands(self._car.get_car_commands(), self._car))

        # add servo commands
        objectsToCommands.update(self._add_object_to_commands(self._servo.get_servo_commands(), self._servo))

        # add camera commands
        objectsToCommands.update(self._add_object_to_commands(self._cameraHelper.get_camera_commands(), self._cameraHelper))

        return objectsToCommands

    def _add_object_to_commands(self, commands: list[str], roboObject: object) -> dict:
        objectToCommands: dict = {}
        for command in commands:
            objectToCommands[command] = roboObject

        return objectToCommands

    def _exit_program(self, flag):
        flag.value = True
        print("Exiting program...")

    def _check_if_X11_connected(self):
        result = subprocess.run(["xset", "q"], capture_output=True, text=True)
        returnCode = result.returncode

        if not returnCode:
            print("Succesful connection to forwarded X11 server")

        return not returnCode

    def add_voice_value(self, _shared_value):
        self._shared_value = _shared_value


class X11ForwardingError(Exception):
    pass


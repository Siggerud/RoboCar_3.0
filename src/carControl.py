import subprocess
from multiprocessing import Process, Value
from xboxControl import XboxControl
from time import sleep

class CarControl:
    def __init__(self):
        if not self._check_if_X11_connected():
            raise X11ForwardingError("X11 forwarding not detected.")

        self._xboxControl = XboxControl()

        self._car = None
        self._servoEnabled = False
        #self._servos = []
        self._servo = None
        self._arduinoCommunicator = None

        self._camera = None
        self._cameraHelper = None

        self._processes = []

        self._buttonToObjectDict = {
        }

        self._commandToObjects: dict[str: object] = {}
        self._commands_to_numbers: dict[str: int] = {}
        self._numbers_to_commands: dict[int: str] = {}
        self._exitCommand: str = "cancel program" #TODO: make this an input to the class

        self.shared_array = None
        self._shared_value = None
        self.shared_flag = Value('b', False)

    def add_arduino_communicator(self, arduinoCommunicator):
        self._arduinoCommunicator = arduinoCommunicator

    def add_car(self, car):
        self._car = car

    def add_camera(self, camera):
        self._camera = camera

    def add_camera_helper(self, cameraHelper):
        self._cameraHelper = cameraHelper

    def add_servo(self, servo):
        self._servo = servo

    def add_array(self, array):
        self.shared_array = array

    def get_commands_to_numbers(self) -> dict[str: int]:
        return self._commands_to_numbers

    def start(self):
        # TODO: print commands
        self._map_all_objects_to_commands() #TODO: move to init method
        self._populate_commands_to_numbers() #TODO: move to init method
        self._populate_numbers_to_commands() #TODO: move to init method

        if self._camera:
            self._get_camera_ready() # this needs to be first method called

            self._activate_camera()

        #self._activate_car_handling()
        self._activate_voice_command_handling()

    def cleanup(self):
        # close all threads
        for process in self._processes:
            process.join()

    def _get_camera_ready(self):
        self._set_shared_array_and_array_dict()

        if self._car:
            self._camera.set_car_enabled()

        if self._servoEnabled:
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

        if self._servoEnabled:
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

    def _activate_car_handling(self):
        process = Process(target=self._start_listening_for_xbox_commands, args=(self.shared_array, self.shared_flag))
        self._processes.append(process)
        process.start()

    def _activate_voice_command_handling(self):
        process = Process(
            target=self._start_listening_for_voice_commands,
            args=(self._shared_value, self.shared_flag)
        )
        self._processes.append(process)
        process.start()

    def _populate_commands_to_numbers(self):
        # add commands from all objects
        for index, command in enumerate(list(self._commandToObjects.keys())):
            self._commands_to_numbers[command] = index

        # add exit command to dictionary
        self._commands_to_numbers[self._exitCommand] = index + 1

    def _populate_numbers_to_commands(self):
        self._numbers_to_commands = {num: command for command, num in self._commands_to_numbers.items()}

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

            sleep(0.5)

            #self._cameraHelper.update_control_values_for_video_feed(shared_array)

        # cleanup objects
        self._servo.cleanup()
        self._car.cleanup()

    def _get_voice_command(self, num: int) -> str:
        return self._numbers_to_commands[num]

    def _start_listening_for_xbox_commands(self, shared_array, flag):
        self._print_button_explanation()
        self._map_all_objects_to_buttons()

        if self._car:
            self._car.setup()

        if self._servoEnabled:
            for servo in self._servos:
                servo.setup()

        while not flag.value:
            for event in self._xboxControl.get_controller_events():
                button, pressValue = self._xboxControl.get_button_and_press_value_from_event(event)
                if self._xboxControl.check_for_exit_event(button):
                    self._exit_program(flag)
                    break

                # get the object to take action based on the button pushed
                try:
                    self._buttonToObjectDict[button].handle_xbox_input(button, pressValue)
                except KeyError: # if key does not correspond to object, then go to next event
                    continue

                if self._cameraHelper:
                    self._cameraHelper.update_control_values_for_video_feed(shared_array)

            # sleep between event handlings to not overload cpu, sleep value is derived from experiments
            sleep(0.002)

        if self._car:
            self._car.cleanup()

        if self._servoEnabled:
            for servo in self._servos:
                servo.cleanup()

        self._xboxControl.cleanup()

        print("Exiting car handling")


    def _start_camera(self, shared_array, flag):
        self._camera.setup()

        while not flag.value:
            self._camera.show_camera_feed(shared_array)

        self._camera.cleanup()

    def _start_listening_for_arduino_communication(self, flag):
        self._arduinoCommunicator.setup()

        while not flag.value:
            # start the communicator
            self._arduinoCommunicator.start()
            sleep(0.01)  # sleep too not use too much CPU resources

        # cleanup when flag is set to true
        self._arduinoCommunicator.cleanup()
        print("Exiting arduino")

    def _print_button_explanation(self):
        print()
        print("Controller layout: ")
        if self._car:
            print("Car controls:")
            print("Turn left: " + self._car.get_car_buttons()["Left"])
            print("Turn right: " + self._car.get_car_buttons()["Right"])
            print("Drive forward: " + self._car.get_car_buttons()["Gas"])
            print("Reverse: " + self._car.get_car_buttons()["Reverse"])
            print()
        if self._servoEnabled:
            print("Servo controls:")
            for servo in self._servos:
                print("Turn servo" + servo.get_plane() + ": " + servo.get_servo_buttons()["Servo"])
            print()
        if self._camera:
            print("Camera controls")
            print("Zoom camera: " + self._cameraHelper.get_camera_buttons()["Zoom"])
            print("Turn HUD on or off: " + self._cameraHelper.get_camera_buttons()["HUD"])
            print()

        print(f"Double tap {self._xboxControl.get_exit_button()} to exit")

    def _map_all_objects_to_commands(self):

        self._add_object_to_commands(self._car.get_car_commands(), self._car)

        self._add_object_to_commands(self._servo.get_servo_commands(), self._servo)

        self._add_object_to_commands(self._cameraHelper.get_camera_commands(), self._cameraHelper)

    def _map_all_objects_to_buttons(self):
        if self._car:
            self._add_object_to_buttons(self._car.get_car_buttons(), self._car)

        if self._servoEnabled:
            for servo in self._servos:
                self._add_object_to_buttons(servo.get_servo_buttons(), servo)

        if self._cameraHelper:
            self._add_object_to_buttons(self._cameraHelper.get_camera_buttons(), self._cameraHelper)

    def _add_object_to_commands(self, commands, roboObject):
        for command in commands:
            self._commandToObjects[command] = roboObject

    def _add_object_to_buttons(self, buttonDict, roboObject):
        for button in list(buttonDict.values()):
            self._buttonToObjectDict[button] = roboObject

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


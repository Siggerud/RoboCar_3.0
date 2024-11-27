import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message
import pygame
from time import time

class XboxControl:
    def __init__(self):
        self._controller = self._set_controller()

        self._hatNum = 0

        self._joyHatMotionToButtons = {
            -1: "D-PAD left",
            1: "D-PAD right",
        }

        self._dpad_button_states = self._create_button_state_dict(self._joyHatMotionToButtons)

        self._joyAxisMotionToButtons = {
            0: "LSB horizontal",
            1: "LSB vertical",
            2: "RSB horizontal",
            3: "RSB vertical",
            4: "RT",
            5: "LT",
        }

        self._pushButtons = {
            0: "A",
            1: "B",
            3: "X",
            4: "Y",
            6: "LB",
            7: "RB",
            11: "Start",
            15: "Back"
        }

        self._pushButtonsStates = self._create_button_state_dict(self._pushButtons)
        self._eventTypeToButtonStates = {
            pygame.JOYBUTTONUP: 0,
            pygame.JOYBUTTONDOWN: 1
        }

        self._exitButton = "Start"
        self._exitButtonLastPush = None # keeps track of last time exit button was pushed

    def get_controller_events(self):
        return pygame.event.get()

    def get_button_and_press_value_from_event(self, event):
        button = None
        buttonPressValue = None

        eventType = event.type
        if eventType == pygame.JOYHATMOTION:
            button = self._get_dpad_button(self._controller.get_hat(self._hatNum)[0])
            buttonPressValue = self._dpad_button_states[button]
        elif eventType == pygame.JOYAXISMOTION:
            axis = event.axis
            button = self._joyAxisMotionToButtons[axis]
            buttonPressValue = event.value
        elif eventType == pygame.JOYBUTTONDOWN or eventType == pygame.JOYBUTTONUP:
            button = self._get_pushed_button(event)
            buttonPressValue = self._pushButtonsStates[button]

        return button, buttonPressValue

    def check_for_exit_event(self, button):
        if button == self._exitButton:
            # check if exit button has been pushed
            if self._pushButtonsStates[self._exitButton] == 1:

                # check how long ago it was pushed
                if self._exitButtonLastPush:
                    if (time() - self._exitButtonLastPush) < 0.5:
                        return True
                    else:
                        self._exitButtonLastPush = time()
                else:
                    self._exitButtonLastPush = time()

        return False

    def get_exit_button(self):
        return self._exitButton

    def cleanup(self):
        pygame.quit()

    def _get_dpad_button(self, num):
        try:
            button = self._joyHatMotionToButtons[num]
            self._dpad_button_states[button] = 1
        except KeyError:
            for button in list(self._joyHatMotionToButtons.values()):
                if self._dpad_button_states[button] == 1:
                    self._dpad_button_states[button] = 0
                    break

        return button

    def _get_pushed_button(self, event):
        buttonNum = event.button
        button = self._pushButtons[buttonNum]
        self._pushButtonsStates[button] = self._eventTypeToButtonStates[event.type]

        return button

    def _create_button_state_dict(self, otherDict):
        buttonStateDict = {}
        for button in list(otherDict.values()):
            buttonStateDict[button] = 0

        return buttonStateDict

    def _set_controller(self):
        pygame.init()
        pygame.joystick.init()

        num_joysticks = pygame.joystick.get_count()
        if num_joysticks > 0:
            controller = pygame.joystick.Joystick(0)
            controller.init()
            print("Controller connected: ", controller.get_name())
        else:
            raise NoControllerDetected("No controller detected. Turn on xbox controller")

        return controller

class NoControllerDetected(Exception):
    pass
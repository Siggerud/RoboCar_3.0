import unittest
import pygame
from pygame.event import Event
from unittest.mock import patch, Mock
from xboxControl import XboxControl, NoControllerDetected

class TestXboxControl(unittest.TestCase):
    @patch("pygame.joystick.Joystick")
    @patch("pygame.init")
    @patch("pygame.joystick.init")
    @patch.object(pygame.joystick, "get_count")
    def get_xbox_control(self, mock_count, mock_joyInit, mock_init, mock_joyJoy):
        mock_count.return_value = 1
        xboxControl = XboxControl()

        return xboxControl

    @patch("pygame.init")
    @patch("pygame.joystick.init")
    @patch.object(pygame.joystick, "get_count")
    def test_for_no_controller_detected_exception(self, mock_count, mock_joyInit, mock_init):
        mock_count.return_value = 0
        with self.assertRaises(NoControllerDetected):
            xboxControl = XboxControl()

    @patch("pygame.quit")
    def test_cleanup_calls_quit(self, mock_quit):
        xboxControl = self.get_xbox_control()
        xboxControl.cleanup()

        mock_quit.assert_called_once()

    def test_get_button_and_press_value_from_event_returns_state_0(self):
        mock_controller = Mock()

        event1 = Event(pygame.JOYHATMOTION, {'joy': 0, 'instance_id': 0, 'hat': 0, 'value': (-1, 0)})
        event2 = Event(pygame.JOYHATMOTION, {'joy': 0, 'instance_id': 0, 'hat': 0, 'value': (0, 0)})

        xboxControl = self.get_xbox_control()
        xboxControl._controller = mock_controller

        # first call is for left d-pad pushed down
        mock_controller.get_hat.return_value = (-1, 0)
        button, pressValue = xboxControl.get_button_and_press_value_from_event(event1)

        self.assertEqual("D-PAD left", button)
        self.assertEqual(1, pressValue)

        # second call is for release of left d-pad
        mock_controller.get_hat.return_value = (0, 0)
        button, pressValue = xboxControl.get_button_and_press_value_from_event(event2)

        self.assertEqual("D-PAD left", button)
        self.assertEqual(0, pressValue)

    def test_get_button_and_press_value_from_event_returns_correct_axis_button_and_press_value(self):
        event = Event(pygame.JOYAXISMOTION, {'joy': 0, 'instance_id': 0, 'axis': 2, 'value': 0.6357615894039735})

        xboxControl = self.get_xbox_control()
        button, pressValue = xboxControl.get_button_and_press_value_from_event(event)

        self.assertEqual("RSB horizontal", button)
        self.assertEqual(0.6357615894039735, pressValue)

    def test_get_button_and_press_value_from_event_returns_correct_push_button_and_state(self):
        event1 = Event(pygame.JOYBUTTONDOWN, {'joy': 0, 'instance_id': 0, 'button': 3})
        event2 = Event(pygame.JOYBUTTONUP, {'joy': 0, 'instance_id': 0, 'button': 3})

        xboxControl = self.get_xbox_control()

        # first call is for the X button to be pushed down
        button, pressValue = xboxControl.get_button_and_press_value_from_event(event1)

        self.assertEqual("X", button)
        self.assertEqual(1, pressValue)

        # second call is for the X button to be released
        button, pressValue = xboxControl.get_button_and_press_value_from_event(event2)

        self.assertEqual("X", button)
        self.assertEqual(0, pressValue)

    @patch("xboxControl.time", autospec=True)
    def test_check_for_exit_button_returns_true(self, mock_time):
        eventButtonDown = Event(pygame.JOYBUTTONDOWN, {'joy': 0, 'instance_id': 0, 'button': 11})
        eventButtonUp = Event(pygame.JOYBUTTONUP, {'joy': 0, 'instance_id': 0, 'button': 11})

        xboxControl = self.get_xbox_control()

        # simulate the first pushing and releasing of exit button
        mock_time.return_value = 1 # set first button push to occur at second 1

        button, pressValue = xboxControl.get_button_and_press_value_from_event(eventButtonDown)
        exitCheck = xboxControl.check_for_exit_event(button)
        self.assertFalse(exitCheck)

        button, pressValue = xboxControl.get_button_and_press_value_from_event(eventButtonUp)
        exitCheck = xboxControl.check_for_exit_event(button)
        self.assertFalse(exitCheck)

        # simulate the second pushing and releasing of exit button
        # when the timegap between the button pushes is within a certain timeframe it should return True
        mock_time.return_value = 1.4  # set second button push to occur 0.4 second after first button push
        button, pressValue = xboxControl.get_button_and_press_value_from_event(eventButtonDown)
        exitCheck = xboxControl.check_for_exit_event(button)
        self.assertTrue(exitCheck)

    @patch("xboxControl.time", autospec=True)
    def test_check_for_exit_button_returns_false(self, mock_time):
        eventButtonDown = Event(pygame.JOYBUTTONDOWN, {'joy': 0, 'instance_id': 0, 'button': 11})
        eventButtonUp = Event(pygame.JOYBUTTONUP, {'joy': 0, 'instance_id': 0, 'button': 11})

        xboxControl = self.get_xbox_control()

        # simulate the first pushing and releasing of exit button
        mock_time.return_value = 1 # set first button push to occur at second 1

        button, pressValue = xboxControl.get_button_and_press_value_from_event(eventButtonDown)
        exitCheck = xboxControl.check_for_exit_event(button)
        self.assertFalse(exitCheck)

        button, pressValue = xboxControl.get_button_and_press_value_from_event(eventButtonUp)
        exitCheck = xboxControl.check_for_exit_event(button)
        self.assertFalse(exitCheck)

        # simulate the second pushing and releasing of exit button
        # when the timegap between the button pushed is too long, the method should return False
        mock_time.return_value = 1.6  # set second button push to occur 0.6 seconds after first button push
        button, pressValue = xboxControl.get_button_and_press_value_from_event(eventButtonDown)
        exitCheck = xboxControl.check_for_exit_event(button)
        self.assertFalse(exitCheck)

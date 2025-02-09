import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from buzzer import Buzzer
from unittest.mock import patch

@pytest.fixture
def buzzer():
    return Buzzer(38, 0.3, 4, {"buzzCommand": "start honking", "buzzForSpecifiedTimeCommand": "honk {param}"})

def test_get_command_validity(buzzer):
    assert buzzer.get_command_validity("my command") == "valid"

@patch("RPi.GPIO.output")
@patch("buzzer.sleep")
def test_buzz_time(mockSleep, mockGPIO, buzzer):
    buzzer.handle_voice_command("start honking")

    mockGPIO.assert_called()
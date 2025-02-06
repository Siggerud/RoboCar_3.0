import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from buzzer import Buzzer

@pytest.fixture
def buzzer():
    return Buzzer(1, 0.3, 4, {"buzzCommand": "start honking", "buzzForSpecifiedTimeCommand": "honk {param}"})

def test_get_command_validity(buzzer):
    honker = buzzer
    pass
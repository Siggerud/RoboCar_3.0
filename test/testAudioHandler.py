import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from audioHandler import AudioHandler, MicrophoneException
import pytest
from unittest.mock import Mock, patch

def test_bluetooth_headphones_connected():
    with pytest.raises(MicrophoneException):
        with patch('subprocess.check_output', return_value=b"Device 12345 yourMicrophone"), \
        patch('sleep', return_value=None), \
        patch.object(AudioHandler, '_get_device_index', return_value=1):
            audioHandler = AudioHandler("stop", "English (United States)", "myMicrophone")


def test_get_device_index():
    pass
    # TODO: Implement test

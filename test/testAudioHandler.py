from ..src.audioHandler import AudioHandler, MicrophoneException
import pytest
from unittest.mock import Mock, patch

def test_bluetooth_headphones_connected():
    with pytest.raises(MicrophoneException):
        with patch('subprocess.check_output', return_value="Device 12345 myMicrophone"), \
        patch.object(AudioHandler, '_get_device_index', return_value=1):
            audioHandler = AudioHandler("stop", "English (United States)", "myMicrophone")


def test_get_device_index():
    pass
    # TODO: Implement test

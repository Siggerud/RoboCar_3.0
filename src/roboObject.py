from abc import ABC, abstractmethod

class RoboObject(ABC):

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def print_commands(self):
        pass

    @abstractmethod
    def handle_voice_command(self, command):
        pass

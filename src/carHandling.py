import RPi.GPIO as GPIO
from roboCarHelper import RobocarHelper

class CarHandling:
	def __init__(self, leftBackward, leftForward, rightBackward, rightForward, enA, enB, pwmMinTT, pwmMaxTT, speedStep, userCommands):
		self._leftBackward: int = leftBackward
		self._leftForward: int = leftForward
		self._rightBackward: int = rightBackward
		self._rightForward: int = rightForward
		self._enA: int = enA
		self._enB: int = enB

		self._pwmMinTT: int = pwmMinTT
		self._pwmMaxTT: int = pwmMaxTT

		self._speedStep: int = speedStep

		self._speed: int = self._pwmMinTT

		self._turnLeft: bool = False
		self._turnRight: bool = False
		self._goForward: bool = False
		self._goReverse: bool = False

		self._gpioThrottle = None

		self._pwmA = None
		self._pwmB = None

		directionCommands = userCommands["direction"]
		self._direction_commands: dict = {
			directionCommands["turnLeftCommand"]: {"description": "Turns car left", "gpioValues": [False, True, True, False], "direction": "Left"},
			directionCommands["turnRightCommand"]: {"description": "Turns car right", "gpioValues": [True, False, False, True], "direction": "Right"},
			directionCommands["driveCommand"]: {"description": "Drives car forward", "gpioValues": [True, True, False, False], "direction": "Forward"},
			directionCommands["reverseCommand"]: {"description": "Reverses car", "gpioValues": [False, False, True, True], "direction": "Reverse"},
			directionCommands["stopCommand"]: {"description": "Stops car", "gpioValues": [False, False, False, False], "direction": "Stopped"},
		}

		speedCommands = userCommands["speed"]
		self._speed_commands: dict = {
			speedCommands["increaseSpeedCommand"]: {"description": "Increases car speed"},
			speedCommands["decreaseSpeedCommand"]: {"description": "Decrease car speed"}
		}

		self._direction: str = "Stopped"

		self._exact_speed_commands: dict = self._set_exact_speed_commands(speedCommands["exactSpeedCommand"])

	def setup(self):
		GPIO.setup(self._leftBackward, GPIO.OUT)
		GPIO.setup(self._leftForward, GPIO.OUT)
		GPIO.setup(self._rightBackward, GPIO.OUT)
		GPIO.setup(self._rightForward, GPIO.OUT)
		GPIO.setup(self._enA, GPIO.OUT)
		GPIO.setup(self._enB, GPIO.OUT)

		self._pwmA = GPIO.PWM(self._enA, 100)
		self._pwmB = GPIO.PWM(self._enB, 100)

		self._pwmA.start(self._speed)
		self._pwmB.start(self._speed)

		self._gpioThrottle = {True: GPIO.HIGH, False: GPIO.LOW}

	def handle_voice_command(self, command):
		print("Command: " + command)
		if command in self._direction_commands:
			newGpioValues = self._direction_commands[command]["gpioValues"]
			self._adjust_gpio_values(newGpioValues)
			self._adjust_direction_value(self._direction_commands[command]["direction"])
		elif command in self._speed_commands or command in self._exact_speed_commands:
			print("Adjusting speed...")
			self._adjust_speed(command)

	def print_commands(self):
		for command, v in self._direction_commands.items():
			print(f"{command}: {v['description']}")

	def get_command_validity(self, command) -> str:
		# check if direction remains unchanged
		if command in self._direction_commands:
			if self._direction == self._direction_commands[command]["direction"]:
				return "partially valid"

		# check if speed remains unchanged
		elif command in self._exact_speed_commands:
			if self._speed == self._exact_speed_commands[command]:
				return "partially valid"

		# check if new speed increase/decrease is within valid range
		elif command in self._speed_commands:
			if command == "go faster":
				if (self._speed + self._speedStep) > self._pwmMaxTT:
					return "partially valid"
			elif command == "go slower":
				if (self._speed - self._speedStep) < self._pwmMinTT:
					return "partially valid"

		return "valid"


	def cleanup(self):
		self._pwmA.stop()
		self._pwmB.stop()

	def get_voice_commands(self) -> dict[str: str]:
		return RobocarHelper.chain_together_dict_keys([self._direction_commands,
										 self._speed_commands,
										 self._exact_speed_commands])

	def get_current_speed(self):
		return int(self._speed)

	def get_current_turn_value(self):
		return self._direction

	def _set_exact_speed_commands(self, userCommand: str) -> dict:
		speedCommands: dict = {}
		for speed in range(self._pwmMinTT, self._pwmMaxTT + 1):
			command = RobocarHelper.format_command(userCommand, str(speed))
			#command = self._format_exact_speed_command(userCommand, speed)
			speedCommands[command] = speed

		return speedCommands

	def _adjust_direction_value(self, direction):
		self._direction = direction

	def _adjust_speed(self, command: str):
		adjustSpeed: bool = False

		if command == "go faster":
			self._speed += self._speedStep
			adjustSpeed = True
		elif command == "go slower":
			self._speed -= self._speedStep
			adjustSpeed = True
		else:
			newSpeed = self._exact_speed_commands[command]
			if newSpeed != self._speed:
				adjustSpeed = True
				self._speed = newSpeed

		if adjustSpeed:
			print(self._speed)
			self._change_duty_cycle()

	def _change_duty_cycle(self):
		for pwm in [self._pwmA, self._pwmB]:
			pwm.ChangeDutyCycle(self._speed)

	def _adjust_gpio_values(self, gpioValues):
		leftForwardValue, rightForwardValue, leftBackwardValue, rightBackwardValue = gpioValues

		GPIO.output(self._leftForward, self._gpioThrottle[leftForwardValue])
		GPIO.output(self._rightForward, self._gpioThrottle[rightForwardValue])
		GPIO.output(self._leftBackward, self._gpioThrottle[leftBackwardValue])
		GPIO.output(self._rightBackward, self._gpioThrottle[rightBackwardValue])







import RPi.GPIO as GPIO
from roboCarHelper import map_value_to_new_scale, chain_together_dict_keys

class CarHandling:
	def __init__(self, leftBackward, leftForward, rightBackward, rightForward, enA, enB, pwmMinTT, pwmMaxTT):
		self._leftBackward = leftBackward
		self._leftForward = leftForward
		self._rightBackward = rightBackward
		self._rightForward = rightForward
		self._enA = enA
		self._enB = enB

		self._pwmMinTT = pwmMinTT
		self._pwmMaxTT = pwmMaxTT

		self._speed = self._pwmMinTT

		self._turnLeft = False
		self._turnRight = False

		self._goForward = False
		self._goReverse = False

		self._gpioThrottle = None

		self._pwmA = None
		self._pwmB = None

		self._direction_commands: dict = {
			"turn left": {"description": "Turns car left", "gpioValues": [False, True, True, False], "direction": "left"},
			"turn right": {"description": "Turns car right", "gpioValues": [True, False, False, True], "direction": "right"},
			"go forward": {"description": "Drives car forward", "gpioValues": [True, True, False, False], "direction": "-"},
			"go backward": {"description": "Reverses car", "gpioValues": [False, False, True, True], "direction": "-"},
			"stop now": {"description": "Stops car", "gpioValues": [False, False, False, False], "direction": "-"},
		}

		self._speed_commands: dict = {
			"go faster": {"description": "Increases car speed"},
			"go slower": {"description": "Decrease car speed"}
		}

		self._direction: str = "-"

		self._exact_speed_commands: dict = self._set_exact_speed_commands()

		self._speedStep: int = 10 #TODO: add this to config

	def setup(self):
		GPIO.setmode(GPIO.BOARD)

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


	def cleanup(self):
		self._pwmA.stop()
		self._pwmB.stop()

		GPIO.cleanup()

	def get_car_commands(self) -> dict[str: str]:
		return chain_together_dict_keys([self._direction_commands,
										 self._speed_commands,
										 self._exact_speed_commands])

	def get_current_speed(self):
		return int(self._speed)

	def get_current_turn_value(self):
		return self._direction

	def _set_exact_speed_commands(self) -> dict:
		speedCommands: dict = {}
		for speed in range(self._pwmMinTT, self._pwmMaxTT + 1):
			speedCommands[f"speed {speed}"] = speed

		return speedCommands

	def _adjust_direction_value(self, direction):
		self._direction = direction

	def _adjust_speed(self, command: str):
		adjustSpeed: bool = False

		if command == "go faster":
			if (self._speed + self._speedStep) <= self._pwmMaxTT:
				self._speed += self._speedStep
				adjustSpeed = True
		elif command == "go slower":
			if (self._speed - self._speedStep) >= self._pwmMinTT:
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







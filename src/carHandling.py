import RPi.GPIO as GPIO
from roboCarHelper import map_value_to_new_scale
from itertools import chain

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

		self._speed = 0

		self._turnLeft = False
		self._turnRight = False

		self._goForward = False
		self._goReverse = False

		self._gpioThrottle = None

		self._pwmA = None
		self._pwmB = None

		self._controlsDictTurnButtons = {
			"Left": "D-PAD left",
			"Right": "D-PAD right",
		}

		self._controlsDictThrottle = {
			"Gas": "RT",
			"Reverse": "LT"
		}

		self._turnButtons = list(self._controlsDictTurnButtons.values())

		self._gasAndReverseButtons = list(self._controlsDictThrottle.values())

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

		self._pwmA.start(0)
		self._pwmB.start(0)

		self._gpioThrottle = {True: GPIO.HIGH, False: GPIO.LOW}

	def handle_xbox_input(self, button, pressValue):
		if button in self._turnButtons:
			self._prepare_car_for_turning(button, pressValue)
			self._move_car()
		elif button in self._gasAndReverseButtons:
			self._prepare_car_for_throttle(button, pressValue)
			self._move_car()

	def cleanup(self):
		self._pwmA.stop()
		self._pwmB.stop()

		GPIO.cleanup()

	def get_car_buttons(self):
		completeDict = dict(chain(self._controlsDictThrottle.items(), self._controlsDictTurnButtons.items()))

		return completeDict

	def get_current_speed(self):
		return int(self._speed)

	def get_current_turn_value(self):
		if self._turnLeft:
			return "Left"
		elif self._turnRight:
			return "Right"
		else:
			return "-"

	def _change_duty_cycle(self, pwms, speed):
		for pwm in pwms:
			pwm.ChangeDutyCycle(speed)

	def _adjust_gpio_values(self, gpioValues):
		leftForwardValue, rightForwardValue, leftBackwardValue, rightBackwardValue = gpioValues

		GPIO.output(self._leftForward, self._gpioThrottle[leftForwardValue])
		GPIO.output(self._rightForward, self._gpioThrottle[rightForwardValue])
		GPIO.output(self._leftBackward, self._gpioThrottle[leftBackwardValue])
		GPIO.output(self._rightBackward, self._gpioThrottle[rightBackwardValue])

	def _move_car(self):
		if self._goForward:
			if not self._turnLeft and not self._turnRight:
				gpioValues = [True, True, False, False]
			elif self._turnLeft:
				gpioValues = [False, True, False, False]
			elif self._turnRight:
				gpioValues = [True, False, False, False]
		elif self._goReverse:
			if not self._turnLeft and not self._turnRight:
				gpioValues = [False, False, True, True]
			elif self._turnLeft:
				gpioValues = [False, False, False, True]
			elif self._turnRight:
				gpioValues = [False, False, True, False]
		elif not self._goReverse and not self._goForward:
			if not self._turnLeft and not self._turnRight:
				gpioValues = [False, False, False, False]
			elif self._turnLeft:
				gpioValues = [False, True, True, False]
			elif self._turnRight:
				gpioValues = [True, False, False, True]

		self._adjust_gpio_values(gpioValues)

	def _prepare_car_for_turning(self, button, buttonState):
		stopTurning = False

		if button == "D-PAD left" and buttonState == 1:
			self._turnLeft = True
			self._turnRight = False
		elif button == "D-PAD right" and buttonState == 1:
			self._turnLeft = False
			self._turnRight = True
		else:
			self._turnLeft = False
			self._turnRight = False
			stopTurning = True

		if not stopTurning:
			if not self._goForward and not self._goReverse:
				self._change_duty_cycle([self._pwmA, self._pwmB], self._pwmMaxTT)

	def _prepare_car_for_throttle(self, button, buttonPressValue):
		speed = map_value_to_new_scale(
			buttonPressValue,
			self._pwmMinTT,
			self._pwmMaxTT,
			2
		)
		if speed > self._pwmMinTT + 1: # only change speed if over the treshold
			if button == "RT":
				self._goForward = True
				self._goReverse = False
			elif button == "LT":
				self._goForward = False
				self._goReverse = True
		else:
			speed = 0

			self._goForward = False
			self._goReverse = False
		#TODO: only change if speed has changed
		self._change_duty_cycle([self._pwmA, self._pwmB], speed)
		self._speed = speed



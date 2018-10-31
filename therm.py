try:
	import RPi.GPIO as GPIO
except ImportError as ex:
	print("Package RPi.GPIO not found, install it.")
import time
from threading import Thread
from threading import Event

# PINOUT
pinOn = 26  # Turns on (pin no. 37)
pinOff = 20  # Turns off


class Thermostat(Thread):

	def __init__(self, sensor, scheduler):
		# Init pins
		try:
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(pinOn, GPIO.OUT)
			GPIO.setup(pinOff, GPIO.OUT)
			GPIO.output(pinOn, 0)
			GPIO.output(pinOff, 0)

			# Create a new sensor obj, used for reading temperature
			self.sensor = sensor
			self.scheduler = scheduler
		except Exception as gpio_ex:
			print(gpio_ex)
			raise (Exception("Problems with GPIO. Try to reboot"))
		Thread.__init__(self)
		self.stopFlag = False
		self.stopper = Event()

	def __del__(self):
		self.turnOff()
		GPIO.cleanup()

	def turnOn(self):
		GPIO.output(pinOn, 1)
		time.sleep(0.1)  # Wait for it
		GPIO.output(pinOn, 0)

	def turnOff(self):
		GPIO.output(pinOff, 1)
		time.sleep(0.1)
		GPIO.output(pinOff, 0)

	def stop(self):
		self.stopFlag = True
		self.stopper.set()

	def run(self):
		try:
			while not self.stopFlag:
				# get current temp from sensor
				current_temp = round(self.sensor.get_temp(), 1)
				# get ref temp from scheduler
				sched_temp = self.scheduler.ref_temp()

				self.turnOn() if current_temp < sched_temp else self.turnOff()
				if self.verbose:
					print("Therm: checking..")
				self.stopper.wait(60)
		except Exception as therm_ex:
			print("Thermostat: ex")
			print(therm_ex)

		print("Thermostat: exiting...")

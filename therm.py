import RPi.GPIO as GPIO
import time
import DS18B20 as DS18B20
import scheduler
from threading import Thread
from threading import Event

# PINOUT
pinOn = 26  # Turns on (pin no. 37)
pinOff = 20  # Turns off


class Thermostat(Thread):

	def __init__(self):
		# Init pins
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pinOn, GPIO.OUT)
		GPIO.setup(pinOff, GPIO.OUT)
		GPIO.output(pinOn, 0)
		GPIO.output(pinOff, 0)

		# Create a new sensor obj, used for reading temperature
		self.sensor = DS18B20.TempSensor()
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
				currentTemp = round(self.sensor.get_temp(), 1)
				# get ref temp from scheduler
				schedTemp = self.scheduler.ref_temp()

				self.turnOn() if currentTemp < schedTemp else self.turnOff()
				if self.verbose:
					print("Therm: checking..")
				self.stopper.wait(60)
		except Exception as ex:
			print("Screen: ex")
			print(ex)

		print("Screen: exiting...")

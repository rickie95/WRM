import RPi.GPIO as GPIO
import time
import DS18B20 as DS18B20
import scheduler

pinOn = 26 #Turns on (pin no. 37)
pinOff = 20 #Turns off

#Inizialize pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(pinOn, GPIO.OUT)
GPIO.setup(pinOff, GPIO.OUT)
GPIO.output(pinOn,0)
GPIO.output(pinOff,0)

def turnOn():
	GPIO.output(pinOn,1)
	time.sleep(0.1) #Wait for it
	GPIO.output(pinOn,0)

def turnOff():
	GPIO.output(pinOff,1)
	time.sleep(0.1)
	GPIO.output(pinOff,0)

def getSched():
	return sched;

# Every minute reads temperature from DS18B20
sched = scheduler.SchedManager()


try:
	#while True:
		old_ST = 20
		try:
			schedTemp = sched.refTemp() # This is actually a critical section, think to a bad formatted file.
 		except Exception:
			schedTemp = old_ST # If something go bad better use last T set. You can even set a custom T (20C) 
 
		print("Current ref temp set: ", schedTemp)
		temp = round(DS18B20.get_temp(), 1) #Grab the T, truncated at first decimal
		print("Room: ", temp)
	
		if temp < schedTemp : # Time to turning on
			print("turning on")
			turnOn()
		if temp > schedTemp : # Turns off
			print("turning off")
			turnOff()

		#time.sleep(60)


except KeyboardInterrupt:
	print("\nPutting rele on OFF")
	turnOff()
	print("Exiting..")
	GPIO.cleanup()

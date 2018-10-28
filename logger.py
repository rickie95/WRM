import DS18B20
import datetime
import os
import scheduler_xml as scheduler
import time

s = scheduler.SchedManager()

path = "/home/pi/wrm_app/control_panel/"


try:
	original = open(path+"log.txt", "r")
	copy = open(path+"n_log.txt", "w")
	file = original.read().splitlines()
	print(len(file))
	numb = min ( 30, len(file) )
	for count in range(1, numb+1):
		copy.write(file[count]+"\n")
	original.close()
	t = DS18B20.get_temp()
	t = round(t,1)
	settemp = s.get_reference_temp()
	timez = datetime.datetime.now()
	minut = timez.minute
	if minut < 10:
		s_min = "0"+str(minut)	
	if minut >= 10:
		s_min = str(minut)
	stringa = str(timez.hour) + ":" + s_min
	copy.write(stringa + "," + str(t) + "," + str(settemp)+"\n")
	copy.close()
	os.remove(path+"log.txt")
	os.rename(path+"n_log.txt", path+"log.txt")
#	time.sleep(1)
except KeyboardInterrupt:
	original.close()
	copy.close()
	try:
		os.remove(path+"n_log.txt")
	except e:
		pass

import datetime
import xml.etree.ElementTree as ET
import operator


class SchedManager:
	# Static params, so every instance of SchedManager work on same data
	MaxT = ""
	ManualT = ""
	HolidayT = ""
	NoFreezeT = ""
	Mode = ""
	daily_sched = []  # Schedule entries list
	#daily = []
	
	def __init__(self, verbose=False):
		self.verbose = verbose
		
		try:		
			self.file = ET.parse('scheduling.xml').getroot()
		except Exception as ex:
			print("Scheduler: Problems with file")
			print("Scheduler:" + ex)
			return None
		
		SchedManager.Mode = self.file.find('mode').text.strip()
		SchedManager.HolidayT = self.file.find('holiday_temp').text.strip()
		SchedManager.MaxT = self.file.find('max_temp').text.strip()
		SchedManager.ManualT = self.file.find('manual_temp').text.strip()
		# if saily sched is not empty
		SchedManager.daily_sched = self.setFasciaD()
		if self.verbose==False:
			print("Mode: " + SchedManager.Mode)
			print("Manual t" + SchedManager.ManualT)
			SchedManager.daily_sched.print_daily_sched()

	def setFasciaD(self):  # Read the file, looking for scheduler entries
		daily = self.file.find('daily_scheduling')
		fascia_gg = DailyScheduling()
		
		for element in daily:
			# key = int(element.attrib['order'])
			start, end, temp = element
			h_ss, m_ss = start.attrib
			h_ee, m_ee = end.attrib
			ss = int(start.attrib[h_ss])*60 + int(start.attrib[m_ss])
			ee = int(end.attrib[h_ee])*60 + int(end.attrib[m_ee])
			temp = int(temp.attrib['value'])
			fascia_gg.add_sched(ss, ee, temp)
			# print(key, ss, ee, temp)
		return fascia_gg
	
	def ref_temp(self):
		if self.Mode == "W":
			return self.get_weekly_temp()
		if self.Mode == "H":
			return SchedManager.HolidayT
		if self.Mode == "F":
			return SchedManager.NoFreezeT
		if self.Mode == "D":
			return self.get_daily_temp()
		if self.Mode == "M":
			return SchedManager.ManualT

	def get_daily_temp(self):
		time = datetime.datetime.now()
		return SchedManager.daily_sched.getTempByTime(time.hour, time.minute)
		
	def get_weekly_temp(self):
		time = datetime.datetime.now()
		DOW = datetime.datetime.today().weekday()
		fascia = SchedManager.daily_sched[DOW]
		return fascia.get_temp_by_time(time.hour, time.minute)

	def get_mode(self):
		return SchedManager.Mode

	def set_manual_temp(self, temp):
		SchedManager.ManualT = int(temp)

	def set_holiday_temp(self, temp):
		SchedManager.HolidayT = int(temp)

	def set_no_freeze_temp(self, temp):
		SchedManager.NoFreezeT = int(temp)

	def set_mode(self, mode):
		SchedManager.Mode = mode

	@staticmethod
	def add_temp(s, e, t):
		SchedManager.daily_sched.addFascia(s, e, t)

	@staticmethod
	def remove_by_st(st):
		SchedManager.daily_sched.remove_sched_by_start(st)

	@staticmethod
	def get_daily_sched_list():
		return SchedManager.daily_sched.get_sched_list()

	@staticmethod
	def print_sched():
		SchedManager.daily_sched.printFascia()


class DailyScheduling:

	def __init__(self, d="Daily"):
		self.day = d
		self.lista = []

	def get_temp_by_time(self, hour, minute):
		actual_time = hour * 60 + minute
		for elem in self.lista:
			if elem[1] <= actual_time <= elem[2]:
				return elem[3]
		return None

	def sort_by_start_time(self):
		self.lista.sort(key=operator.itemgetter(1))

	def get_day(self):
		return self.day

	def add_sched(self, s, e, t):
		self.lista.append((len(self.lista)+1, s, e, t))
		self.sort_by_start_time()

	def remove_sched_by_start(self, st):
		self.lista.remove(list(filter(lambda x : x[1] == st, self.lista))[0])

	def get_sched_list(self):
		return self.lista.copy()

	# TODO: da revisionare
	def print_daily_sched(self):
		print(self.day + " (" + str(len(self.lista)) + ")")
		for line in self.lista:
			print(line)

	def getShortDay(self):
		gg = self.get_day()[:3]
		return gg.upper() + ":"

	def getFascia(self):
		return self.lista

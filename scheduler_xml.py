import datetime
import tempfile
import xml.etree.ElementTree as ET

class SchedManager:
	#Parametri statici, accessibili ad ogni istanza della classe
	MaxT = ""
	ManualT = ""
	HolidayT = ""
	NoFreezeT = ""
	Mode = ""
	sched = [] # e' una lista di fasce
	daily = []
	
	def __init__(self): # apre il file e legge le informazioni di base, procede a creare lo scheduler  e le fasce se in mod W o D
		
		try:		
			self.file = ET.parse('scheduling.xml').getroot()
		except:
			print("Problemi con il file")
			return null
		
		Mode = self.file.find('mode').text.strip()
		HolidayT = self.file.find('holiday_temp').text.strip()
		MaxT = self.file.find('max_temp').text.strip()
		
		print(Mode)
		print(HolidayT)
		
		self.f_gg = self.setFasciaD()
		self.f_gg.printFascia()

	def setFasciaD(self): #leggo il file andando a cercare le fasce per lo scheduler giornaliero
                daily = self.file.find('daily_scheduling')
                fascia_gg = FasciaGiornaliera()   
		
		for element in daily:
                    key = int(element.attrib['order'])
                    start, end, temp = element
                    h_ss, m_ss = start.attrib
                    h_ee, m_ee = end.attrib
                    ss = int(start.attrib[h_ss])*60 + int(start.attrib[m_ss])
                    ee = int(end.attrib[h_ss])*60 + int(end.attrib[m_ss])
                    temp = int(temp.attrib['value'])
                    fascia_gg.addFascia(key, ss, ee, temp)
                    print(key, ss, ee, temp)
                
                return fascia_gg

	def setFasceW(self):
		pass
	
	def refTemp(self):
		if self.isChanged():	
			self.__init__()

		if self.Mode == "W":
			return self.getWeeklyT()
		if self.Mode == "H":
			return self.HolidayT
		if self.Mode == "F":
			return self.NoFreezeT
		if self.Mode == "D":
			return self.getDailyT()
		if self.Mode == "M":
			return self.ManualT

	def getDailyT(self):
		time = datetime.datetime.now()
		return self.daily.getTempByTime(time.hour, time.minute)
		
	def getWeeklyT(self): 
		time = datetime.datetime.now()
		DOW = datetime.datetime.today().weekday()
		fascia = self.sched[DOW]
		return fascia.getTempByTime(time.hour, time.minute)
	
	def isChanged(self):
		f = open(self.path+"changed.txt", "r+w")
		for line in f:
			line = line.rstrip('\n')
			if line == "True":
				print("il file e' stato modificato")
				esit = True
			if line == "False":
				print("Il file non e' stato modificato")
				esit = False
		if esit == True:
			f.seek(0)
			f.truncate()
			f.write("False")
		f.close
		return esit

################################### SEZIONE LATO VIEWS ########################################

	def notifyChange(self):
		f = open(self.path+"changed.txt", "r+w")
		f.seek(0)
		f.truncate()
		f.write("True")

	def setManualT(self, temp):
		self.ManualT = int(temp)

	def setHolidayT(self, temp):
		self.HolidayT = int(temp)

	def setNoFreezeT(self, temp):
		self.NoFreezeT = int(temp)

	def setMode(self, mode):
		self.Mode = mode
	
	def getFasce(self):
		return self.daily

	def setFasce(self, lista):
		self.daily.setLista(lista)
	
	def printFasce(self):
		self.daily.printFascia()
	
	def getMode(self):
		return self.Mode

	def applyChanges(self):
		f = open(self.path+"scheduling.txt", "r+w")
		f.seek(0)
		f.truncate()
		
		f.write("$MODE\n")
		f.write(str(self.Mode)+"\n")
		
		f.write("$MANUAL_T\n")
		f.write(str(self.ManualT)+"\n")
		
		f.write("$HOLIDAY_T\n")
		f.write(str(self.HolidayT)+"\n")
		
		f.write("$NOFREEZE_T\n")
		f.write(str(self.NoFreezeT)+"\n")
		
		f.write("$MAX_T\n")
		f.write(str(self.MaxT)+"\n")

		f.write("$DAILY\n")
		for orari in self.daily.getListaFasce():
			s, e, t = orari # ((hh,mm),(hh,mm),t)
			ss, es = s	# (hh,mm)
			if(es < 10):
				es = "0"+str(es)
			se, ee = e	# (hh,mm)
			if(ee < 10):
				ee = "0"+str(ee)
			f.write(str(ss)+":"+str(es)+"," + str(se)+":"+str(ee) + "," + str(t)+"\n")

		f.write("---\n")
		f.write("$WEEKLY\n")
		for fasciaG in self.sched:
			f.write(fasciaG.getShortDay()+"\n")
			for orari in fasciaG.getListaFasce():
				s, e, t = orari
				ss, es = s
				es, ee = e
				f.write(str(ss)+":"+str(es)+"," + str(se)+":"+str(ee) + "," + str(t)+"\n")

			f.write("--\n")
		f.write("---\n")
		f.close()
		self.notifyChange()		

class FasciaGiornaliera:

	def __init__(self,d="Daily"):
		self.day = d
		self.lista = []

	def getTempByTime(self,hour, minute):
            actual_time = hour * 60 + minute
		for elem in self.lista:
			key, s, e, t = elem
			if( s <= actual_time && actual_time <= e ):
                            return t
		return None

	def setLista(self, lista): # dove lista è una lista di righe del tipo hh:mm,hh:mm,temp
		self.lista = []
		key = 1
		for row in lista:
			s, e, t = row
			ss, se = s.split(":")
			es, ee = e.split(":")
			self.lista.append(( key, int(ss)*60 + int(se) , int(es)*60 + int(ee) , int(t) ))

	def getDay(self):
		return self.day

	def getListaFasce(self):
		return self.lista

	def getShortDay(self):
		gg = self.getDay()[:3]
		return gg.upper()+":"
		
	def getFascia(self):
		return self.lista		
		
	def addFascia(self,key, s,e,t):
		self.lista.append((key,s,e,t))
	
	def printFascia(self):
		print(self.day + " (" + str(len(self.lista)) + ")")
		for line in self.lista:
			print(line)


s = SchedManager()
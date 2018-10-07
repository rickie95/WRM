import screen as S
import DS18B20 as D
import time

t = D.TempSensor()
s = S.Schermo(t)  

try:
    
    s.setParam(t.get_temp(), 20, 1)
    
    s.start()
    
    while True:
        time.sleep(1)
    
except (Exception, KeyboardInterrupt) as ex:
    print("Sto uscendo, generata eccezione")
    print(ex)
    s.stop()
    s.join()
    

print("Tutto ok")
if s.is_alive():
    s.stop = True 
    s.join()

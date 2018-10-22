import screen as S
import DS18B20 as D
import therm
import time

t_sensor = D.TempSensor()
screen = None

try:
    screen = S.Screen(t_sensor, True)
except Exception as ex:
    print("I cannot reach the screen, check wiring.")
    print(ex)

try:

    if screen is not None:
        screen.setParam(t_sensor.get_temp(), 20, 1)
        screen.start()
    
    while True:
        time.sleep(1)
    
except (Exception, KeyboardInterrupt) as ex:
    print("Sto uscendo, generata eccezione")
    print(ex)
    screen.stop()
    screen.join()
    

print("Tutto ok")
if screen.is_alive():
    screen.stop = True
    screen.join()

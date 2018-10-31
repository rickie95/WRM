import screen as S
import DS18B20 as D
import therm as T
import scheduler_xml as Scheduler
import sys
import time


def main(verbose=False):
    t_sensor = None
    screen = None
    thermostat = None
    scheduler = None

    try:
        t_sensor = D.TempSensor()
    except Exception as ex:
        print("Cannot reach the sensor, check wiring. Aborting..")
        print(ex)

    try:
        scheduler = Scheduler.SchedManager()
    except Exception as ex:
        print("A problem occurs while initialising Scheduler obj.")
        print(ex)

    # Create and init Screen
    if t_sensor is not None and scheduler is not None:
        try:
            thermostat = T.Thermostat(t_sensor)
            screen = S.Screen(t_sensor, verbose)
        except Exception as ex:
            print(ex)

        try:
            if thermostat is not None:
                thermostat.start()

            if screen is not None:
                screen.setParam(t_sensor.get_temp(), 20, 1)
                screen.start()

            while True:
                time.sleep(1)
        except (Exception, KeyboardInterrupt) as ex:
            print("Exiting, raised exception.")
            print(ex)
            screen.stop()
            thermostat.stop()
            screen.join()
            thermostat.join()

    print("Everything ok.")
    if screen.is_alive():
        screen.stop = True
        screen.join()
    if thermostat.is_alive():
        thermostat.stop()
        thermostat.join()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        main()
    if len(sys.argv) == 2 and (sys.argv[1] == "v"):
        main(True)

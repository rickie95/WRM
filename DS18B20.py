import os
import glob
import time
# Could be converted in a static class


class TempSensor:

    def __init__(self):
        os.system('modprobe w1-gpio')
        os.system('sudo modprobe w1-therm')
        base_dir = '/sys/bus/w1/devices/'                          # point to the address
        device_folder = glob.glob(base_dir + '28*')[0]             # find device with address starting from 28*
        self.device_file = device_folder + '/w1_slave'                  # store the details

    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()                                   # read the device details
        f.close()
        return lines

    def get_temp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':                   # ignore first line
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        temp = None    # find temperature in the details
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp = float(temp_string) / 1000.0                 # convert to Celsius
        return temp

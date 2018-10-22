#!/usr/bin/env python
# coding: utf-8
import time
import datetime
import os
import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI

import DS18B20 as tempSensor

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from threading import Thread
from threading import Event

# HW params
DC = 23
RST = 24
SPI_PORT = 0
SPI_DEVICE = 0

# ABOUT WIRING:
#   Script assumes the current wiring: (LCD -> RASPBERRY PI (BCM))
#       Pin #1 RST  ->  Pin #24
#       Pin #2 CE   ->  Pin CS0
#       Pin #3 DC   ->  Pin #23
#       Pin #4 DIN  ->  Pin MOSI
#       Pin #5 CLK  ->  Pin SCLK
#       Pin #6 VCC  ->  Pin 3.3V
#       Pin #7 BL   ->  Pin 3.3V
#       Pin #8 GND  ->  Pin GND
#   Power draw is not really a thing for this display, anyway if you're using board like RP Zero it's preferable use
#   a separate power source.

# LCD dim: 84 rows x 48 cols


class Screen(Thread):
    
    def __init__(self, sensor, verbose=False):
        self.verbose = True
        self.sensor = sensor
        # load fonts
        try:
            path = os.getcwd() + "arial.ttf"
            self.font = ImageFont.truetype(path, 9)
            self.fontBig = ImageFont.truetype(path, 20)
            self.fontMid = ImageFont.truetype(path, 10)
            self.fontLil = ImageFont.truetype(path, 9)
        except IOError:
            print("WARN: font not found, I'll load the (ugly) default font.")
            self.font = ImageFont.load_default()
            self.fontBig = self.font
            self.fontMid = self.font

        print("Init the screen..")
        self.display = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))
        self.display.begin(contrast=60)
        # init the tread only if everything is ok.
        Thread.__init__(self)
        self.stopFlag = False
        self.stopper = Event()


    def update(self):
        self.display.clear()
        self.display.display()
        image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))

        draw = ImageDraw.Draw(image)

        draw.rectangle((0, 0, LCD.LCDWIDTH, LCD.LCDHEIGHT), outline=255, fill=255)

        # x_start, y_start, x_end, y_end
        draw.line((0, 10, 84, 10))
        draw.line((0, 39, 84, 39))
        
        draw.text((0, 0), self.getTimeFormatted(), font=self.font)
        draw.text((60, 0), self.mode, font=self.font)
        draw.text((0, 10), self.currentTemp, font=self.fontBig)
        draw.text((63, 11), self.setTemp, font=self.fontMid)
        # draw.text((0,40), 'Error 505', font=fontLil)

        self.display.image(image)
        self.display.display()
        
    # Format input parameters (INT, INT, INT)
    def setParam(self, currentTemp, setTemp, mode):
        self.setCurrentTemp(currentTemp)
        self.setSetTemp(setTemp)
        self.setMode(mode)

    def setCurrentTemp(self, currentTemp):
        self.currentTemp = str(round(currentTemp,1)) + u'°'
    
    def setSetTemp(self, setTemp):
        self.setTemp = str(round(setTemp,0)) + u'°'
        
    def setMode(self, mode):
        if mode == 0:
            self.mode = 'AUTO'
        else:
            self.mode = 'MAN'
        
    # returns a string like 'hh:mm' (eg. 16:04)
    def getTimeFormatted(self):
        now = datetime.datetime.now()
        if now.minute < 10:
            min = '0'+str(now.minute)
        else:
            min = str(now.minute)
        if now.hour < 10:
            hh = '0'+str(now.hour)
        else:
            hh = str(now.hour)
        
        return hh+':'+min
    
    def stop(self):
        self.stopFlag = True
        self.stopper.set()
    
    # Thread routine, every 60s
    def run(self):
        try:
            while not self.stopFlag:
                # get current temp from sensor, then update
                self.setCurrentTemp(self.sensor.get_temp())
                self.update()
                if self.verbose:
                    print("Screen: updated")
                self.stopper.wait(60)
        except Exception as ex:
            print("Screen: ex")
            print(ex)
            
        print("Screen: exiting...")


#!/usr/bin/env python3
from tm1637 import TM1637
from time import time, sleep, localtime
import RPi.GPIO as GPIO
import os
DIO=6
CLK=5
GPIO.setmode(GPIO.BCM)
GPIO.setup(9, GPIO.IN)
GPIO.setup(10, GPIO.IN)
GPIO.setup(11, GPIO.IN)
def show_clock(tm):
    t = localtime()
    sleep(1 - time() % 1)
    tm.numbers(t.tm_hour, t.tm_min, False)
tm = TM1637(CLK, DIO)
tm.brightness(0)
radio = False
while True:
    show_clock(tm)
    if GPIO.input(10) == False:
      print ("Stop pressed")
      tm.show("STOP")
      os.system("killall mplayer")
      sleep(1)
    if GPIO.input(9) == False:
      print ("Play Pressed")
      tm.show("Play")
      if radio == False:
        os.system("mplayer -playlist /home/pi/alarms/alarmlist.m3u &")
      if radio == True:
        os.system("mplayer -playlist http://network.absoluteradio.co.uk/core/audio/aacplus/live.pls?service=achq &")
    if GPIO.input(11) == False:
      print ("Mode changed")
      if radio == False:
        print ("Radio")
        radio = True
        tm.show("RAD ")
      else:
        print ("Local Files")
        radio = False
        tm.show("FLAC")

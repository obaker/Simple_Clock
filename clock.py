#!/usr/bin/env python3
from tm1637 import TM1637
from time import time, sleep, localtime
import RPi.GPIO as GPIO
import os
import vlc
import fnmatch
import random
import os.path
import threading
DIO=6
CLK=5
GPIO.setmode(GPIO.BCM)
GPIO.setup(9, GPIO.IN)
GPIO.setup(10, GPIO.IN)
GPIO.setup(11, GPIO.IN)
def show_clock(tm):
    t = localtime()
    tm.numbers(t.tm_hour, t.tm_min, False)
tm = TM1637(CLK, DIO)    
tm.brightness(0)
radio = False
source_path="/home/pi/Music/oliver"
flist = []
for root, dirs, files in os.walk(source_path, followlinks = True):
  for name in files:
    fullname=os.path.join(root,name)
    if (fnmatch.fnmatch(fullname,'*.mp3') or fnmatch.fnmatch(fullname,'*.flac')):
      flist.append(fullname)
instance = vlc.Instance()
player = instance.media_player_new()
station = vlc.MediaList(["http://network.absoluteradio.co.uk/core/audio/aacplus/live.pls?service=achq"])
radio=vlc.Instance().media_list_player_new()
radio.set_media_list(station)
while True:
    show_clock(tm)
    if GPIO.input(10) == False:
       print ("Stop pressed")
       tm.show("STOP")
       player.stop()
       radio.stop()
       os.system("killall mplayer")
    if GPIO.input(9) == False:
       radio.stop()
       print ("Play Pressed")
       tm.show("FLAC")
       player.set_mrl(random.choice(flist))
       player.play()
    if GPIO.input(11) == False:
       player.stop()
       print ("Radio")
       tm.show("RAD ")
       radio.play()
    if player.get_state() == vlc.State.Ended:
        player.set_mrl(random.choice(flist))
        player.play()
    sleep(1)

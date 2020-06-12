#!/usr/bin/env python3
from tm1637 import TM1637
import datetime
from time import time, sleep, localtime, strftime
import RPi.GPIO as GPIO
import os
import vlc
import fnmatch
import random
import os.path
import threading
import sqlite3
from sys import argv, exit
DIO=6
CLK=5
GPIO.setmode(GPIO.BCM)
GPIO.setup(9, GPIO.IN)
GPIO.setup(10, GPIO.IN)
GPIO.setup(11, GPIO.IN)
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
def initialise_db():
  db = sqlite3.connect(db_file)
  c = db.cursor()
  c.execute('''CREATE TABLE alarms (alarm_ID INTEGER PRIMARY KEY, time TEXT, dow INT, radio INT);''')
  db.commit()
  c.execute('PRAGMA user_version=1;')
  db.commit()
  db.close()
def remove_alarm(delete):
    active_days = []
    db = sqlite3.connect(db_file)
    c = db.cursor()
    c.execute("SELECT dow FROM alarms WHERE alarm_ID = "+delete)
    dow = c.fetchone()[0]
    if dow % 2 != 1: 
       for i in range(7):
          if dow & (128 >> i) != 0:
             active_days.append(weekdays[i])
       if len(active_days) == 1:
          c.execute("DELETE FROM alarms WHERE alarm_ID = "+delete)
       else:
          active_days.remove (strftime("%A", localtime()))
          new_dow = 0
          for i in range(7):
             if weekdays[i] in active_days:
                new_dow = new_dow + (128 >> i)
          c.execute("UPDATE alarms SET dow = "+str(new_dow)+" WHERE alarm_ID = "+delete)
    db.commit()
    db.close()
def view_db(alarm_time, ID):   
   time = "00:00"
   alarm_ID = None
   alarm_set = False
   db = sqlite3.connect(db_file)
   c = db.cursor()
   for dow, time, alarm_ID in db.execute("SELECT dow, time, alarm_ID FROM alarms ORDER BY time ASC;"): #Selects the primary key, time and days of week sorted by time, loops for all alarms
       active_days = []
       for i in range(7):
          if dow & (128 >> i) != 0:
             #dow = dow - weekday_numbers[i]
             active_days.append(weekdays[i])
       if strftime("%A", localtime()) in active_days and strftime("%H:%M", localtime()) < time < alarm_time and alarm_set == False:
          alarm_set = True
          alarm_time = time
          ID = alarm_ID
          #if dow % 2 == 1:
          #    repeat = True
   db.commit()
   db.close()
   return (alarm_time,ID)
def led_brightness():#function to change brightness of the clock during the day
    d = datetime.datetime.utcnow()
    if 8 < d.hour < 21:
        tm.brightness(7)
    if 21 <= d.hour < 23:
        tm.brightness(2)
    elif 8 > d.hour or d.hour >= 23:
        tm.brightness(0)
def show_clock(tm):
    t = localtime()
    tm.numbers(t.tm_hour, t.tm_min, False)
if len(argv) > 2:
   exit()
if len(argv) < 2:
   db_file = "/home/pi/alarms/clock.db"
else:
   db_file = sys.argv[1]
tm = TM1637(CLK, DIO)    
led_brightness()
radio = False
source_path="/home/pi/Music/oliver"
alarm_path="/home/pi/alarms/symlinks"
flist = []
for root, dirs, files in os.walk(source_path, followlinks = True):
  for name in files:
    fullname=os.path.join(root,name)
    if (fnmatch.fnmatch(fullname,'*.mp3') or fnmatch.fnmatch(fullname,'*.flac') or fnmatch.fnmatch(fullname,'*.m4a')):
      flist.append(fullname)
alist = []
for root, dirs, files in os.walk(alarm_path, followlinks = True):
  for name in files:
    fullname=os.path.join(root,name)
    if (fnmatch.fnmatch(fullname,'*.mp3') or fnmatch.fnmatch(fullname,'*.flac') or fnmatch.fnmatch(fullname,'*.m4a')):
      alist.append(fullname)
instance = vlc.Instance()
player = instance.media_player_new()
station = vlc.MediaList(["http://network.absoluteradio.co.uk/core/audio/aacplus/live.pls?service=achq"])
radio=vlc.Instance().media_list_player_new()
radio.set_media_list(station)
count = "-1"
alarm_time = "25:00"
ID = 0
normal_volume = 50
alarm_volume = 20
alarm_checker = view_db(alarm_time, ID)
alarm_time = alarm_checker[0] 
ID = alarm_checker[1]
while True:
    show_clock(tm)
    if GPIO.input(10) == False:
       tm.show("STOP")
       player.stop()
       radio.stop()
    if GPIO.input(9) == False:
       radio.stop()
       tm.show("FLAC")
       player.set_mrl(random.choice(flist))
       player.audio_set_volume(normal_volume)
       player.play()
    if GPIO.input(11) == False:
       player.stop()
       tm.show("RAD ")
       player.audio_set_volume(normal_volume)
       radio.play()
    if player.get_state() == vlc.State.Ended:
        player.set_mrl(random.choice(flist))
        player.audio_set_volume(normal_volume)
        player.play()
    if count != strftime("%M", localtime()):
        alarm_checker = view_db(alarm_time, ID)
        #print ("Next alarm at " + alarm_checker[0])
        alarm_time = alarm_checker[0]
        ID = alarm_checker[1]
        led_brightness()
        #print (ID)
    if strftime("%H:%M", localtime()) >= alarm_time:
       #print (alarm_time)
       alarm_time = "25:00"
       #print (alarm_checker[2])
       radio.stop()
       player.stop()
       player.set_mrl(random.choice(alist))
       player.audio_set_volume(alarm_volume)
       player.play()
       remove_alarm(str(alarm_checker[1]))
       alarm_checker = view_db(alarm_time, ID)
       alarm_time = alarm_checker[0] 
       ID = alarm_checker[1]
    count = strftime("%M", localtime())
    sleep(1)

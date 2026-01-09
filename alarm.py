#!/usr/bin/env python3
import sqlite3
from time import localtime, strftime
from sys import exit, argv

def initialise_db():#Creates DB if it doesn't already exist
  db = sqlite3.connect(db_file)
  c = db.cursor()
  c.execute('''CREATE TABLE alarms (alarm_ID INTEGER PRIMARY KEY, time TEXT, dow INT, radio INT);''')
  db.commit()
  c.execute('PRAGMA user_version=1;')
  db.commit()
  db.close()
def display_db():#Displays database directly, without any filtering
   db = sqlite3.connect(db_file)
   c = db.cursor()
   c.execute("SELECT * from alarms")
   rows = c.fetchall()
   print ("Alarm ID, Time, dow, radio")
   for row in rows:
       print(row)
   db.commit()
   db.close()
def view_all():# Shows all alarms in a more human readable format.
   weekday_numbers = [128, 64, 32, 16, 8, 4, 2]
   weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
   db = sqlite3.connect(db_file)
   c = db.cursor()
   for dow, time, alarm_ID in db.execute("SELECT dow, time, alarm_ID FROM alarms ORDER BY time ASC;"): #Selects the primary key, time and days of week sorted by time, loops for all alarms
       active_days = []#List to store active days for alarm
       for i in range(7): # 
          if dow - weekday_numbers[i] >= 0: #checks what days alarm is active, starting from monday
             dow = dow - weekday_numbers[i] 
             active_days.append(weekdays[i]) # adds active days to list
       print (alarm_ID, time, active_days, end='')#Displays all alarms
       if dow % 2 == 1:#adds an (R) to repeating alarms
          print (" (R)")
       else:#Else if alarm is non repeating
          print ("\n")
   
def view_db(): #Shows todays alarms
   weekday_numbers = [128, 64, 32, 16, 8, 4, 2]
   weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
   db = sqlite3.connect(db_file)
   c = db.cursor()
   for dow, time in db.execute("SELECT dow, time FROM alarms ORDER BY time ASC;"): #Selects day of week and time, to show the user.
       active_days = []
       for i in range(7):
          if dow - weekday_numbers[i] >= 0:
             dow = dow - weekday_numbers[i]
             active_days.append(weekdays[i])
       if strftime("%A", localtime()) in active_days and strftime("%H:%M", localtime()) < time: #Only processes the alarm if it's set for today, and in the future.
          print(time, active_days, end='')#Displays all alarms
          if dow % 2 == 1:#adds an (R) to repeating alarms
              print (" (R)")
          else:
              print ("\n")
def add_alarm(time, dow, radio):
    db = sqlite3.connect(db_file)
    c = db.cursor()
    c.execute("INSERT INTO alarms VALUES (NULL, '" + time + "' , "+str(dow)+", "+str(radio)+")")#Inserts user specified values into alarm DB
    db.commit()
    db.close()
def remove_alarm():
    view_all()#Runs the function showing all alarms in a more human readable format.
    delete = input ("Enter the ID of the alarm to delete\n   ")
    db = sqlite3.connect(db_file)
    c = db.cursor()
    c.execute("DELETE FROM alarms WHERE alarm_ID = "+delete)#Deletes the specified alarm
    db.commit()
    db.close()
if len(argv) > 2:
   exit()
if len(argv) < 2:
   db_file = "/home/ocb/alarms/clock.db"
else:
   db_file = argv[1]
db = sqlite3.connect(db_file)
c = db.cursor()
c.execute('PRAGMA user_version;')
db.commit()
version = c.fetchone()
db.close()
if version is None or version[0] == 0:
   initialise_db()
elif version[0] != 1:
   print("Incompatible DB version")
   exit()
while True:
   command = input("  (V)iew alarms  \n  (D)isplay Database Directly\n  (A)dd Alarm \n  (R)emove Alarm \n  (Q)uit \n   ").lower()#Shows menu, and waits for valid input
   if command == "v" or command == "view":
      view_all()#Display human readable DB
   if command == "d" or command == "display":
      display_db() #display DB directly
   if command == "a" or command == "add":
      weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
      weekday_numbers = [128, 64, 32, 16, 8, 4, 2]
      dow = 0
      while True:
         alarm_time_hr = input("Please input the hours for the alarm \n   ")
         if alarm_time_hr.isdigit():
            if 0 <= int(alarm_time_hr) < 24:
               if len(alarm_time_hr) == 1:
                  alarm_time_hr = "0" + alarm_time_hr
               break
            else:
               print ("Hours must be between 0 and 23")
         else:
            print ("Please enter a number between 0 and 23")
      while True:
         alarm_time_min = input("Please input the minute for the alarm \n   ")
         if not alarm_time_min:
               alarm_time_min = "00"
               break
         if alarm_time_min.isdigit():
            if 0 <= int(alarm_time_min) < 60:
               if len(alarm_time_min) == 1:
                  alarm_time_min = "0" + alarm_time_min
               break
            else:
               print ("Minutes must be between 0 and 59")
         else:
            print ("Please enter a number between 0 and 59")
      alarm_time = alarm_time_hr + ":" + alarm_time_min
      for i in range(7):
         active = input ("Is alarm active on "+weekdays[i] +" (y/N)\n   ").lower()
         if active == "y" or active == "yes":
            dow = dow + weekday_numbers[i]
      repeat = input("Does alarm repeat (y/N)\n   ").lower()
      if repeat == "y" or repeat == "yes":
         dow += 1
      radio_preset = input("Please choose a radio station, input 0 for local music\n   ")
      if radio_preset == "":
         radio_preset = 0
      add_alarm(time = alarm_time, dow = dow , radio = radio_preset )
   if command == "r" or command == "remove":
      print ("Remove")
      remove_alarm()
   if command == "q" or command == "quit":
      print ("Quitting...")
      exit()
 

#!/usr/bin/env python3

from tm1637 import TM1637
from time import time, sleep, localtime

DIO=6
CLK=5
def show_clock(tm):
    t = localtime()
    sleep(1 - time() % 1)
    tm.numbers(t.tm_hour, t.tm_min, False)
    print(t.tm_hour)
tm = TM1637(CLK, DIO)    
tm.brightness(0)
while True:
    show_clock(tm)


#!/usr/bin/env python
'''
Project: pipeline
Aquaponics Web Controller
by Mark Pryor

Version: 0.0.5a
'''

import app
import sqlite3
import time
import os
import RPi.GPIO as GPIO
from datetime import datetime

#Pointer to database file
dbname ='pipeline/db/pipeline.db'

def setup():
    pass

# MAIN FUNCTION FOR RUNNING TIMER.
def run_timer():

    while True:
        conn=sqlite3.connect(dbname)
        curs=conn.cursor()
        for pin in curs.execute("SELECT * FROM times"):
            #Check to see if timer enabled for that pin
            if pin[3] == 1:
                #Grab Current time.
                current_time = datetime.now().time()
                if current_time >= datetime.strptime(pin[1], '%H:%M').time() and current_time <= datetime.strptime(pin[2], '%H:%M').time():
                    if GPIO.input(pin[0]) == GPIO.LOW:
                        print str(pin[0]) + " Already On"
                    else:
                        GPIO.output(pin[0], GPIO.LOW)

                elif current_time <= datetime.strptime(pin[1], '%H:%M').time() or current_time >= datetime.strptime(pin[2], '%H:%M').time():
                    if GPIO.input(pin[0]) == GPIO.HIGH:
                        print str(pin[0]) + " Already Off"
                    else:
                        GPIO.output(pin[0], GPIO.HIGH)
            elif pin[3] == 2:
                pass

            else:
                print str(pin[0]) + ': no timer set.'
        conn.close()

        time.sleep(5)


run_timer()

"""
if __name__ == "__main__":
    try:
        #setup()
        #runtime()


    except KeyboardInterrupt:
        print "Exiting"
"""

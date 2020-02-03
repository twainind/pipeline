#!/usr/bin/env python

'''
Project: pipeline
Aquaponics Web Controller
by Mark Pryor

Version: 0.0.8a
'''
import sqlite3
import os
import time
import glob
import RPi.GPIO as GPIO
from flask import Flask, render_template, request, url_for, redirect


app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


#path
pth="pipeline/"

#DATABASES
dbgpio = "pipeline/db/pipeline.db"
dbtemp = "pipeline/db/pipeline.db"
dbtime = "pipeline/db/pipeline.db"


# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
    12: {'name': 'GPIO 12', 'state': GPIO.HIGH, 'status': "OFF", 'timer':False},
    16: {'name': 'GPIO 16', 'state': GPIO.HIGH, 'status': "OFF", 'timer':False},
    20: {'name': 'GPIO 20', 'state': GPIO.HIGH,  'status': "OFF", 'timer':False},
    21: {'name': 'GPIO 21', 'state': GPIO.HIGH,  'status': "OFF", 'timer':False}
}
## GPIO SETUP ##
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
## END GPIO SETUP ##

#SWITCH FOR TEMPERATURE GRAPH: INITIAL SETTING.
tempMod = '-3 Hours'

temps = {
    1: {'name': 'T1', "TIMESTAMP": [], "TEMP": [], "HUMID": [], "LIMIT": 35.0},
    2: {'name': 'T2', "TIMESTAMP": [], "TEMP": [], "HUMID": [], "LIMIT": 35.0},
    3: {'name': 'T3', "TIMESTAMP": [], "TEMP": [], "HUMID": [], "LIMIT": 35.0}
} # changed temp to dictionary

# Setup device names for pin allocation. 191118
def device_labels():
    with open(pth + 'devices.txt','r') as devnames:
        next(devnames)
        for line in devnames:
            try:
                if int(line[:2]) in pins:
                    pins[int(line[:2])]['name'] = line[3:].strip()
                else:
                    pass
            except:
                if line.split("=")[0][2:] == 'NAME':
                    temps[int(line[1:2])]['name'] = line.split("=")[1]

                elif line.split("=")[0][2:] == 'LIMIT':
                    temps[int(line[1:2])]['LIMIT'] = float(line.split("=")[1])

                else:
                    print "DEVICES.txt - Line Not Found!"
                    pass

######################################################
# Temperature Probe Settings
# READS .db for TEMP

def display_temp_data(time_Delta):

    conn=sqlite3.connect(dbtemp)
    curs=conn.cursor()

    for i in temps:
        temps[i]['TIMESTAMP'] = []
        temps[i]['TEMP'] = []
        temps[i]['HUMID'] = []

    #for row in curs.execute("SELECT * FROM temps;"):
    for row in curs.execute("SELECT * FROM temps WHERE timestamp >= DATETIME('now', 'localtime', (?));", (time_Delta,)):

        #SELECT FROM temps WHERE timestamp IN (SELECT timestamp FROM temps ORDER BY timestamp DESC LIMIT 30)")

        temps[row[0]]['TIMESTAMP'].append(row[1])
        temps[row[0]]['TEMP'].append(row[2])
        temps[row[0]]['HUMID'].append(row[3])
    print temps
    return temps

    conn.close()

######################################################
# END OF TEMP Settings
######################################################

######################################################
# Timer Set Functions
# READS .db for times.
######################################################
def get_timer_status():
    # Sets local dictionary timer values to reflect those from the db.
    conn=sqlite3.connect(dbtime)
    curs=conn.cursor()

    for row in curs.execute("SELECT * FROM times"):
        if row[3] == 0:
            pins[row[0]]['timer'] = False
        elif row[3] == 1:
            pins[row[0]]['timer'] = True
        else:
            print "Error: Pin Status Failure!"

    conn.close()

def set_timer(status, pin):
    #Updates the times table with data collected from timers.html POST
    conn=sqlite3.connect(dbtime)
    curs=conn.cursor()

    curs.execute("UPDATE times SET status = %s WHERE pin = %s;" % (status, pin))

    conn.commit()

    conn.close()

def display_timer_data():
    conn=sqlite3.connect(dbtime)
    curs=conn.cursor()
    times = {}
    lables = ["TIMEON", "TIMEOFF"]

    for row in curs.execute("SELECT * FROM times"):
        times[row[0]] = {lables[0]:str(row[1]),lables[1]:str(row[2])}

    return times
    conn.close()
######################################################
# END OF TIME Settings
######################################################

def set_gpio(state, pin):
#set gpio is only to capture the last user input for the on/off switch and store them in the data base
#In the event of a power failure, get_gpio() will be called upon start-up and the last used settings will be usedself.
    conn=sqlite3.connect(dbtime)
    curs=conn.cursor()

    curs.execute("UPDATE gpio SET status=? WHERE pin=?", (state, pin))

    conn.commit()
    conn.close()

### INITIALISE THIS!! ###

def get_gpio():

    conn=sqlite3.connect(dbgpio)
    curs=conn.cursor()

    for row in curs.execute("SELECT * FROM gpio;"):
        pins[row[0]]['name'] = row[1]

        if row[2] == 0:
            pins[row[0]]['state'] = GPIO.HIGH
            pins[row[0]]['status'] = 'OFF'
            GPIO.output(row[0], GPIO.HIGH)
        elif row[2] == 1:
            pins[row[0]]['state'] = GPIO.LOW
            pins[row[0]]['status'] = 'ON'
            GPIO.output(row[0], GPIO.LOW)
        else:
            pass

    conn.close()
### END OF BEFORE_FIRST_REQUEST ###

@app.route("/")
def main():

    #Get timer status from database.
    get_timer_status()

    # For each pin, read the pin state and store it in the pins dictionary:
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)

    temperature = display_temp_data(tempMod)

    # Put the pin dictionary into the template data dictionary:
    templateData = {
        'pins': pins,
        'temperature': temperature
    }
    # Pass the template data into the template main.html and return it to the user
    return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with the pin number and action in it:


@app.route("/<changePin>/<action>")
def action(changePin, action):

    #Get timer status from database.
    #get_timer_status()

    changePin = int(changePin)
    #deviceName = pins[changePin]['name']

    if action == "on":

        GPIO.output(changePin, GPIO.LOW)

        pins[changePin]['status'] = 'ON'

        set_gpio(1, changePin)


    elif action == "off":

        GPIO.output(changePin, GPIO.HIGH)

        pins[changePin]['status'] = 'OFF'

        set_gpio(0, changePin)



    elif action == "timeon":
        #Change timer to True ie. Turn on timing function. Set_timer db 1
        set_timer(1, changePin)
        pins[changePin]['timer'] = True


    elif action == "timeoff":

        set_timer(0, changePin)
        pins[changePin]['timer'] = False

    temperature = display_temp_data(tempMod)

    return redirect(url_for('main'))

@app.route("/temperatures")
def temperatures():

    temperature = display_temp_data(tempMod)

    templateData = {
        'temperature': temperature
    }
    print temperature
    return render_template('temperatures.html', **templateData)

@app.route("/temperatures/<time_Delta>")
def change_graph(time_Delta):

    global tempMod

    HDM = {
            'H':'Hours',
            'D':'Days',
            'M':'Months'
            }

    if time_Delta[-1:] in HDM:
        print "IF STATEMENT WORKING" + "*" *100
        tempMod = "-" + time_Delta[:-1] + " " + HDM[time_Delta[-1:]]
        temperature = display_temp_data(tempMod)
    else:
        print "ERROR: Not enough time!"



    templateData = {
        'temperature': temperature
    }

    return redirect(url_for('temperatures'))

@app.route("/gpio")
def gpio():

    temperature = display_temp_data(tempMod)

    templateData = {
        'temperature': temperature
    }

    return render_template('gpio.html', **templateData)

@app.route("/timers")
def timers():

    temperature = display_temp_data(tempMod)
    timesData = display_timer_data()

    templateData = {
        'temperature': temperature,
        'timesData': timesData,
        'pins': pins
    }

    return render_template('timers.html', **templateData)


@app.route("/update-timerdb/<pin>", methods = ["POST"])
def update_timerdb(pin):

    ontime = request.form.get('%s.ontime' % (pin))
    offtime = request.form.get('%s.offtime' % (pin))

    conn=sqlite3.connect(dbtime)
    curs=conn.cursor()

    curs.execute("UPDATE times SET timeon=? WHERE pin=?", (ontime, pin))
    curs.execute("UPDATE times SET timeoff=? WHERE pin=?", (offtime, pin))

    conn.commit()
    conn.close()

    temperature = display_temp_data(tempMod)
    timesData = display_timer_data()


    return redirect(url_for('timers'))



if __name__ == "__main__":
    get_gpio()
    device_labels()
    app.run(host='0.0.0.0', port=80, debug=True)

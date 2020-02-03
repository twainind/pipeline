#!/usr/bin/env python

'''
Project: pipeline
Aquaponics Web Controller
by Mark Pryor

Version: 0.0.5a
'''
import sqlite3
import os
import time
import glob
import Adafruit_DHT as dht

# global variables
dbname='pipeline/db/pipeline.db'
rest=(15*60)-1

def dht22():
    h, t = dht.read_retry(dht.DHT22, 18)

    if h is not None and t is not None:
        log_temperature(3, round(t, 2), round(h, 2))
        return True
    else:
        print "DHT22 SENSOR: Failed to get reading, check connection"
        pass

# store the temperature in the database
def log_temperature(id, temp, hum=None):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    curs.execute("INSERT INTO temps VALUES((?), datetime('now', 'localtime'), (?), (?))", (id, temp, hum))
    #curs.execute("DELETE FROM temps WHERE timestamp NOT IN (SELECT timestamp FROM temps ORDER BY timestamp DESC LIMIT 30)")
    conn.commit()

    conn.close()


# get temerature
# returns None on error, or the temperature as a float
def get_temp(devicefile):

    try:
        fileobj = open(devicefile,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        return None

    # get the status from the end of line 1
    #status = lines[0][-4:-1]

    if 'YES' in lines[0].split():
        #print status
        tempvalue = (float(lines[1].split()[-1].split("=")[1]))/1000

        return float("%.2f" % tempvalue)
    else:
        print "DEVICEFILE: Error reading sensor."
        return None



# main function
# This is where the program starts
def run_temp():
    # Run DHT22 sensor code
    dht = dht22()
    # enable kernel modules
    os.system('sudo modprobe w1-gpio')
    os.system('sudo modprobe w1-therm')

    # Detect devices

    if glob.glob('/sys/bus/w1/devices/28*'):
        # search for a device file that starts with 28
        devicelist = glob.glob('/sys/bus/w1/devices/28*')
        if devicelist=='':
            return None
        else:
            for i in devicelist:
                # append /w1slave to the device file
                w1devicefile = i + '/w1_slave'
                # get the temperature from the device file
                temperature = get_temp(w1devicefile)
                if temperature != None:
                    log_temperature(devicelist.index(i) + 1, temperature)
                else:
                    # Sometimes reads fail on the first attempt
                    # so we need to retry
                    temperature = get_temp(w1devicefile)
                    log_temperature(devicelist.index(i) + 1, temperature)
                        # Store the temperature in the database

    else:
        print "1-WIRE INTERFACE: No temperature devices found!"
        if dht == True:
            pass
        else:
            exit()

if __name__=="__main__":
    try:
        while True:
            run_temp()
            time.sleep(rest)
            #display_data()
    except KeyboardInterrupt:
        print "Exiting"

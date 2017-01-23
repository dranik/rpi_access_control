import sqlite3
import datetime
import time
import logging

def verify(input):
    red_blink
    if input == '0': return
    dbRaw = sqlite3.connect('onboard.db')
    db = dbRaw.cursor()
    db.execute("SELECT * FROM ACCESSLIST WHERE checksum = ?",(input, ))
    entry = db.fetchone()
    dbRaw.commit()
    if entry is None:
        return
    if entry[4] == 'Surveyor':
        grant()
    if entry[4] == 'Pass':
        time_from = datetime.datetime.strptime(entry[2], '%Y-%m-%dT%H:%M:%S.%fZ')
        time_to = datetime.datetime.strptime(entry[3], '%Y-%m-%dT%H:%M:%S.%fZ')
        if datetime.datetime.utcnow()>time_from and datetime.datetime.utcnow()<time_to:
            grant()
    if entry[4] == 'Appointment' and not entry[5]:
        time_from = datetime.datetime.strptime(entry[2], '%Y-%m-%dT%H:%M:%S.%fZ')
        time_to = datetime.datetime.strptime(entry[3], '%Y-%m-%dT%H:%M:%S.%fZ')
        if datetime.datetime.utcnow()>time_from and datetime.datetime.utcnow()<time_to:
            db = dbRaw.cursor()
            db.execute("UPDATE ACCESSLIST SET sync = 1 WHERE checksum = ? AND ext_id = ? AND type = ?",(input,entry[0],entry[4]))
            dbRaw.commit()
            grant()


def grant():
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.OUT, initial = False)
        GPIO.output(12,True)
        time.sleep(10)
        GPIO.output(12, False)
        GPIO.cleanup()
        logging.info('Access granted')
    except:
        logging.error('Failed to grant access. Probably you are running the script on non-RPi device or RPi.GPIO is not present')


def red_blink():
	try:
		import RPi.GPIO as GPIO
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(16, GPIO.OUT, initial = False)
		GPIO.output(16, True)
		time.sleep(2)
		GPIO.output(16, True)
	except:
		return False

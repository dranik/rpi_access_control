import sqlite3
import logging
import sysv_ipc
from hashlib import sha256
import hmac
import requests
from email.utils import formatdate
import json
import time
import datetime


def sync(memory_key, server):
    memory = sysv_ipc.SharedMemory(memory_key)
    memory.attach()
    logging.info('DB sync starts')
    logging.info('Serial: '+getserial())
    dbRaw = sqlite3.connect('onboard.db')
    db = dbRaw.cursor()
    db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ACCESSLIST';")
    if db.fetchone() == None:
        db.execute("CREATE TABLE ACCESSLIST(ext_id integer, checksum text, start_time integer, end_time integer, type text, sync integer)")
    dbRaw.commit()
    while True:
        recieve(server, dbRaw)
        decimate(server, dbRaw)
        time.sleep(5)
    return


def getserial():
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:6]=='Serial':
                cpuserial = line[10:26]
        f.close()
        cpuserial = "000-" + cpuserial
    except:
        cpuserial = "ERROR000000000"
    return cpuserial


def recieve(server, dbRaw):
    data = json.loads(rx_request(server))
    db = dbRaw.cursor()
    if data:
        for entry in data:
            db.execute("SELECT * FROM ACCESSLIST WHERE type=? AND ext_id=?",(entry[u'type'],entry[u'id']))
            row = db.fetchone()
            if row == None:
                data = (entry[u'id'], entry[u'checksum'], entry[u'time_from'], entry[u'time_to'], entry[u'type'], False)
                db.execute("INSERT INTO ACCESSLIST  VALUES (?,?,?,?,?,?)", data)
            else:
                if row[1] != entry[u'checksum']:
                    db.execute("DELETE FROM ACCESSLIST WHERE type=? AND ext_id=? AND checksum = ?",(entry[u'type'],entry[u'id'],entry[u'checksum']))
                    data = (entry[u'id'], entry[u'checksum'], entry[u'time_from'], entry[u'time_to'], entry[u'type'], False)
                    db.execute("INSERT INTO ACCESSLIST  VALUES (?,?,?,?,?,?)", data)
        #for row in db.execute("SELECT * FROM ACCESSLIST"):
        #    print row
        dbRaw.commit()



def decimate(server, dbRaw):
    db = dbRaw.cursor()
    ids = []
    for row in db.execute("SELECT * FROM ACCESSLIST WHERE NOT sync=0"):
        ids.append({'id':row[0]})
    if ids != []:
        if tx_request(server, ids):
            for entry in ids:
                db.execute("DELETE FROM ACCESSLIST WHERE type='Appointment' AND ext_id=?", (entry['id'], ))
    for row in db.execute("SELECT * FROM ACCESSLIST WHERE (type='Appointment' OR type='Pass') AND sync=0"):
        time_to = datetime.datetime.strptime(row[3], '%Y-%m-%dT%H:%M:%S.%fZ')
        if time_to < datetime.datetime.utcnow():
            db.execute("DELETE FROM ACCESSLIST WHERE type=? AND ext_id=?", (row[4],row[0]))
    dbRaw.commit()


def rx_request(server):
    path = '/devices'
    headers = generate_headers('POST',path)
    try:
        response = requests.post(server+path, headers=headers, json={'id' : getserial()})
    except:
        return json.dumps(False)
    logging.info(response)
    logging.info(response.content)
    if response.status_code == 200:
        return response.content
    else:
        return json.dumps(False)


def tx_request(server, data):
    path = '/devices/'+getserial()
    headers = generate_headers('PUT', path)
    try:
        response = requests.put(server+path, headers=headers, data=json.dumps(data))
    except:
        return False
    if response.status_code == 200 or response.status_code == 422:
        return True
    else:
        return False


def generate_headers(method, path):
    date = formatdate(timeval=None, localtime=False, usegmt=True)
    hwid = getserial()
    raw = hwid + date + path + method
    key = 'such_a_secret_key'
    hashed = hmac.new(key, raw, sha256)
    headers = {'Authorization': hwid + ':' + hashed.digest().encode("base64").rstrip('\n'), 'Date': date}
    return headers

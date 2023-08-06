import time
import snowflake
import struct
import serial
import serial.tools.list_ports
import socket as SOCKETS
import zmq
import random
import multiprocessing
import os
import platform
import subprocess
import sys
import traceback
import json
import psutil
import math
import requests
import ftplib
import fnmatch
import ntplib
import argparse
import logging
import sync
import uuid
from datetime import datetime
from getpass import getpass
from numpy import linspace

base_dir = '.'
if getattr(sys, 'frozen', False):
    base_dir = os.path.join(sys._MEIPASS)

# Module multiprocessing is organized differently in Python 3.4+
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking

if sys.platform.startswith('win'):
    # First define a modified version of Popen.
    class _PopenX(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_PopenX, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    # Second override 'Popen' class with our modified version.
    forking.Popen = _PopenX


class daqbrokerClient:
    """
    Main client application class. This class can be used in the Python CLI to start the client application
    or to register a machine with existing DAQBroker servers

    :ivar name: (string) name of the machine that will be used to identify it by the users. Defaults to platform.node()
    :ivar commport: (integer) the network port for the main part of the client application. Defaults to 9091
    :ivar logport: (integer) the network port for the logging process of the application. Defaults to 9094

    """
    def __init__(self, name=platform.node(), commport=9091, logport=9094, **kwargs):
        self.name = name
        self.logport = logport
        self.commport = commport
        self.shareStr = str(uuid.uuid4())[0:8]

    def start(self):
        """
        Function to start the main client application

        .. warning::

            This is a long running process and blocks execution of the main task, it should therefore be called on a separate process.

        """
        #shareStr = str(uuid.uuid4())[0:8]
        print('SETUP LOGGER')
        p4 = multiprocessing.Process(target=logServer, args=(self.logport,))
        p4.start()
        print('STARTED LOGGER')
        time.sleep(1)
        print("SETUP MCAST")
        p5 = multiprocessing.Process(
            target=mCastListen,
            args=(
                snowflake.make_snowflake(
                    snowflake_file=os.path.join(base_dir, 'foo')),
                self.name,
                self.commport,
                self.shareStr))
        p5.start()
        print("STARTED LOGGER")
        time.sleep(1)
        print('SETUP CONSUMER')
        print("Share str : " + self.shareStr)
        consumer(self.commport, self.logport)

    def register(self, server=None, username=None, password=None):
        """
        This function allows registering a client application with a DAQBroker server. This function can
        be used to register with servers outside the local network. This function provides an interactive command
        line interface to insert the relevant parameters for registering with a server that were not provided
        as parameters

        :ivar server (optiona): (string) Server URL
        :ivar username (optional): (string) DAQBroker login username
        :ivar password (optional): (string) DAQBroker login password

        :return: (boolean) True if registration was completed successfully. False if not. Prints the error of the
        registration request on failure

        """
        if server:
            serverName = server
        else:
            serverName = input('Input the server URL (serverName.com | ip.ip.ip.ip)')
        if username:
            loginU = server
        else:
            loginU = input('Insert daqbroker username:')
        if password:
            loginP = password
        else:
            loginP = getpass('Insert daqbroker password:')
        toSend = {
            'ID': id,
            'name': self.name,
            'username': loginU,
            'password': loginP,
            'port': self.commport}
        url = 'http://' + serverName + '/daqbroker/registerNode'
        # print(url)
        # print(toSend)
        r = requests.post(url, data=toSend)
        # print(r)
        # print(r.text)
        # print(r.json())
        if r.status_code == 200:
            print(
                "Successfully registered with " +
                serverName +
                " at port ")
            return True
        else:
            print(
                "There was a problem registering your client, please contact your system administrator\n\n")
            print(r.text)
            return False
    # Gotta deal with new and old. Should also return the myself, don't know
    # why, maybe not useful


# Gets all the metadata from an instrument, sorts only the most recent and
# from different example files and parses that data
def syncInst(
        servAddr,
        sendBackPort,
        instMeta,
        instrument,
        metaid,
        metaType,
        database,
        logPort,
        lockList,
        backupPort,
        backupUser,
        backupPass,
        serverDB,
        engineDB,
        metaName):
    try:
        for i, lock in enumerate(lockList):
            if lock['metaid'] == metaid:
                break
        theInstLock = lockList[i]
        theInstLock['locked'] = True
        lockList[i] = theInstLock
        consumer_sender = False
        context = zmq.Context()
        theLogSocket = context.socket(zmq.REQ)
        theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
        toSend = {
            'req': 'LOG',
            'type': 'INFO',
            'process': 'CONSUMER',
            'message': "SYNCING - " + instrument}
        theLogSocket.send(json.dumps(toSend).encode())
        theLogSocket.close()
        consumer_sender = context.socket(zmq.PUSH)
        consumer_sender.setsockopt(zmq.LINGER, 1000)
        machine = "tcp://" + servAddr + ":" + str(sendBackPort)
        consumer_sender.connect(machine)
        errors = []
        sync.syncDirectory(
            servAddr,
            database,
            instrument,
            instMeta,
            backupPort,
            backupUser,
            backupPass,
            metaName,
            serverDB)
    except Exception as e:
        # traceback.print_exc()
        _, _, tb = sys.exc_info()
        tbResult = traceback.format_list(traceback.extract_tb(tb)[-1:])[-1]
        filename = tbResult.split(',')[0].replace('File', '').replace('"', '')
        lineno = tbResult.split(',')[1].replace('line', '')
        funname = tbResult.split(',')[2].replace('\n', '').replace(' in ', '')
        line = str(e)
        theLogSocket = context.socket(zmq.REQ)
        theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
        toSend = {
            'req': 'LOG',
            'type': 'ERROR',
            'process': 'SYNCINST',
            'message': str(e),
            'filename': filename,
            'lineno': lineno,
            'funname': funname,
            'line': line}
        theLogSocket.send(json.dumps(toSend).encode())
        theLogSocket.close()
    finally:
        theInstLock = lockList[i]
        theInstLock['locked'] = False
        theInstLock['counts'] = 0
        lockList[i] = theInstLock
        if consumer_sender:
            endMessage = {
                "server": serverDB,
                "engine": engineDB,
                "database": database,
                "instrument": instrument,
                "metaid": metaid,
                "metaName": metaName,
                "order": "METASYNCOVER",
                "errors": errors}
            consumer_sender.send_json(endMessage)
            consumer_sender.close()


def logServer(port):
    logging.basicConfig(
        filename=os.path.join(base_dir, 'logFileAgent.log'),
        level=logging.DEBUG,
        format='')
    logging.info(datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S") +
                 " [LOGGER][INFO][logServer] : started logging server")
    context = zmq.Context()
    theSocket = context.socket(zmq.ROUTER)
    logLvls = {
        'info': logging.INFO,
        'error': logging.ERROR,
        'warning': logging.warning,
        'debug': logging.debug}
    theSocket.bind("tcp://127.0.0.1:" + str(port))
    while True:
        #  Wait for next request from client
        message = False
        try:
            message = theSocket.recv_json()
            logReq = message
            if 'req' in logReq:
                if logReq['req'] == 'LOG':
                    if not (logReq['type'] == 'ERROR'):
                        if 'method' in logReq:
                            logMessage = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S") + \
                                ' [' + logReq['process'] + '][' + logReq['method'] + '][' + logReq['type'] + '] : ' + logReq['message']
                        else:
                            logMessage = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S") + \
                                ' [' + logReq['process'] + '][' + logReq['type'] + '] : ' + logReq['message']
                    else:
                        logMessage = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S") + \
                            ' [' + logReq['process'] + '][' + logReq['type'] + '][' + logReq['filename'] + '][' + logReq['lineno'] + '][' + logReq['funname'] + '] : ' + logReq['line']
                    logging.info(logMessage)
        except Exception as e:
            if message:
                _, _, tb = sys.exc_info()
                tbResult = traceback.format_list(
                    traceback.extract_tb(tb)[-1:])[-1]
                filename = tbResult.split(',')[0].replace(
                    'File', '').replace('"', '')
                lineno = tbResult.split(',')[1].replace('line', '')
                funname = tbResult.split(',')[2].replace(
                    '\n', '').replace(' in ', '')
                logMessage = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S") + \
                    ' [LOGGER][ERROR][' + filename + '+][' + lineno + '][' + funname + '] : ' + str(e)
                logging.info(logMessage)


def getNTPTIme(server, timeback):
    try:
        c = ntplib.NTPClient()
        timeback.value = c.request(server).tx_time
    except BaseException:
        # traceback.print_exc()
        timeback.value = 0


def getLocalTime(timeback):
    timeback.value = time.time()


def getMachineDetails(extra):
    if 'serverNTP' in extra:
        if not extra['serverNTP'] == '':
            try:
                serverTime = multiprocessing.Value('d', 0.0)
                localTime = multiprocessing.Value('d', 0.0)
                time1 = time.time()
                p1 = multiprocessing.Process(
                    target=getNTPTIme, args=(
                        extra['serverNTP'], serverTime))
                p2 = multiprocessing.Process(
                    target=getLocalTime, args=(localTime,))
                p1.start()
                p2.start()
                p1.join()
                p2.join()
                time2 = time.time()
                theServerTime = serverTime.value
                theLocalTime = localTime.value
                timeDiff = theServerTime - theLocalTime
                timeDiffProcs = time2 - time1
                if(platform.system() == 'Windows'):  # Running on windows machine
                    theSetReturn = _win_set_time(timeDiff)
                elif(platform.system() == 'Linux'):  # Running on linux machine
                    theSetReturn = _linux_set_time(timeDiff)
                if theSetReturn:
                    theTimeLocal = time.time()
                    time2 = time.time()
                    timeDiff = time2 - theTimeLocal
                    theTimeDifference = timeDiff
                else:
                    theTimeLocal = time.time()
                    theTimeDifference = 'N/A'
            except Exception as e:
                # traceback.print_exc()
                theTimeDifference = 'N/A'
        else:
            theTimeDifference = 'N/A'
    else:
        theTimeDifference = 'N/A'
    theTimeLocal = time.time()
    psutil.cpu_percent()
    result = {}
    disks = psutil.disk_partitions()
    ram = psutil.virtual_memory()
    result["ram"] = {}
    result["ram"]["total"] = getSizeData(ram.total)
    result["ram"]["available"] = getSizeData(ram.available)
    rom = []
    result["rom"] = []
    temp = []
    ioTemp = psutil.disk_io_counters(perdisk=True)
    for i, value in enumerate(disks):
        try:
            rom.append(psutil.disk_usage(disks[i].mountpoint))
            result["rom"].append({"total": getSizeData(rom[len(rom) - 1].total),
                                  "free": getSizeData(rom[len(rom) - 1].free),
                                  "device": disks[i].device,
                                  "io": ioTemp[list(ioTemp.keys())[i]]._asdict()})
        except BaseException:
            poop = 'poop'
    result["cpu"] = psutil.cpu_percent(interval=0.5)
    result["cpuMulti"] = psutil.cpu_percent(percpu=True)
    result["timeInfo"] = {
        'localTime': theTimeLocal,
        'serverDifference': theTimeDifference}
    return result


def getSizeData(number):
    result = {}
    i = 0
    while number / (math.pow(2, 10 * i)) > 1:
        i = i + 1
        continue
    if i == 0:
        type = "B"
    elif i == 1:
        type = "B"
    elif i == 2:
        type = "kB"
    elif i == 3:
        type = "MB"
    elif i == 4:
        type = "GB"
    elif i == 5:
        type = "TB"
    elif i == 6:
        type = "PB"
    elif i > 6:
        type = "FUCKTON"
    if i > 0:
        result["number"] = number / (math.pow(2, 10 * (i - 1)))
    else:
        result["number"] = number / (math.pow(2, 10 * i))
    result["type"] = type
    return result


def getPortData(port, parseInterval, command):
    try:
        client = SOCKETS.socket(SOCKETS.AF_INET, SOCKETS.SOCK_STREAM)
        if(not command == ""):
            client.settimeout(5)
        else:
            client.settimeout(parseInterval)
        server_address = ('localhost', port)
        client.connect(server_address)
        if(not command == ""):
            client.send(command.encode())
        time.sleep(1)
        reply = ""
        recieved = client.recv(4096)
        reply = reply + recieved.decode()
        return {'status': 0, 'error': "", "reply": reply}
    except Exception as e:
        # traceback.print_exc()
        return {'status': -1, 'error': str(e), "reply": ""}


def getCOMData(device, parseInterval, command, baud, par, bytes, stop):
    try:
        if stop == "0":
            stopBits = serial.STOPBITS_ONE
        if stop == "1":
            stopBits = serial.STOPBITS_ONE_POINT_FIVE
        if stop == "2":
            stopBits = serial.STOPBITS_ONE_TWO
        if(not command == ""):
            ser = serial.Serial(
                device,
                baudrate=baud,
                bytesize=bytes,
                parity=par,
                stopbits=stopBits,
                timeout=5)
        else:
            ser = serial.Serial(
                device,
                baudrate=baud,
                bytesize=bytes,
                parity=par,
                stopbits=stopBits,
                timeout=parseInterval / 2)
        ser.flush()
        if(not command == ""):
            ser.write(command.encode())
        while not ser.readable():  # Should stay here before being readable, should leave when becomes readable. Should IMMEDIATELY become readable
            continue
        data = ser.read(1000000).decode()
        return {'status': 0, 'error': "", "reply": data}
    except Exception as e:
        traceback.print_exc()
        return {'status': -1, 'error': str(e), "reply": ""}


def getPeripheralData(
        server,
        database,
        instrument,
        meta,
        type,
        backupPort,
        backupUser,
        backupPass,
        metaName,
        metaid,
        sendBackPort,
        serverDB,
        engineDB,
        channels,
        logPort,
        lockList):
    try:
        for i, lock in enumerate(lockList):
            if lock['metaid'] == metaid:
                break
        theInstLock = lockList[i]
        theInstLock['locked'] = True
        lockList[i] = theInstLock
        errors = []
        context = zmq.Context()
        timeStart = time.time()
        consumer_sender = False
        consumer_sender = context.socket(zmq.PUSH)
        consumer_sender.setsockopt(zmq.LINGER, 1000)
        machine = "tcp://" + server + ":" + str(sendBackPort)
        consumer_sender.connect(machine)
        if not os.path.isdir(os.path.join('temp', server, instrument)):
            os.makedirs(os.path.join('temp', server, instrument))
        theFile = open(os.path.join('temp', server, instrument, metaName + '_' + \
                       str(datetime.now().day) + '_' + str(datetime.now().hour) + '.tmp'), 'a')
        if type == 1:
            returned = getPortData(int(meta["port"]), int(
                meta["parseInterval"]), meta["command"])
            timeEnd = time.time()
            if returned["status"] == 0:
                if 'parsingInfo' in meta:
                    lines = returned["reply"].split('\n')
                    for i, line in enumerate(lines):
                        elements = line.split(meta["parsingInfo"]["separator"])
                        trueLine = [elements[i][chann["remarks"]["min"]:chann["remarks"]["max"]]
                                    for i, chann in enumerate(channels) if i < len(elements)]
                        lines[i] = meta["parsingInfo"]["separator"].join(
                            trueLine)
                        if not meta["parsingInfo"]["timeProvided"]:
                            times = list(
                                linspace(
                                    timeStart,
                                    timeEnd,
                                    len(lines)))
                            lines[i] = str(
                                times[i]) + meta["parsingInfo"]["separator"] + lines[i]
                    theFile.write(lines[i] + '\n')
        elif type == 2:
            returned = getCOMData(
                meta["device"], int(
                    meta["parseInterval"]), meta["command"], int(
                    meta["baudRates"]), meta["parity"], int(
                    meta["dataBits"]), meta["stopBits"])
            timeEnd = time.time()
            if returned["status"] == 0:
                if 'parsingInfo' in meta:
                    if meta["parsingInfo"]["terminator"] == '':
                        lines = returned["reply"].split('\n')
                    else:
                        lines = returned["reply"].split(
                            meta["parsingInfo"]["terminator"])
                    for i, line in enumerate(lines):
                        elements = line.split(meta["parsingInfo"]["separator"])
                        trueLine = [elements[i][chann["remarks"]["min"]:chann["remarks"]["max"]]
                                    for i, chann in enumerate(channels) if i < len(elements)]
                        lines[i] = meta["parsingInfo"]["separator"].join(
                            trueLine)
                        if not meta["parsingInfo"]["timeProvided"]:
                            times = list(
                                linspace(
                                    timeStart,
                                    timeEnd,
                                    len(lines)))
                            lines[i] = str(
                                times[i]) + meta["parsingInfo"]["separator"] + lines[i]
                        theFile.write(lines[i] + '\n')
        toSyncMeta = {
            'getNested': False,
            'path': os.path.join(
                'temp',
                server,
                instrument),
            'extension': 'tmp',
            'pattern': metaName}
        theFile.close()
        sync.syncDirectory(
            server,
            database,
            instrument,
            toSyncMeta,
            backupPort,
            backupUser,
            backupPass,
            metaName)
    except Exception as e:
        traceback.print_exc()
        errors.append(str(e))
        poop = "pooop"
    finally:
        theInstLock = lockList[i]
        theInstLock['locked'] = False
        theInstLock['counts'] = 0
        lockList[i] = theInstLock
        if consumer_sender:
            endMessage = {
                "server": serverDB,
                "engine": engineDB,
                "database": database,
                "instrument": instrument,
                "metaid": metaid,
                "metaName": metaName,
                "order": "METASYNCOVER",
                "errors": errors}
            consumer_sender.send_json(endMessage)
            consumer_sender.close()


def _win_set_time(timeOffset):
    try:
        #import pywin32
        timestamp = time.time() + timeOffset
        import win32api
        # http://timgolden.me.uk/pywin32-docs/win32api__SetSystemTime_meth.html
        # pywin32.SetSystemTime(year, month , dayOfWeek , day , hour , minute , second , millseconds )
        #win32api.SetSystemTime( time_tuple[:2] + (dayOfWeek,) + time_tuple[2:])
        year = int(datetime.utcfromtimestamp(int(timestamp)).strftime('%Y'))
        month = int(datetime.utcfromtimestamp(timestamp).strftime('%m'))
        dayOfWeek = int(datetime.utcfromtimestamp(timestamp).strftime('%w'))
        day = int(datetime.utcfromtimestamp(timestamp).strftime('%d'))
        hour = int(datetime.utcfromtimestamp(timestamp).strftime('%H'))
        minute = int(datetime.utcfromtimestamp(timestamp).strftime('%M'))
        second = int(datetime.utcfromtimestamp(timestamp).strftime('%S'))
        milliseconds = int((timestamp - int(timestamp)) * 1000)
        win32api.SetSystemTime(
            year,
            month,
            0,
            day,
            hour,
            minute,
            second,
            milliseconds)
        return True
    except BaseException:
        # traceback.print_exc()
        return False


def _linux_set_time(timeOffset):
    try:
        timestamp = time.time() + timeOffset
        toRun = 'date +%s -s @' + str(int(timestamp))
        # print(toRun)
        a = subprocess.call(
            toRun.split(' '),
            stderr=subprocess.DEVNULL,
            stdout=subprocess.PIPE)
        if a == 0:
            return True
        else:
            return False
    except BaseException:
        # print(toRun)
        # traceback.print_exc()
        return False


def consumer(port, logPort):
    context = zmq.Context()
    theLogSocket = context.socket(zmq.REQ)
    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
    toSend = {'req': 'LOG', 'type': 'INFO', 'process': 'CONSUMER',
              'message': "STARTED CONSUMER ON PORT- " + str(port)}
    theLogSocket.send(json.dumps(toSend).encode())
    theLogSocket.close()
    # recieve work
    consumer_receiver = context.socket(zmq.PULL)
    machine = "tcp://*:" + str(port)
    # print(machine)
    consumer_receiver.bind(machine)
    # send work
    processes = []
    manager = multiprocessing.Manager()
    lockList = manager.list()
    while True:
        try:
            data = consumer_receiver.recv_json()
            if 'order' in data:
                if data['order'] == 'update':
                    theLogSocket = context.socket(zmq.REQ)
                    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                    toSend = {
                        'req': 'LOG',
                        'type': 'INFO',
                        'process': 'CONSUMER',
                        'message': "UPDATING NODE INFO"}
                    theLogSocket.send(json.dumps(toSend).encode())
                    theLogSocket.close()
                    consumer_sender = context.socket(zmq.PUSH)
                    consumer_sender.setsockopt(zmq.LINGER, 1000)
                    machine = "tcp://" + \
                        data['server'] + ":" + str(data['sendBack'])
                    consumer_sender.connect(machine)
                    if(not (data['extra']['serverNTP'] == "") and not (data['extra']['serverNTP'] == "NONE") and data['extra']["tSync"] == "1"):
                        details = getMachineDetails(data['extra'])
                        if details["timeInfo"]['serverDifference'] == 'N/A':
                            theLogSocket = context.socket(zmq.REQ)
                            theLogSocket.connect(
                                "tcp://127.0.0.1:" + str(logPort))
                            #toSend={'req':'LOG','type':'ERROR','process':'CONSUMER','message':"could not syncronize computer time"}
                            toSend = {
                                'req': 'LOG',
                                'type': 'ERROR',
                                'process': 'CONSUMER',
                                'message': "could not syncronize computer time",
                                'filename': 'consumer',
                                'lineno': '317',
                                'funname': 'getMachineDetails',
                                'line': "details=getMachineDetails(data['extra'])"}
                            theLogSocket.send(json.dumps(toSend).encode())
                            theLogSocket.close()
                    else:
                        details = getMachineDetails({})
                        # details={}
                    message = {
                        'order': 'DETAILSOVER',
                        'theNode': data['theNode'],
                        'port': port,
                        'details': details}
                    consumer_sender.send_json(message)
                    consumer_sender.close()
                elif data["order"] == "SYNC":
                    insts = []
                    for directive in data["directives"]:
                        # print(directive)
                        foundInstLock = False
                        for i, lock in enumerate(lockList):
                            if lock['metaid'] == directive["metaid"]:
                                foundInstLock = True
                                break
                        if not foundInstLock:
                            lockList.append(
                                {'metaid': directive["metaid"], 'locked': False, 'counts': 0})
                            i = len(lockList) - 1
                        if(not lockList[i]['locked']):
                            if directive["type"] == 0:
                                insts.append(directive["instrument"])
                                g = multiprocessing.Process(
                                    target=syncInst,
                                    args=(
                                        directive['server'],
                                        directive['sendBackPort'],
                                        directive["remarks"],
                                        directive["instrument"],
                                        directive["metaid"],
                                        directive["type"],
                                        directive["database"],
                                        logPort,
                                        lockList,
                                        directive["backupPort"],
                                        directive["backupUser"],
                                        directive["backupPass"],
                                        directive["serverDB"],
                                        directive["engine"],
                                        directive["metaName"]))
                            if directive["type"] == 1 or directive["type"] == 2:
                                g = multiprocessing.Process(
                                    target=getPeripheralData,
                                    args=(
                                        directive['server'],
                                        directive["database"],
                                        directive["instrument"],
                                        directive["remarks"],
                                        directive["type"],
                                        directive["backupPort"],
                                        directive["backupUser"],
                                        directive["backupPass"],
                                        directive["metaName"],
                                        directive["metaid"],
                                        directive['sendBackPort'],
                                        directive["serverDB"],
                                        directive["engine"],
                                        directive["channels"],
                                        logPort,
                                        lockList))
                                # server,database,instrument,meta,type,backupPort,backupUser,backupPass,metaName,metaid,sendBackPort,serverDB,engineDB,channels,logPort,lockList
                            g.start()
                elif data["order"] == "GETPORTDATA":
                    machine = "tcp://" + \
                        data['server'] + ":" + str(data['sendBack'])
                    portData = getPortData(
                        data["port"], data["parseInterval"], data["command"])
                    consumer_sender = context.socket(zmq.REQ)
                    consumer_sender.setsockopt(zmq.LINGER, 1000)
                    message = {'order': 'PORTDATA', 'portData': portData}
                    consumer_sender.connect(machine)
                    consumer_sender.send_json(message)
                    consumer_sender.close()
                elif data["order"] == "GETCOMMPORTS":
                    machine = "tcp://" + \
                        data['server'] + ":" + str(data['sendBack'])
                    consumer_sender = context.socket(zmq.REQ)
                    consumer_sender.setsockopt(zmq.LINGER, 1000)
                    portData = []
                    for port in serial.tools.list_ports.comports():
                        portData.append({'device': port.device,
                                         'info': port.description,
                                         'hwid': port.hwid,
                                         'vid': port.vid,
                                         'serial': port.serial_number,
                                         'manufacturer': port.manufacturer})
                    message = {'order': 'COMMPORTS', 'portData': portData}
                    consumer_sender.connect(machine)
                    consumer_sender.send_json(message)
                    consumer_sender.close()
        except Exception as e:
            _, _, tb = sys.exc_info()
            tbResult = traceback.format_list(traceback.extract_tb(tb)[-1:])[-1]
            filename = tbResult.split(',')[0].replace(
                'File', '').replace('"', '')
            lineno = tbResult.split(',')[1].replace('line', '')
            funname = tbResult.split(',')[2].replace(
                '\n', '').replace(' in ', '')
            line = str(e)
            theLogSocket = context.socket(zmq.REQ)
            theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
            toSend = {
                'req': 'LOG',
                'type': 'ERROR',
                'process': 'CONSUMER',
                'message': str(e),
                'filename': filename,
                'lineno': lineno,
                'funname': funname,
                'line': line}
            theLogSocket.send(json.dumps(toSend).encode())
            theLogSocket.close()


def mCastListen(id, node, commport, shareStr):
    multicast_group = '224.224.224.224'
    server_address = ('', 10090)

    # Create the socket
    sock = SOCKETS.socket(SOCKETS.AF_INET, SOCKETS.SOCK_DGRAM)

    # Bind to the server address
    sock.bind(server_address)

    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
    group = SOCKETS.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, SOCKETS.INADDR_ANY)
    sock.setsockopt(SOCKETS.IPPROTO_IP, SOCKETS.IP_ADD_MEMBERSHIP, mreq)

    # Receive/respond loop
    while True:
        data, address = sock.recvfrom(1024)
        try:
            processed = json.loads(data.decode())
            if 'message' in processed:
                if processed["message"] == 'show':
                    details = getMachineDetails(processed["ntp"])
                    toReply = {
                        'id': id,
                        'node': node,
                        'details': details,
                        'serverAddr': address[0],
                        'port': commport}
                    sock.sendto(json.dumps(toReply).encode(), address)
                elif processed["message"] == 'test':
                    if processed["idTest"] == id and processed["shareStr"] == shareStr:
                        details = getMachineDetails({})
                        toReply = {
                            'result': True,
                            'id': id,
                            'node': {
                                'id': id,
                                'node': node,
                                'details': details,
                                'serverAddr': address[0],
                                'port': commport}}
                        sock.sendto(json.dumps(toReply).encode(), address)
        except BaseException:
            traceback.print_exc()
            continue


if __name__ == "__main__":
    multiprocessing.freeze_support()
    theArguments = ['name', 'commport', 'logport', 'action']
    obj = {}
    if len(sys.argv) < 6:
        for i, val in enumerate(sys.argv):
            if i == len(theArguments) + 1:
                break
            if i < 1:
                continue
            obj[theArguments[i - 1]] = val
    else:
        sys.exit(
            "Usage:\n\tdaqbrokerClient name commport logport action\nOr:\n\tdaqbrokerClient name commport logport\nOr:\n\tdaqbrokerClient name commport\nOr:\n\tdaqbrokerClient name\nOr:\n\tdaqbrokerClient")
    if os.path.isfile(os.path.join(base_dir, 'pid')):
        with open(os.path.join(base_dir, 'pid'), 'r') as f:
            existingPID = f.read().strip('\n').strip('\r').strip('\n')
        processExists = False
        if existingPID:
            if psutil.pid_exists(int(existingPID)):
                processExists = True
        print(existingPID)
        if not processExists:
            with open(os.path.join(base_dir, 'pid'), 'w') as f:
                f.write(str(os.getpid()))
                f.flush()
            newClient = daqbrokerClient(**obj)
            if 'action' not in obj:
                obj['action'] = None
            if obj["action"] == 'register':
                newClient.register()
            newClient.start()
        else:
            sys.exit("DAQBroker client application already running, please exit all running clients before starting new ones")
    else:
        with open(os.path.join(base_dir, 'pid'), 'w') as f:
            f.write(str(os.getpid()))
            f.flush()
        newClient = daqbrokerClient(**obj)
        if 'action' not in obj:
            obj['action'] = None
        if obj["action"] == 'register':
            newClient.register()
        newClient.start()

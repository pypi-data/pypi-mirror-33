import time
import socket
import zmq
import pprint
import smtplib
import multiprocessing
import json
import os
import fnmatch
import netifaces
import sys
import psutil
import requests
import math
import traceback
import logging
import re
import platform
import subprocess
import sqlite3
import backupFuncs
import parsingFuncs
import pyAesCrypt
import collector
import arrow
import ctypes
from email.mime.text import MIMEText
from getpass import getpass
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import bindparam
from numpy import asarray, linspace
from scipy.interpolate import interp1d
from numbers import Number
from asteval import Interpreter
from fractions import gcd


def parseMeta(
        server,
        engine,
        username,
        password,
        db,
        instrument,
        meta,
        paths,
        logPort,
        lockList):
    try:
        theContext = zmq.Context()
        daqbroObject = collector.serverData(
            server=server, engine=engine, user=username, pword=password)
        if(meta["parsing"]["locked"] == 0 and meta["parsing"]["forcelock"] == 0):
            database = db["dbname"]
            remarks = meta["parsing"]["remarks"]
            remarksMeta = meta["remarks"]
            metaType = meta["type"]
            warned = False
            errors = []
            try:
                theLogSocket = theContext.socket(zmq.REQ)
                theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                toSend = {
                    'req': 'LOG',
                    'type': 'INFO',
                    'process': 'COLLECTOR',
                    'message': "Parse LOCK - " + instrument["Name"],
                    'method': 'parseMeta'}
                theLogSocket.send(json.dumps(toSend).encode())
                theLogSocket.close()
                daqbroObject.db.execute(
                    text("UPDATE parsing SET locked='1',lastAction=:lastAction WHERE instid=:instid AND metaid=:metaid"),
                    lastAction=time.time(),
                    instid=instrument['instid'],
                    metaid=meta["metaid"])
                res = daqbroObject.db.execute(
                    text("SELECT lastAction from parsing WHERE instid=:instid AND metaid=:metaid"),
                    instid=instrument['instid'],
                    metaid=meta["metaid"])
                for row in res:  # This is just bullshit to test
                    stupidTime = row["lastAction"]
                # Look for channels that have a custom flag for them
                customChannels = [
                    x for x in meta["channels"] if int(
                        x["channeltype"]) == 2]
                # This is for file parsing
                if meta["remarks"]["toParse"] == "1" or meta["remarks"]["toParse"] == "true" or meta["remarks"]["toParse"]:
                    if metaType == 0:  # File parsing
                        if meta["remarks"]['parsingInfo']['separator'] == 'tab':
                            meta["remarks"]['parsingInfo']['separator'] = '\t'
                        elif meta["remarks"]['parsingInfo']['separator'] == 'comma':
                            meta["remarks"]['parsingInfo']['separator'] = ','
                        elif meta["remarks"]['parsingInfo']['separator'] == 'semicolon':
                            meta["remarks"]['parsingInfo']['separator'] = ';'
                        elif meta["remarks"]['parsingInfo']['separator'] == 'colon':
                            meta["remarks"]['parsingInfo']['separator'] = ':'
                        elif meta["remarks"]['parsingInfo']['separator'] == 'space':
                            meta["remarks"]['parsingInfo']['separator'] = ' '
                        header = []
                        headerHor = []
                        for channel in meta["channels"]:
                            if not int(channel["channeltype"]) == 2:
                                header.append(
                                    {
                                        'name': channel["Name"],
                                        'alias': channel["alias"],
                                        "type": channel["channeltype"],
                                        'channelid': channel["channelid"],
                                        'firstClock': channel["firstClock"],
                                        'lastclock': channel["lastclock"]})
                        lastFound = 0
                        thePath = os.path.join(
                            paths["BACKUPPATH"], database, instrument["Name"], meta["name"])
                        if 'getNested' in meta["remarks"]:
                            if(meta["remarks"]['getNested'] == "1" or meta["remarks"]['getNested'] == "true" or meta["remarks"]['getNested']):
                                walked = os.walk(thePath)
                                orderedFiles = []
                                for vals in walked:
                                    for file in vals[2]:
                                        orderedFiles.append(
                                            os.path.join(vals[0], file))
                            else:
                                def mtime(f): return os.stat(f).st_mtime
                                orderedFiles = list(sorted([os.path.join(
                                    thePath, x) for x in os.listdir(thePath)], key=mtime, reverse=True))
                        else:
                            def mtime(f): return os.stat(f).st_mtime
                            orderedFiles = list(sorted([os.path.join(
                                thePath, x) for x in os.listdir(thePath)], key=mtime, reverse=True))
                        # reduce file list by comparing with pattern and
                        # extension
                        filesWithPattern = [
                            x for x in orderedFiles if fnmatch.fnmatch(
                                x,
                                '*' +
                                meta["remarks"]["pattern"] +
                                '*.' +
                                meta["remarks"]["extension"])]  # reduced list
                        foundSyncedFiles = [
                            x for t in orderedFiles for x in remarks if t == x['name']]
                        foundSyncedFilesNames = [
                            x for t in remarks for x in orderedFiles if(
                                x == t['name'] and fnmatch.fnmatch(
                                    t['name'],
                                    '*' +
                                    meta["remarks"]["pattern"] +
                                    '*.' +
                                    meta["remarks"]["extension"]))]
                        notFoundSynced = list(
                            set(filesWithPattern) - set(foundSyncedFilesNames))
                        for file in foundSyncedFiles:
                            j = remarks.index(file)
                            changes = False
                            linesParsed = int(remarks[j]["linesParsed"])
                            linesNotParsed = int(remarks[j]["linesNotParsed"])
                            lastParsedLine = int(remarks[j]["lastParsedLine"])
                            lastChangeDate = int(remarks[j]["lastChangeDate"])
                            lastTime = float(remarks[j]["lastTime"])
                            # if((time.time()-os.path.getmtime(file['name'])>1*24*60*60)
                            # and (not (linesParsed==0 and
                            # linesNotParsed==0))):
                            if(os.path.getsize(file['name']) == file['size'] and os.path.getsize(file['name']) == file['parsedSize'] and os.path.getmtime(file['name']) == file['lastChangeDate']):
                                continue  # Files with no changes
                            # print(file)
                            if os.path.getsize(file['name']) > file['size']:
                                sizeDiff = os.path.getsize(
                                    file['name']) - file['size']
                                fileTest = open(file['name'], 'rb')
                                fileTest.seek(sizeDiff * -1, 2)
                                data = fileTest.read()
                                fileTest.close()
                                lines = data.decode().split('\n')
                                if len(
                                        lines) > 1000:  # Making lines small size to keep the parsing small
                                    lines = [
                                        x for i, x in enumerate(lines) if i <= 1000]
                                lines = [
                                    x for i, x in enumerate(lines) if not x == '']
                            else:
                                fileTest = open(file['name'], 'rU')
                                lines = [
                                    x for i, x in enumerate(fileTest) if i > lastParsedLine]
                                if len(
                                        lines) > 1000:  # Making lines small size to keep the parsing small
                                    lines = [
                                        x for i, x in enumerate(lines) if i <= 1000]
                                fileTest.close()
                            size = os.path.getsize(file['name'])
                            linesSize = file["parsedSize"] + \
                                sum([len(x.encode()) for x in lines])
                            # print('existing',len(lines))
                            parseResult = parseFileLines(
                                lines,
                                header,
                                remarksMeta['parsingInfo']['dataType'],
                                meta["remarks"],
                                instrument["Name"],
                                daqbroObject.db,
                                db["dbname"],
                                logPort)
                            linesParsed = linesParsed + \
                                parseResult["linesParsed"]
                            linesNotParsed = linesNotParsed + \
                                parseResult["linesNotParsed"]
                            lastParsedLine = lastParsedLine + len(lines)
                            changeDate = os.path.getmtime(file['name'])
                            lastTime = parseResult["lastTime"]
                            remarks[j] = {
                                'singleName': file['singleName'],
                                "name": file['name'],
                                "size": size,
                                "lastChangeDate": changeDate,
                                "linesParsed": linesParsed,
                                "linesNotParsed": linesNotParsed,
                                "lastParsedLine": lastParsedLine,
                                "totalLines": len(lines),
                                'lastTime': lastTime,
                                'parsedSize': linesSize}
                            remarks = sorted(
                                remarks, key=lambda k: k['lastChangeDate'], reverse=True)
                            daqbroObject.db.execute(
                                text("UPDATE parsing SET remarks=:remarks WHERE instid=:instid AND metaid=:metaid"),
                                remarks=json.dumps(remarks),
                                instid=instrument["instid"],
                                metaid=meta["metaid"])
                        for file in notFoundSynced:
                            # print(file)
                            fileTest = open(file, 'rU')
                            lines = fileTest.readlines()
                            fileTest.close()
                            # if len(lines)>1000:
                            #	newLines=lines[0:1000]
                            # else:
                            #	newLines=lines
                            if len(
                                    lines) > 1000:  # Making lines small size to keep the parsing small
                                lines = [
                                    x for i, x in enumerate(lines) if i <= 1000]
                            linesSize = sum([len(x.encode()) for x in lines])
                            # print('nonexisting',len(lines))
                            parseResult = parseFileLines(lines[int(meta["remarks"]['parsingInfo']['headerLines']):],
                                                         header,
                                                         remarksMeta['parsingInfo']['dataType'],
                                                         meta["remarks"],
                                                         instrument["Name"],
                                                         daqbroObject.db,
                                                         database,
                                                         logPort)
                            linesParsed = parseResult["linesParsed"]
                            linesNotParsed = parseResult["linesNotParsed"]
                            if "lastTime" in parseResult:
                                lastTime = float(parseResult["lastTime"])
                            # Not always necessarily true but important to
                            # ensure that monitoring continues
                            lastParsedLine = len(lines)
                            if(len(parseResult["errors"]) > 1):
                                for error in parseResult["errors"]:
                                    errors.append(error)
                            remarks.append({"singleName": file,
                                            "name": file,
                                            "size": os.path.getsize(file),
                                            "lastChangeDate": os.path.getmtime(file),
                                            "linesParsed": linesParsed,
                                            "linesNotParsed": linesNotParsed,
                                            "lastParsedLine": lastParsedLine,
                                            "totalLines": len(lines),
                                            'lastTime': lastTime,
                                            'parsedSize': linesSize})
                            remarks = sorted(
                                remarks, key=lambda k: k['lastChangeDate'], reverse=True)
                            daqbroObject.db.execute(
                                text("UPDATE parsing SET remarks=:remarks WHERE instid=:instid AND metaid=:metaid"),
                                remarks=json.dumps(remarks),
                                instid=instrument["instid"],
                                metaid=meta["metaid"])
                if len(customChannels) > 0:
                    for channel in customChannels:
                        parseCustomChannel(
                            instrument, channel, daqbroObject.db)
            except Exception as e:
                traceback.print_exc()
                _, _, tb = sys.exc_info()
                tbResult = traceback.format_list(
                    traceback.extract_tb(tb)[-1:])[-1]
                filename = tbResult.split(',')[0].replace(
                    'File', '').replace('"', '')
                lineno = tbResult.split(',')[1].replace('line', '')
                funname = tbResult.split(',')[2].replace(
                    '\n', '').replace(' in ', '')
                line = str(e)
                theLogSocket = theContext.socket(zmq.REQ)
                theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                toSend = {
                    'req': 'LOG',
                    'type': 'ERROR',
                    'process': 'COLLECTOR',
                    'message': str(e),
                    'filename': filename,
                    'lineno': lineno,
                    'funname': funname,
                    'line': line}
                theLogSocket.send(json.dumps(toSend).encode())
                theLogSocket.close()
            finally:
                theLogSocket = theContext.socket(zmq.REQ)
                theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                toSend = {
                    'req': 'LOG',
                    'type': 'INFO',
                    'process': 'COLLECTOR',
                    'message': "Parse UNLOCK - " + instrument["Name"],
                    'method': 'parseMeta'}
                theLogSocket.send(json.dumps(toSend).encode())
                theLogSocket.close()
                daqbroObject.db.execute(
                    text("UPDATE parsing SET locked='0' WHERE instid=:instid AND metaid=:metaid"),
                    instid=instrument['instid'],
                    metaid=meta["metaid"])
    except Exception as e:
        traceback.print_exc()
        _, _, tb = sys.exc_info()
        tbResult = traceback.format_list(traceback.extract_tb(tb)[-1:])[-1]
        filename = tbResult.split(',')[0].replace('File', '').replace('"', '')
        lineno = tbResult.split(',')[1].replace('line', '')
        funname = tbResult.split(',')[2].replace('\n', '').replace(' in ', '')
        line = str(e)
        theLogSocket = theContext.socket(zmq.REQ)
        theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
        toSend = {
            'req': 'LOG',
            'type': 'ERROR',
            'process': 'COLLECTOR',
            'message': str(e),
            'filename': filename,
            'lineno': lineno,
            'funname': funname,
            'line': line}
        theLogSocket.send(json.dumps(toSend).encode())
        theLogSocket.close()
    finally:
        daqbroObject.db.close()
        for i, el in enumerate(lockList):
            if el['instrument'] == instrument["Name"] and el['meta'] == meta["name"]:
                temp = {
                    'instrument': instrument["Name"],
                    'meta': meta["name"],
                    'locked': False}
                lockList[i] = temp


def interpolateDataArray(
        dataArray,
        minResolution,
        startTime,
        endTime,
        screenSize):
    for dataObj in dataArray:
        dataObj["data"] = interpolateData(
            asarray(
                dataObj["data"]),
            dataObj["channeltype"],
            minResolution,
            startTime,
            endTime,
            screenSize)
    return dataArray


def interpolateData(data, type, resolution, startTime, endTime, screenSize):
    # There is an ethical dilema here. For empty intervals I will interpolate from the closest value in time to start and end times.
    # This can be milliseconds but it can also be hours and days. This can
    # lead to bad interpolations in some cases.
    if resolution:
        # print(startTime,endTime,screenSize)
        if(screenSize < 0):  # I want to use the smallest resolution posible
            timeInt = linspace(int(startTime), int(endTime), int(
                (int(endTime) - int(startTime)) / int(resolution)))
        else:  # Using screen size to limit resolution
            timeInt = linspace(int(startTime), int(endTime), int(screenSize))
        if type == 1:
            strings = [x for x in data[:, 1]]
            data = asarray([[int(x), id(strings[i])]
                            for i, x in enumerate(data[:, 0])])
        intF = interp1d(data[:, 0], data, axis=0, kind="zero", fill_value=(
            data[0], data[-1]), bounds_error=False)
        newData = intF(timeInt)
        if type == 1:
            newData = [
                [x[0], ctypes.cast(int(x[1]), ctypes.py_object).value] for x in newData]
    else:  # This is for the case that EVERYTHING is empty, gotta find a good way to do this
        if type == 1:
            strings = [x for x in data[:, 1]]
            data = asarray([[int(x), id(strings[i])]
                            for i, x in enumerate(data[:, 0])])
        timeInt = linspace(int(startTime), int(endTime), 10)
        intF = interp1d(data[:, 0], data, axis=0, kind="zero", fill_value=(
            data[0], data[-1]), bounds_error=False)
        newData = intF(timeInt)
        if type == 1:
            newData = [
                [x[0], ctypes.cast(int(x[1]), ctypes.py_object).value] for x in newData]
    if type == 1:
        del strings
    return newData


def gatherChannels(ids, connection):
    toReturn = []
    for id in ids:
        chanInfo = False
        query = text("SELECT * from channels WHERE channelid=:channID")
        result = connection.execute(query, channID=id)
        for row in result:
            chanInfo = dict(zip(row.keys(), row))
            query2 = text(
                "SELECT Name from instruments WHERE instid=:channInst")
            result2 = connection.execute(query2, channInst=row["instid"])
            for row2 in result2:
                chanInfo["instrument"] = row2["Name"]
        toReturn.append(chanInfo)
    return toReturn


def getDataArray(channID, idx, channelData):
    for channData in channelData:
        if channData["channelID"] == channID:
            return channData["data"][idx][1]


def lcm(list):
    LCM = 1
    for i in list:
        LCM = LCM * i / gcd(LCM, i)
    return LCM


def parseCustomChannel(instrument, channel, connection):
    a = Interpreter(
        no_for=True,
        no_while=True,
        no_print=True,
        no_delete=True,
        no_assert=True)
    expression = channel["remarks"]["customExpression"]
    forbiddenStrings = [
        'daqbroObject',
        'connection',
        'os.',
        'sh.',
        'multiprocessing.',
        'sys.']  # Must find more exploitation methods
    for badString in forbiddenStrings:
        if expression.find(badString) >= 0:
            raise InvalidUsage(
                "You are trying to do forbidden things! Please stop",
                status_code=500)
    funcDeclares = re.findall(r'ID\(\d*\)', expression)
    ids = list(set([int(re.search(r"\d+", x).group()) for x in funcDeclares]))
    gatheredChannels = gatherChannels(ids, connection)
    if False in gatheredChannels:
        print("Bad expression - someone's trying forbidden things")
        return -1
    dbQuery = "SELECT max(clock) as maxClock FROM  `" + \
        instrument["Name"] + "_custom` WHERE `" + channel["Name"] + "` IS NOT NULL"
    maxClock = None
    result = connection.execute(text(dbQuery))
    for row in result:
        maxClock = row["maxClock"]
    if maxClock is None:
        maxClock = 0
    metaids = []
    parseInts = []
    for gatheredChannel in gatheredChannels:
        metaids.append(gatheredChannel["metaid"])
    metaids = list(set(metaids))
    dbQuery = "SELECT remarks from instmeta WHERE metaid in ("
    for metaid in metaids:
        dbQuery = dbQuery + str(metaid) + ","
    dbQuery = dbQuery.strip(',') + ")"
    result = connection.execute(text(dbQuery))
    for row in result:
        theRemarks = json.loads(row["remarks"])
        if "parseInterval" in theRemarks:
            parseInts.append(int(theRemarks["parseInterval"]))
    if len(parseInts) > 0:
        maxClock = maxClock - 2 * (lcm(parseInts) * 1000)
    # Getting the data from the channels
    channelData = []
    for gatheredChannel in gatheredChannels:
        dbQuery = text("SELECT * FROM instruments WHERE instid=:theInstid").bindparams(
            theInstid=gatheredChannel["instid"])
        result = connection.execute(dbQuery)
        for row in result:
            theChannelInstrument = dict(zip(row.keys(), row))
        if not gatheredChannel["channeltype"] == 2:
            tableAppend = "_data"
        else:
            tableAppend = "_custom"
        theQuery2 = text(
            " SELECT `" +
            theChannelInstrument['Name'] +
            tableAppend +
            "`.clock,`" +
            theChannelInstrument['Name'] +
            tableAppend +
            "`.`" +
            gatheredChannel["Name"] +
            "` FROM `" +
            theChannelInstrument['Name'] +
            tableAppend +
            "` WHERE clock>=:theStartTime AND clock<:theEndTime AND `" +
            gatheredChannel["Name"] +
            "`IS NOT NULL ORDER BY clock LIMIT 1000").bindparams(
            theStartTime=maxClock,
            theEndTime=time.time() *
            1000)
        toReturn = {
            'type': 'dataChannel',
            'closestClockDown': None,
            'closestClockUp': None,
            'closestValueDown': None,
            'closestValueUp': None,
            'min': None,
            'max': None,
            'mean': None,
            'std': None,
            'minTime': None,
            'maxTime': None,
            'minTimeStep': None,
            'maxTimeStep': None,
            'meanTime': None,
            'stdTime': None,
            'name': gatheredChannel["Name"],
            'iname': theChannelInstrument["Name"],
            'channelID': gatheredChannel["channelid"],
            'channeltype': gatheredChannel["channeltype"],
            'remarks': gatheredChannel["remarks"],
            'metaid': gatheredChannel["metaid"],
            'query': str(
                theQuery2.compile(
                    bind=connection,
                    compile_kwargs={
                        "literal_binds": True})),
            'data': []}
        delta = None
        delta2 = None
        M2 = None
        deltaTime = None
        delta2Time = None
        M2Time = None
        lastClock = None
        result = connection.execute(theQuery2)
        for i, row in enumerate(result):
            toReturn["data"].append(
                [row["clock"], row[gatheredChannel["Name"]]])
            if not (gatheredChannel["channeltype"] == 1):
                if toReturn["max"]:
                    if toReturn["max"] < float(row[gatheredChannel["Name"]]):
                        toReturn["max"] = float(row[gatheredChannel["Name"]])
                else:
                    toReturn["max"] = float(row[gatheredChannel["Name"]])
                if toReturn["min"]:
                    if toReturn["min"] > float(row[gatheredChannel["Name"]]):
                        toReturn["min"] = float(row[gatheredChannel["Name"]])
                else:
                    toReturn["min"] = float(row[gatheredChannel["Name"]])
            if toReturn["maxTime"]:
                if toReturn["maxTime"] < float(row["clock"]):
                    toReturn["maxTime"] = float(row["clock"])
            else:
                toReturn["maxTime"] = float(row["clock"])
            if toReturn["minTime"]:
                if toReturn["minTime"] > float(row["clock"]):
                    toReturn["minTime"] = float(row["clock"])
            else:
                toReturn["minTime"] = float(row["clock"])
            if lastClock is not None:
                if toReturn["maxTimeStep"] < float(row["clock"]) - lastClock:
                    toReturn["maxTimeStep"] = float(row["clock"]) - lastClock
            else:
                toReturn["maxTimeStep"] = 0
            if lastClock is not None:
                if toReturn["minTimeStep"] > float(row["clock"]) - lastClock:
                    toReturn["minTimeStep"] = float(row["clock"]) - lastClock
            else:
                toReturn["minTimeStep"] = 1000000000000000000
            if M2 is None:
                M2 = 0
                delta = 0
                delta2 = 0
                M2Time = 0
                deltaTime = 0
                delta2Time = 0
                toReturn["std"] = 0
                if not (gatheredChannel["channeltype"] == 1):
                    toReturn["mean"] = float(row[gatheredChannel["Name"]])
                toReturn["stdTime"] = 0
                toReturn["meanTime"] = 0
            else:
                if not (gatheredChannel["channeltype"] == 1):
                    delta = float(row[gatheredChannel["Name"]]
                                  ) - toReturn["mean"]
                    toReturn["mean"] = toReturn["mean"] + delta / float(i)
                    delta2 = float(
                        row[gatheredChannel["Name"]]) - toReturn["mean"]
                    M2 = M2 + delta * delta2
                deltaTime = (float(row["clock"]) -
                             lastClock) - toReturn["meanTime"]
                toReturn["meanTime"] = toReturn["meanTime"] + \
                    deltaTime / float(i)
                delta2Time = (float(row["clock"]) -
                              lastClock) - toReturn["meanTime"]
                M2Time = M2Time + deltaTime * delta2Time
                if i > 1:
                    toReturn["std"] = math.sqrt(M2 / (i - 1))
                    toReturn["stdTime"] = math.sqrt(M2Time / (i - 1))
            lastClock = float(row["clock"])
        theQuery4 = text(
            "SELECT `" +
            theChannelInstrument['Name'] +
            tableAppend +
            "`.clock,`" +
            theChannelInstrument['Name'] +
            tableAppend +
            "`.`" +
            gatheredChannel["Name"] +
            "` FROM `" +
            theChannelInstrument['Name'] +
            tableAppend +
            "` WHERE clock<=:theStartTime AND `" +
            gatheredChannel["Name"] +
            "`IS NOT NULL ORDER BY clock DESC LIMIT 1").bindparams(
            theStartTime=maxClock)
        result4 = connection.execute(theQuery4)
        for row in result4:
            toReturn["closestValueDown"] = row[gatheredChannel["Name"]]
            toReturn["closestClockDown"] = row["clock"]
        theQuery5 = text(
            "SELECT `" +
            theChannelInstrument['Name'] +
            tableAppend +
            "`.clock,`" +
            theChannelInstrument['Name'] +
            tableAppend +
            "`.`" +
            gatheredChannel["Name"] +
            "` FROM `" +
            theChannelInstrument['Name'] +
            tableAppend +
            "` WHERE clock>=:theEndTime AND `" +
            gatheredChannel["Name"] +
            "`IS NOT NULL ORDER BY clock ASC LIMIT 1").bindparams(
            theEndTime=time.time() *
            1000)
        result5 = connection.execute(theQuery5)
        for row in result5:
            toReturn["closestValueUp"] = row[gatheredChannel["Name"]]
            toReturn["closestClockUp"] = row["clock"]
        channelData.append(toReturn)
        if len(channelData[-1]) < 1:
            channelData[-1]["data"] = [[channelData[-1]["closestClockDown"],
                                        channelData[-1]["closestValueDown"]],
                                       [time.time() * 1000,
                                        channelData[-1]["closestValueDown"]]]
            if channelData[-1]["closestClockDown"] is not None:
                channelData[-1]["minTime"] = channelData[-1]["closestClockDown"]
            if channelData[-1]["closestClockUp"] is not None:
                channelData[-1]["maxTime"] = channelData[-1]["closestClockUp"]
    minStep = 0
    maxChannClock = 0
    minChannClock = 10000000000000000000000
    for i, channData in enumerate(channelData):
        if channData["minTimeStep"] is not None:
            if not minStep:
                minStep = channData["minTimeStep"]
            else:
                if channData["minTimeStep"] < minStep:
                    minStep = channData["minTimeStep"]
        if maxChannClock < channData["maxTime"]:
            maxChannClock = channData["maxTime"]
        if channData["maxTime"] is None:
            if maxChannClock > channData["closestClockUp"]:
                maxChannClock = channData["closestClockUp"]
        if minChannClock > channData["minTime"]:
            minChannClock = channData["minTime"]
        if channData["minTime"] is None:
            if minChannClock > channData["closestClockDown"]:
                minChannClock = channData["closestClockDown"]
    channelData = interpolateDataArray(
        channelData, minStep, minChannClock, maxChannClock, -1)
    timeList = linspace(int(minChannClock), int(maxChannClock), int(
        (int(maxChannClock) - int(minChannClock)) / int(minStep)))
    q = 0
    emptyInInterval = "UPDATE `" + \
        instrument["Name"] + "_custom` SET `" + channel["Name"] + "`=NULL WHERE clock >=" + str(maxClock)
    connection.execute(emptyInInterval)
    dbQueryHead = "INSERT INTO `" + \
        instrument["Name"] + "_custom` (`clock`,`" + channel["Name"] + "`) VALUES "
    dbQueryMiddle = ""
    dbQueryTail = " ON DUPLICATE KEY UPDATE `" + \
        channel["Name"] + "`=VALUES(`" + channel["Name"] + "`)"
    for t, theTime in enumerate(timeList):
        exprVal = None
        returnVal = None
        toTest = expression
        foundANone = False  # If one value is none this can come from a lot of sources, regardless, if I can't find the value of one channel I can't do anything for the value of the expression of the values. There is a LOT of work into making empty intervals have values so that is not going to be a problem for expresison analysis
        for i, channid in enumerate(ids):
            theChannel = [x for x in channelData if x["channelID"]
                          == channid]  # Should only be one channel
            if getDataArray(channid, t, channelData) is None:
                foundANone = True
                break
            if theChannel[0]["channeltype"] == 1:
                toTest = toTest.replace(
                    "ID(" + str(channid) + ")", "'" + str(getDataArray(channid, t, channelData)) + "'")
            else:
                toTest = toTest.replace(
                    "ID(" + str(channid) + ")", str(getDataArray(channid, t, channelData)))
        returnVal = a(toTest, show_errors=False)
        if not foundANone:
            if "exprVal" in a.symtable:
                exprVal = a.symtable["exprVal"]
                a.symtable["exprVal"] = None
            if len(a.error) > 0:
                exprVal = None
                returnVal = None
            if returnVal is None:
                if exprVal is None:
                    dbQueryMiddle = dbQueryMiddle + str(
                        text("(:clock,:value),").bindparams(
                            clock=int(theTime), value=None).compile(
                            bind=connection, compile_kwargs={
                                "literal_binds": True}))
                else:
                    if isinstance(exprVal, Number):
                        dbQueryMiddle = dbQueryMiddle + str(
                            text("(:clock,:value),").bindparams(
                                clock=int(theTime), value=exprVal).compile(
                                bind=connection, compile_kwargs={
                                    "literal_binds": True}))
                    else:
                        dbQueryMiddle = dbQueryMiddle + str(
                            text("(:clock,:value),").bindparams(
                                clock=int(theTime), value=None).compile(
                                bind=connection, compile_kwargs={
                                    "literal_binds": True}))
            elif isinstance(returnVal, Number):
                dbQueryMiddle = dbQueryMiddle + str(
                    text("(:clock,:value),").bindparams(
                        clock=int(theTime), value=returnVal).compile(
                        bind=connection, compile_kwargs={
                            "literal_binds": True}))
            else:
                dbQueryMiddle = dbQueryMiddle + str(
                    text("(:clock,:value),").bindparams(
                        clock=int(theTime), value=None).compile(
                        bind=connection, compile_kwargs={
                            "literal_binds": True}))
        else:
            dbQueryMiddle = dbQueryMiddle + str(
                text("(:clock,:value),").bindparams(
                    clock=int(theTime), value=None).compile(
                    bind=connection, compile_kwargs={
                        "literal_binds": True}))
        if q >= 1000:
            fullQuery = dbQueryHead + dbQueryMiddle.strip(',') + dbQueryTail
            dbQueryMiddle = ""
            connection.execute(fullQuery)
            q = 0
        q = q + 1
    if q > 1 and q < 1000:
        fullQuery = dbQueryHead + dbQueryMiddle.strip(',') + dbQueryTail
        connection.execute(fullQuery)


def parseFileLines(
        lines,
        header,
        parseType,
        metadata,
        instrument,
        dbConn,
        database,
        logPort):
    # print(len(lines))
    timeStart = time.time()
    theContext = zmq.Context()
    # trans=dbConn.begin()
    dbConn.execute(text("USE `daqbro_" + database + "`"))
    names = [x["name"] for x in header]
    if parseType == 0:
        returned = {}
        returned['linesParsed'] = 0
        returned['linesNotParsed'] = 0
        returned['lastTime'] = 0
        returned['values'] = []
        returned['errors'] = []
        timeFormat = metadata['parsingInfo']['timeFormat'].split('@')
        milliFound = False
        noFormFound = False
        if('NOFORMAT' in timeFormat):
            noFormFound = True
        elif('MILLISECOND' in timeFormat):
            milliFound = True
        theLastLine = 0
        linesGreatTime = 0
        linesLeastTime = 10000000000000000000
        q = 0
        dbQueryHead = 'INSERT INTO `' + instrument + '_data` (`clock`'
        for k in range(0, len(header)):
            dbQueryHead = dbQueryHead + ',`' + header[k]['name'] + '`'
        dbQuery2 = dbQueryHead + ') VALUES '
        linesStore = {}
        dbQueryMiddle = ''
        goodLines = []
        for i, line in enumerate(lines):
            try:
                lineStuff = line.replace('\n', '').split(
                    metadata['parsingInfo']['separator'])
                timeStr = []
                data = []
                for i, el in enumerate(lineStuff):
                    if i < len(timeFormat):
                        if not timeFormat[i] == '':
                            timeStr.append(el)
                        else:
                            data.append(el)
                    else:
                        data.append(el)
                # print(timeStr)
                if noFormFound:
                    # There should only be one element to this list
                    timeNum = float(' '.join(timeStr)) * 1000
                elif milliFound:
                    # There should also be only one element to this list
                    timeNum = float(' '.join(timeStr))
                else:
                    timeObj = arrow.get(
                        ' '.join(timeStr), ' '.join(timeFormat))
                    timeNum = (
                        timeObj.timestamp + timeObj.microsecond / 1e6) * 1000
                lineTime = str(timeNum)
                if not (lineTime in linesStore):
                    linesStore[lineTime] = {}
                if backupFuncs.is_number(lineTime):
                    returned['lastTime'] = lineTime
                    if float(lineTime) > linesGreatTime:
                        linesGreatTime = float(lineTime)
                    if float(lineTime) < linesLeastTime and float(
                            lineTime) > 0:
                        linesLeastTime = float(lineTime)
                dbQueryMiddleOld = dbQueryMiddle
                dbQueryMiddle = dbQueryMiddle + "(" + lineTime + ","
                headGood = []
                for k, head in enumerate(header):
                    try:
                        if(k < len(data)):
                            if(int(head["type"]) == 1):
                                theData = data[k].replace('\r', '')
                            else:
                                theData = float(data[k].replace('\r', ''))
                            # linesStore[lineTime][head["name"].replace('\r','')]=str(theData)
                            if(theData == ''):
                                dbQueryMiddle = dbQueryMiddle + "NULL,"
                                headGood.append(False)
                            else:
                                dbQueryMiddle = dbQueryMiddle + str(
                                    text(" :param,").bindparams(
                                        param=theData).compile(
                                        bind=dbConn, compile_kwargs={
                                            "literal_binds": True}))
                                headGood.append(True)
                        else:
                            headGood.append(False)
                            dbQueryMiddle = dbQueryMiddle + "NULL,"
                    except BaseException:
                        headGood.append(False)
                        dbQueryMiddle = dbQueryMiddle + "NULL,"
                        traceback.print_exc()
                if True in headGood:
                    dbQueryMiddle = dbQueryMiddle.rstrip(',') + "),"
                    goodLines.append(True)
                else:
                    dbQueryMiddle = dbQueryMiddleOld
                    goodLines.append(False)
                theLastLine = i
                q = q + 1
                if q * len(header) > 5000:
                    # print(q)
                    # print('linesread',time.time()-timeStart)
                    if True in goodLines:
                        dbQuery = "INSERT INTO `" + \
                            instrument + "_data` (clock,"
                        dbQuery3 = " ON DUPLICATE KEY UPDATE "
                        for k, name in enumerate(header):
                            dbQuery = dbQuery + "`" + name["name"] + "`,"
                            dbQuery3 = dbQuery3 + "`" + \
                                name["name"] + "`=VALUES(`" + name["name"] + "`),"
                        dbQuery = dbQuery.rstrip(
                            ",") + ") VALUES " + dbQueryMiddle.rstrip(',') + dbQuery3.strip(',')
                        try:
                            dbConn.execute(dbQuery)
                            # print('linessent',time.time()-timeStart)
                            returned['linesParsed'] = returned['linesParsed'] + q
                        except BaseException:
                            traceback.print_exc()
                            returned['linesNotParsed'] = returned['linesNotParsed'] + q
                        try:
                            if linesLeastTime > 1000000000000 and linesGreatTime > 0 and linesLeastTime < 10000000000000000000:  # At least SOMETHING was caught
                                dbQuery = "UPDATE channels SET lastclock=GREATEST(lastclock," + str(
                                    int(linesGreatTime)) + ") "
                                dbQuery0 = "lastValue= CASE channelid "
                                dbQuery1 = "firstClock= CASE firstClock WHEN '0' THEN '" + \
                                    str(int(linesLeastTime)) + "' ELSE LEAST(firstClock,'" + str(int(linesLeastTime)) + "') "
                                dbQuery2 = "WHERE channelid IN("
                                for k in range(0, len(header)):
                                    if k < len(data):
                                        dbQuery2 = dbQuery2 + \
                                            str(header[k]["channelid"]) + ','
                                        if header[k]["firstClock"] > 0:
                                            dbQuery0 = dbQuery0 + "WHEN '" + \
                                                str(header[k]["channelid"]) + "' THEN '" + str(data[k]) + "' "
                                        else:
                                            dbQuery0 = dbQuery0 + "WHEN '" + \
                                                str(header[k]["channelid"]) + "' THEN '" + str(data[k]) + "' "
                                            #dbQuery="UPDATE channels SET lastclock=GREATEST(lastclock,"+str(int(linesGreatTime))+"), lastValue='"+str(data[k])+"', firstClock="+str(int(linesLeastTime))+" WHERE channelid='"+str(header[k]["channelid"])+"'"
                                dbQuery2 = dbQuery2.rstrip(',') + ')'
                                dbQuery = dbQuery + ',' + dbQuery1 + ' END,' + dbQuery0 + " END " + dbQuery2
                                dbConn.execute(dbQuery)
                                # print('channelupdate',time.time()-timeStart)
                        except Exception as e:
                            traceback.print_exc()
                            poop = 'poop'
                    linesStore = {}
                    q = 0
                    dbQueryMiddle = ''
                    headGood = []
                    goodLines = []
            except Exception as e:
                # traceback.print_exc()
                continue
        if q > 0:
            if True in goodLines:
                dbQuery = "INSERT INTO `" + instrument + "_data` (clock,"
                dbQuery3 = " ON DUPLICATE KEY UPDATE "
                for k, name in enumerate(header):
                    dbQuery = dbQuery + "`" + name["name"] + "`,"
                    dbQuery3 = dbQuery3 + "`" + \
                        name["name"] + "`=VALUES(`" + name["name"] + "`),"
                dbQuery = dbQuery.rstrip(
                    ",") + ") VALUES " + dbQueryMiddle.rstrip(',') + dbQuery3.strip(',')
                try:
                    dbConn.execute(dbQuery)
                    returned['linesParsed'] = returned['linesParsed'] + q
                except BaseException:
                    traceback.print_exc()
                    returned['linesNotParsed'] = returned['linesNotParsed'] + q
                try:
                    if linesLeastTime > 1000000000000 and linesGreatTime > 0 and linesLeastTime < 10000000000000000000:  # At least SOMETHING was caught
                        dbQuery = "UPDATE channels SET lastclock=GREATEST(lastclock," + str(
                            int(linesGreatTime)) + ") "
                        dbQuery0 = "lastValue= CASE channelid "
                        dbQuery1 = "firstClock= CASE firstClock WHEN '0' THEN '" + \
                            str(int(linesLeastTime)) + "' ELSE LEAST(firstClock,'" + str(int(linesLeastTime)) + "') "
                        dbQuery2 = "WHERE channelid IN("
                        for k in range(0, len(header)):
                            if k < len(data):
                                dbQuery2 = dbQuery2 + \
                                    str(header[k]["channelid"]) + ','
                                if header[k]["firstClock"] > 0:
                                    dbQuery0 = dbQuery0 + "WHEN '" + \
                                        str(header[k]["channelid"]) + "' THEN '" + str(data[k]) + "' "
                                else:
                                    dbQuery0 = dbQuery0 + "WHEN '" + \
                                        str(header[k]["channelid"]) + "' THEN '" + str(data[k]) + "' "
                                    #dbQuery="UPDATE channels SET lastclock=GREATEST(lastclock,"+str(int(linesGreatTime))+"), lastValue='"+str(data[k])+"', firstClock="+str(int(linesLeastTime))+" WHERE channelid='"+str(header[k]["channelid"])+"'"
                        dbQuery2 = dbQuery2.rstrip(',') + ')'
                        dbQuery = dbQuery + ',' + dbQuery1 + ' END,' + dbQuery0 + " END " + dbQuery2
                        dbConn.execute(dbQuery)
                except Exception as e:
                    traceback.print_exc()
                    poop = 'poop'
            linesStore = {}
            q = 0
            dbQueryMiddle = ''
        returned['lastParsedLine'] = len(lines)
        returned['returnedValue'] = 1
        returned['errors'] = list(set(returned['errors']))
        # dbConn.commit()
    elif int(parseType) == 1:
        returned = {}
        returned['linesParsed'] = 0
        returned['linesNotParsed'] = 0
        returned['values'] = []
        returned['errors'] = []
        linesGreatTime = 0
        linesLeastTime = 10000000000000000000
        if metadata['parsingInfo']['timeFormat'].find(
                'NOFORMAT') == -1:  # Didn't find a noformat string in the time format
            if metadata['parsingInfo']['timeFormat'].find(
                    'MILLISECOND') == -1:  # Didn't find a miliseconds string in the time format
                timeFormatPos = [
                    m.start() for m in re.finditer(
                        '%', metadata['parsingInfo']['timeFormat'])]  # Array with positions of all %
            else:
                timeFormatPos = [metadata['parsingInfo']
                                 ['timeFormat'].find('MILLISECOND')]
        else:  # Found a noformat string in the time format
            timeFormatPos = [metadata['parsingInfo']
                             ['timeFormat'].find('NOFORMAT')]
        timeCols = []
        timeColsFormat = []
        prevItem = 0
        prevCol = 0
        for (i, item) in enumerate(timeFormatPos):
            timeCols.append(
                prevCol +
                metadata['parsingInfo']['timeFormat'].count(
                    '@',
                    prevItem,
                    item))
            prevItem = item
            prevCol = timeCols[i]
        timeColsFormatPre = metadata['parsingInfo']['timeFormat'].split('@')
        timeColsFormat = [x for x in timeColsFormatPre if not x == '']
        timeCols = list(set(timeCols))
        if (len(lines) % int(metadata['parsingInfo']['colSize'])) == 0:
            linesStore = {}
            for i in range(0, int((len(lines)) /
                                  int(metadata['parsingInfo']['colSize']))):
                try:
                    theSlice = lines[i *
                                     int(metadata['parsingInfo']['colSize']):(i +
                                                                              1) *
                                     int(metadata['parsingInfo']['colSize'])]
                    theNewLine = ''.join(theSlice).replace(
                        '\n', metadata['parsingInfo']['separator'])
                    lineStuff = theNewLine.split(
                        metadata['parsingInfo']['separator'])
                    data = lineStuff
                    timeStr = ''
                    for (i, item) in enumerate(timeCols):
                        timeStr = timeStr + lineStuff[timeCols[i]] + '@'
                        timeStr = timeStr.replace('\n', '').replace('\r', '')
                    timeStrFormat = '@'.join(timeColsFormat) + '@'
                    if metadata['parsingInfo']['timeFormat'].find(
                            'NOFORMAT') >= 0:
                        lineTime = str(
                            float(timeStr[0:(len(timeStr) - 1)]) * 1000)
                    elif metadata['parsingInfo']['timeFormat'].find('MILLISECOND') >= 0:
                        # print(timeStr[0:(len(timeStr)-1)])
                        lineTime = str(float(timeStr[0:(len(timeStr) - 1)]))
                    else:
                        # lineTime=str(time.mktime(datetime.timetuple(datetime.strptime(timeStr,timeStrFormat)))*1000)
                        timeObj = arrow.get(
                            ' '.join(timeStr), ' '.join(timeStrFormat))
                        timeNum = (
                            timeObj.timestamp + timeObj.microsecond / 1e6) * 1000
                        lineTime = str(timeNum)
                    if backupFuncs.is_number(lineTime):
                        returned['lastTime'] = lineTime
                        if float(lineTime) > linesGreatTime:
                            linesGreatTime = float(lineTime)
                            valueToInput = lineStuff[int(
                                metadata['parsingInfo']['headerPosition'])]
                        if float(lineTime) < linesLeastTime and float(
                                lineTime) > 0:
                            linesLeastTime = float(lineTime)
                            valueToInput = lineStuff[int(
                                metadata['parsingInfo']['headerPosition'])]
                    headerStr = lineStuff[int(
                        metadata['parsingInfo']['headerPosition'])]
                    # headerStr=lineStuff[int(metadata['parsingInfo']['valuePosition'])]
                    theHeaderValue = [
                        x for x in header if x['alias'] == headerStr]
                    if not str(lineTime) in linesStore:
                        linesStore[str(lineTime)] = {}
                    if(len(theHeaderValue) > 0):
                        if (len(lineStuff) -
                                1) > int(metadata['parsingInfo']['valuePosition']):
                            # if
                            # (len(lineStuff)-1)>=int(metadata['parsingInfo']['headerPosition']):
                            theLineValue = lineStuff[int(
                                metadata['parsingInfo']['valuePosition'])]
                            # print(theLineValue)
                            # print(theHeaderValue)
                            #dbQuery="INSERT INTO `"+instrument+"_data` (clock,`"+theHeaderValue[0]['name']+"`) VALUES('"+str(lineTime)+"','"+theLineValue+"') ON DUPLICATE KEY UPDATE `"+theHeaderValue[0]['name']+"`='"+theLineValue+"';"
                            # dbConn.execute(dbQuery)
                            linesStore[str(lineTime)][theHeaderValue[0]
                                                      ['name']] = theLineValue
                            # r=dbConn.store_result()
                            returned['linesParsed'] = returned['linesParsed'] + \
                                int(metadata['parsingInfo']['colSize'])
                    if len(list(linesStore.keys())) > 10:
                        dbQuery2 = ""
                        dbQuery = "INSERT INTO `" + \
                            instrument + "_data` (clock,"
                        dbQuery3 = " ON DUPLICATE KEY UPDATE "
                        for name in header:
                            dbQuery = dbQuery + "`" + name["name"] + "`,"
                            dbQuery3 = dbQuery3 + "`" + \
                                name["name"] + "`=VALUES(`" + name["name"] + "`),"
                        dbQuery = dbQuery.rstrip(",") + ") VALUES "
                        for theTime in list(linesStore.keys()):
                            if list(linesStore[theTime].keys()):
                                collectedNames = list(
                                    linesStore[theTime].keys())
                                dbQuery2 = dbQuery2 + " (" + theTime + ","
                                values = [
                                    linesStore[theTime][x] if x in collectedNames else None for x in names]
                                for value in values:
                                    if value is not None:
                                        dbQuery2 = dbQuery2 + str(
                                            text(" :param,").bindparams(
                                                param=value).compile(
                                                bind=dbConn, compile_kwargs={
                                                    "literal_binds": True}))
                                    else:
                                        dbQuery2 = dbQuery2 + " NULL,"
                                dbQuery2 = dbQuery2.rstrip(',') + "),"
                            dbQuery = dbQuery + dbQuery2
                        dbQuery = dbQuery.strip(",") + dbQuery3.strip(',')
                        dbConn.execute(dbQuery)
                        linesStore = {}
                except Exception as e:
                    traceback.print_exc()
                    returned['linesNotParsed'] = returned['linesNotParsed'] + \
                        int(metadata['parsingInfo']['colSize'])
                    returned['errors'].append(str(e))
                    continue
            if len(list(linesStore.keys())) > 10:
                dbQuery2 = ""
                dbQuery = "INSERT INTO `" + instrument + "_data` (clock,"
                dbQuery3 = " ON DUPLICATE KEY UPDATE "
                for name in header:
                    dbQuery = dbQuery + "`" + name["name"] + "`,"
                    dbQuery3 = dbQuery3 + "`" + \
                        name["name"] + "`=VALUES(`" + name["name"] + "`),"
                dbQuery = dbQuery.rstrip(",") + ") VALUES "
                for theTime in list(linesStore.keys()):
                    if list(linesStore[theTime].keys()):
                        collectedNames = list(linesStore[theTime].keys())
                        dbQuery2 = dbQuery2 + " (" + theTime + ","
                        values = [
                            linesStore[theTime][x] if x in collectedNames else None for x in names]
                        for value in values:
                            if value is not None:
                                dbQuery2 = dbQuery2 + str(
                                    text(" :param,").bindparams(
                                        param=value).compile(
                                        bind=dbConn, compile_kwargs={
                                            "literal_binds": True}))
                            else:
                                dbQuery2 = dbQuery2 + " NULL,"
                        dbQuery2 = dbQuery2.rstrip(',') + "),"
                    dbQuery = dbQuery + dbQuery2
                dbQuery = dbQuery.strip(",") + dbQuery3.strip(',')
                try:
                    dbConn.execute(dbQuery)
                except BaseException:
                    traceback.print_exc()
                linesStore = {}
                print("BOOP")
            try:
                if linesLeastTime > 1000000000000 and linesGreatTime > 0 and linesLeastTime < 10000000000000000000:  # At least SOMETHING was caught
                    for k in range(0, len(header)):
                        dbQuery = "UPDATE channels SET lastclock=GREATEST(lastclock," + str(int(linesGreatTime)) + "), lastValue='" + str(
                            valueToInput) + "', firstClock=LEAST(firstClock," + str(int(linesLeastTime)) + ") WHERE channelid='" + str(header[k]["channelid"]) + "'"
                        dbConn.execute(dbQuery)
            # dbConn.commit()
            except Exception as e:
                traceback.print_exc()
                poop = 'poop'
    return returned


def parseThirdParty(daqbroObject, instmeta, message, type, remarks, logPort):
    dbQuery = "SELECT instid FROM instruments WHERE Name='" + \
        message['instrument'] + "'"
    daqbroObject.db.query(dbQuery)
    r = daqbroObject.db.store_result()
    instid = r.fetch_row()
    theContext = zmq.Context()
    # First need to check what kind of third party parsing it is
    dbQuery = "SELECT MAX(clock) FROM daqbroker_settings.global"
    daqbroObject.db.query(dbQuery)
    r = daqbroObject.db.store_result()
    temp = r.fetch_row(0)
    dbQuery = "SELECT addonfolder FROM daqbroker_settings.global WHERE clock=" + \
        temp[0][0]
    daqbroObject.db.query(dbQuery)
    r = daqbroObject.db.store_result()
    addonPath = r.fetch_row(0)[0][0].decode()
    dbQuery = "SELECT * FROM daqbroker_settings.addons WHERE id=" + \
        str(type - 100)
    daqbroObject.db.query(dbQuery)
    r = daqbroObject.db.store_result()
    addonDeets = r.fetch_row(0)
    addonFile = addonDeets[0][2].decode()
    file = open(os.path.join(addonPath, addonFile), 'r')
    addonDesc = file.readlines(0)
    file.close()
    addonDescParsed = json.loads(' '.join(addonDesc).replace('\n', ''))
    database = message["database"]
    BACKUPPATH = daqbroObject.globals[0][2].decode()
    warned = False
    if addonDescParsed['type'] == 'fileParser':  # File parser thrid party software
        path = os.path.join(BACKUPPATH, database, message["instrument"])

        def mtime(f): return os.stat(os.path.join(path, f)).st_mtime
        orderedFiles = list(sorted(os.listdir(path), key=mtime, reverse=True))
        # reduce file list by comparing with pattern and extension
        filesWithPattern = [x for x in orderedFiles if fnmatch.fnmatch(
            x, '*' + value["pattern"] + '*.' + value["extension"])]  # reduced list
        foundSyncedFiles = [
            x for y in filesWithPattern for x in remarks if y == x['singleName']]
        foundSyncedFilesNames = [
            x for y in remarks for x in filesWithPattern if x == y['singleName']]
        notFoundSynced = list(
            set(filesWithPattern) -
            set(foundSyncedFilesNames))
        header = []
        for channel in daqbroObject.channels[database][message["instrument"]]:
            stupidRemarks = json.loads(channel[8].decode())
            goodRemarks = {}
            for key in stupidRemarks:
                if not (key == 'name' or key == 'alias' or key == 'remarks' or key ==
                        'lastclock' or key == 'lastclock' or key == 'order'):
                    goodRemarks[key] = stupidRemarks[key]
            if channel[9] == message["metaNo"]:
                header.append({'name': channel[0].decode(), 'alias': channel[13].decode(
                ), 'remarks': goodRemarks, 'lastclock': channel[10], 'order': channel[12]})
        if not os.path.isfile(
            os.path.join(
                addonPath,
                addonDescParsed['folder'],
                addonDescParsed['exeFile'])):
            theLogSocket = theContext.socket(zmq.REQ)
            theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
            toSend = {'req': 'LOG', 'type': 'WARNING', 'process': 'COLLECTOR', 'message': 'COULD NOT FIND EXECUTABLE ' + \
                addonDescParsed['exeFile'] + ' IN PARSING FOLDER. PARSING IGNORED -' + message["instrument"], 'method': 'parseMeta'}
            theLogSocket.send(json.dumps(toSend).encode())
            theLogSocket.close()
            return 0
        for file in foundSyncedFiles:  # Files already synced - this should always be the case
            j = remarks.index(file)
            changes = False
            linesParsed = int(remarks[j]["linesParsed"])
            linesNotParsed = int(remarks[j]["linesNotParsed"])
            lastParsedLine = int(remarks[j]["lastParsedLine"])
            lastChangeDate = int(remarks[j]["lastChangeDate"])
            if('lastTime' in remarks[j]):
                lastTime = float(remarks[j]["lastTime"])
            else:
                lastTime = 0
            if(time.time() - lastChangeDate > 30 * 24 * 60 * 60):
                if not warned:
                    theLogSocket = theContext.socket(zmq.REQ)
                    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                    toSend = {
                        'req': 'LOG',
                        'type': 'WARNING',
                        'process': 'COLLECTOR',
                        'message': 'FOUND FILES OLDER THAN 1 MONTH PARSING OF THESE FILES IGNORED' + message["instrument"],
                        'method': 'parseMeta'}
                    theLogSocket.send(json.dumps(toSend).encode())
                    theLogSocket.close()
                    warned = True
                continue
            if (not (lastChangeDate * 1000 == int(lastTime))
                    and (not ('badFile' in file))):
                theArgument = {
                    'header': header,
                    'file': {
                        'path': os.path.join(
                            path,
                            file['singleName']),
                        'lastTime': lastTime}}
                if(platform.system() == 'Windows'):  # Running on windows machine
                    output = subprocess.check_output(
                        [
                            os.path.join(
                                addonPath,
                                addonDescParsed['folder'],
                                addonDescParsed['exeFile']) +
                            '.exe',
                            json.dumps(theArgument)])
                elif(platform.system() == 'Linux'):  # Running on linux machine
                    output = subprocess.check_output(
                        [
                            os.path.join(
                                addonPath,
                                addonDescParsed['folder'],
                                addonDescParsed['exeFile']),
                            json.dumps(theArgument)])
                try:
                    #(output, err) = p.communicate()
                    #exit_code = p.wait()
                    result = json.loads(output.decode().replace('\n', ''))
                    lastParsedTime = 0
                    if('order' in result):
                        if(result['order'] == 'dataImport'):
                            arrays = [{x: result[x]} for x in result for y in header if (
                                y['name'] == x and not x == 'order')]
                            for array in arrays:
                                for x in array:
                                    maxTime = 0
                                    minTime = 100000000000000
                                    for vals in array[x]:
                                        try:
                                            dbQuery = "INSERT INTO `" + message["instrument"] + "_data` (clock,`" + x + "`) VALUES(" + str(
                                                vals[0]) + "," + str(vals[1]) + ") ON DUPLICATE KEY UPDATE `" + x + "`='" + str(vals[1]) + "'"
                                            daqbroObject.db.query(dbQuery)
                                            r = daqbroObject.db.store_result()
                                            lastParsedTime = float(vals[0])
                                            if(vals[0] > maxTime):
                                                maxTime = vals[0]
                                            if(vals[0] < minTime):
                                                minTime = vals[0]
                                        except BaseException:
                                            continue
                                    if maxTime > 0 and minTime < 10000000000000000000:  # At least SOMETHING was caught
                                        dbQuery = "SELECT channelid FROM channels WHERE instid='" + \
                                            instid[0][0] + "' AND Name='" + x + "'"
                                        daqbroObject.db.query(dbQuery)
                                        r = daqbroObject.db.store_result()
                                        channid = r.fetch_row()
                                        dbQuery = "UPDATE channels SET lastclock=GREATEST(lastclock," + str(
                                            maxTime) + "), firstClock=LEAST(firstClock," + str(minTime) + ") WHERE channelid='" + channid[0][0] + "'"
                                        daqbroObject.db.query(dbQuery)
                                        r = daqbroObject.db.store_result()
                            remarks[j]['lastTime'] = lastParsedTime
                            remarks = sorted(
                                remarks, key=lambda k: k['lastChangeDate'], reverse=True)
                            dbQuery = b"UPDATE parsing SET remarks='" + daqbroObject.db.escape_string(json.dumps(
                                remarks)) + b"' WHERE instid=" + instid[0][0].encode() + b" AND metaid=" + message["metaNo"].encode()
                            daqbroObject.db.query(dbQuery)
                            r = daqbroObject.db.store_result()
                    else:
                        theLogSocket = theContext.socket(zmq.REQ)
                        theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                        toSend = {
                            'req': 'LOG',
                            'type': 'WARNING',
                            'process': 'COLLECTOR',
                            'message': 'FILE ' + file['name'] + ' PARSING DID NOT GENERATE CORRECT ORDER, IGNORED - ' + message["instrument"],
                            'method': 'parseMeta'}
                        theLogSocket.send(json.dumps(toSend).encode())
                        theLogSocket.close()
                        remarks[j]['badFile'] = True
                        remarks = sorted(
                            remarks, key=lambda k: k['lastChangeDate'], reverse=True)
                        dbQuery = b"UPDATE parsing SET remarks='" + daqbroObject.db.escape_string(json.dumps(
                            remarks)) + b"' WHERE instid=" + instid[0][0].encode() + b" AND metaid=" + message["metaNo"].encode()
                        daqbroObject.db.query(dbQuery)
                        r = daqbroObject.db.store_result()
                        error = 1
                        continue
                except Exception as e:
                    theLogSocket = theContext.socket(zmq.REQ)
                    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                    toSend = {
                        'req': 'LOG',
                        'type': 'WARNING',
                        'process': 'COLLECTOR',
                        'message': 'FILE ' + file['name'] + ' - ERROR INTERPRETING PARSING OUTPUT- ' + message["instrument"] + '- ' + str(e),
                        'method': 'parseMeta'}
                    theLogSocket.send(json.dumps(toSend).encode())
                    theLogSocket.close()
                    remarks[j]['badFile'] = True
                    remarks = sorted(
                        remarks,
                        key=lambda k: k['lastChangeDate'],
                        reverse=True)
                    dbQuery = b"UPDATE parsing SET remarks='" + daqbroObject.db.escape_string(json.dumps(
                        remarks)) + b"' WHERE instid=" + instid[0][0].encode() + b" AND metaid=" + message["metaNo"].encode()
                    daqbroObject.db.query(dbQuery)
                    r = daqbroObject.db.store_result()
                    error = 1
                    continue
        for file in notFoundSynced:  # Files not synced - must ALWAYS parse
            newFile = {}
            theArgument = {'meta': instmeta, 'header': header, 'file': file}
            if(platform.system() == 'Windows'):  # Running on windows machine
                output = subprocess.check_output(
                    [
                        os.path.join(
                            addonPath,
                            addonDescParsed['folder'],
                            addonDescParsed['exeFile']) +
                        '.exe',
                        json.dumps(theArgument)])
            elif(platform.system() == 'Linux'):  # Running on linux machine
                output = subprocess.check_output(
                    [
                        os.path.join(
                            addonPath,
                            addonDescParsed['folder'],
                            addonDescParsed['exeFile']),
                        json.dumps(theArgument)],
                    stdout=PIPE)
            try:
                result = json.loads(output)
                lastParsedTime = 0
                if('order' in result):
                    if(result['order'] == 'dataImport'):
                        arrays = [{x: result[x]} for x in result for y in header if (
                            y['name'] == x and not x == 'order')]
                        for array in arrays:
                            for x in array:
                                maxTime = 0
                                minTime = 100000000000000
                                for vals in array[x]:
                                    try:
                                        dbQuery = "INSERT INTO `" + message["instrument"] + "_data` (clock,`" + x + "`) VALUES(" + str(
                                            vals[0]) + "," + str(vals[1]) + ") ON DUPLICATE KEY UPDATE `" + x + "`='" + str(vals[1]) + "'"
                                        daqbroObject.db.query(dbQuery)
                                        r = daqbroObject.db.store_result()
                                        lastParsedTime = float(vals[0])
                                        if(vals[0] > maxTime):
                                            maxTime = vals[0]
                                        if(vals[0] < minTime):
                                            minTime = vals[0]
                                    except BaseException:
                                        continue
                                if maxTime > 0 and minTime < 10000000000000000000:  # At least SOMETHING was caught
                                    dbQuery = "SELECT channelid FROM channels WHERE instid='" + \
                                        instid[0][0] + "' AND Name='" + x + "'"
                                    daqbroObject.db.query(dbQuery)
                                    r = daqbroObject.db.store_result()
                                    channid = r.fetch_row()
                                    dbQuery = "UPDATE channels SET lastclock=GREATEST(lastclock," + str(
                                        maxTime) + "), firstClock=LEAST(firstClock," + str(minTime) + ") WHERE channelid='" + channid[0][0] + "'"
                                    daqbroObject.db.query(dbQuery)
                                    r = daqbroObject.db.store_result()
                        remarks[j]['lastTime'] = lastParsedTime
                        remarks = sorted(
                            remarks, key=lambda k: k['lastChangeDate'], reverse=True)
                        dbQuery = b"UPDATE parsing SET remarks='" + daqbroObject.db.escape_string(json.dumps(
                            remarks)) + b"' WHERE instid=" + instid[0][0].encode() + b" AND metaid=" + message["metaNo"].encode()
                        daqbroObject.db.query(dbQuery)
                        r = daqbroObject.db.store_result()
                else:
                    theLogSocket = theContext.socket(zmq.REQ)
                    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                    toSend = {
                        'req': 'LOG',
                        'type': 'WARNING',
                        'process': 'COLLECTOR',
                        'message': 'FILE ' + file['name'] + ' PARSING DID NOT GENERATE CORRECT ORDER, IGNORED - ' + message["instrument"],
                        'method': 'parseMeta'}
                    theLogSocket.send(json.dumps(toSend).encode())
                    theLogSocket.close()
                    remarks[j]['badFile'] = True
                    remarks = sorted(
                        remarks,
                        key=lambda k: k['lastChangeDate'],
                        reverse=True)
                    dbQuery = b"UPDATE parsing SET remarks='" + daqbroObject.db.escape_string(json.dumps(
                        remarks)) + b"' WHERE instid=" + instid[0][0].encode() + b" AND metaid=" + message["metaNo"].encode()
                    daqbroObject.db.query(dbQuery)
                    r = daqbroObject.db.store_result()
                    error = 1
                    continue
            except Exception as e:
                theLogSocket = theContext.socket(zmq.REQ)
                theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                toSend = {
                    'req': 'LOG',
                    'type': 'WARNING',
                    'process': 'COLLECTOR',
                    'message': 'FILE ' + file['name'] + ' - ERROR INTERPRETING PARSING OUTPUT- ' + message["instrument"] + '- ' + str(e),
                    'method': 'parseMeta'}
                theLogSocket.send(json.dumps(toSend).encode())
                theLogSocket.close()
                remarks[j]['badFile'] = True
                remarks = sorted(
                    remarks,
                    key=lambda k: k['lastChangeDate'],
                    reverse=True)
                dbQuery = b"UPDATE parsing SET remarks='" + daqbroObject.db.escape_string(json.dumps(
                    remarks)) + b"' WHERE instid=" + instid[0][0].encode() + b" AND metaid=" + message["metaNo"].encode()
                daqbroObject.db.query(dbQuery)
                r = daqbroObject.db.store_result()
                error = 1
                continue
    # Full file parser thrid party software
    elif addonDescParsed['type'] == 'fullParser':
        header = []
        for channel in daqbroObject.channels[database][message["instrument"]]:
            stupidRemarks = json.loads(channel[8].decode())
            goodRemarks = {}
            for key in stupidRemarks:
                if not (key == 'name' or key == 'alias' or key == 'remarks' or key ==
                        'lastclock' or key == 'lastclock' or key == 'order'):
                    goodRemarks[key] = stupidRemarks[key]
            if channel[9] == message["metaNo"]:
                header.append({'name': channel[0].decode(), 'alias': channel[13].decode(
                ), 'remarks': goodRemarks, 'lastclock': channel[10], 'order': channel[12]})
        if(platform.system() == 'Windows'):  # Running on windows machine
            output = subprocess.check_output(
                [
                    os.path.join(
                        addonPath,
                        addonDescParsed['folder'],
                        addonDescParsed['exeFile']) +
                    '.exe',
                    json.dumps(theArgument)])
        elif(platform.system() == 'Linux'):  # Running on linux machine
            output = subprocess.check_output(
                [
                    os.path.join(
                        addonPath,
                        addonDescParsed['folder'],
                        addonDescParsed['exeFile']),
                    json.dumps(theArgument)],
                stdout=PIPE)
        try:
            #(output, err) = p.communicate()
            #exit_code = p.wait()
            result = json.loads(output.decode().replace('\n', ''))
            lastParsedTime = 0
            if('order' in result):
                if(result['order'] == 'dataImport'):
                    arrays = [{x: result[x]} for x in result for y in header if (
                        y['name'] == x and not x == 'order')]
                    for array in arrays:
                        for x in array:
                            maxTime = 0
                            minTime = 100000000000000
                            for vals in array[x]:
                                try:
                                    dbQuery = "INSERT INTO `" + message["instrument"] + "_data` (clock,`" + x + "`) VALUES(" + str(
                                        vals[0]) + "," + str(vals[1]) + ") ON DUPLICATE KEY UPDATE `" + x + "`='" + str(vals[1]) + "'"
                                    daqbroObject.db.query(dbQuery)
                                    r = daqbroObject.db.store_result()
                                    lastParsedTime = float(vals[0])
                                    if(vals[0] > maxTime):
                                        maxTime = vals[0]
                                    if(vals[0] < minTime):
                                        minTime = vals[0]
                                except BaseException:
                                    continue
                            if maxTime > 0 and minTime < 10000000000000000000:  # At least SOMETHING was caught
                                dbQuery = "SELECT channelid FROM channels WHERE instid='" + \
                                    instid[0][0] + "' AND Name='" + x + "'"
                                daqbroObject.db.query(dbQuery)
                                r = daqbroObject.db.store_result()
                                channid = r.fetch_row()
                                dbQuery = "UPDATE channels SET lastclock=GREATEST(lastclock," + str(
                                    maxTime) + "), firstClock=LEAST(firstClock," + str(minTime) + ") WHERE channelid='" + channid[0][0] + "'"
                                daqbroObject.db.query(dbQuery)
                                r = daqbroObject.db.store_result()
                    remarks[j]['lastTime'] = lastParsedTime
                    remarks = sorted(
                        remarks,
                        key=lambda k: k['lastChangeDate'],
                        reverse=True)
                    dbQuery = b"UPDATE parsing SET remarks='" + daqbroObject.db.escape_string(json.dumps(
                        remarks)) + b"' WHERE instid=" + instid[0][0].encode() + b" AND metaid=" + message["metaNo"].encode()
                    daqbroObject.db.query(dbQuery)
                    r = daqbroObject.db.store_result()
        except Exception as e:
            poop = "poop"

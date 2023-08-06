import time
import sys
import json
import traceback
import logging
import multiprocessing
import ntplib
import socket as SOCKETS
import psutil
import struct
import shutil
import uuid
import platform
#import sqlalchemy
import os
import arrow
import math
import json
import signal
import sqlite3
import fnmatch
import zmq
import pyAesCrypt
import snowflake
import re
import ctypes
import concurrent.futures
import hashlib
import daqbrokerSettings
import daqbrokerDatabase
from asteval import Interpreter
from concurrent_log_handler import ConcurrentRotatingFileHandler
from subprocess import call
from subprocess import check_output
#from bcrypt import gensalt
from functools import reduce
from sqlalchemy import create_engine
from sqlalchemy import text, and_, or_, func, select
from sqlalchemy import bindparam
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy.ext.declarative import DeclarativeMeta
from logging.handlers import RotatingFileHandler
from sqlalchemy_utils.functions import database_exists
from sqlalchemy_utils.functions import drop_database
from sqlalchemy_utils.functions import create_database
from flask import Flask
from flask import Blueprint
from flask import Markup
from flask import request
from flask import render_template
from flask import redirect
from flask import send_from_directory
from flask import url_for
from flask import session
from flask import flash
from flask import jsonify
from flask import current_app
from flask import request_tearing_down
from flask_login import UserMixin
from flask_login import LoginManager
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user
from urllib.parse import urlparse
from numpy import asarray, linspace
from scipy.interpolate import interp1d
from numbers import Number
from functools import wraps
from fractions import gcd


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


class InvalidUsage(Exception):

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def connect(request):
    return current_user.conn


def get_directory_structure(rootdir):
    dir = {}
    #print(rootdir)
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys(files)
        fileDefs={x : {'lchange':os.path.getmtime(os.path.join(path, x)), 'size':getSizeData(os.path.getsize(os.path.join(path, x)))} if x not in dirs else {} for x in files}
        #print(fileDefs)
        #print(subdir)
        parent = reduce(dict.get, folders[:-1], dir)
        parent[folders[-1]] = fileDefs
    return dir

def getServerUsers(connection):
    users = []
    result = connection.execute(text("SELECT * FROM daqbroker_settings.users"))
    for row in result:
        users.append(dict(zip(row.keys(), row)))
    return users


def getNTPTime(server):
    ntp = ntplib.NTPClient()
    req = ntp.request(server)
    return req


def resolveAddr(addr, idx, shared):
    try:
        indxObjc = shared[idx]
        indxObjc['addressName'] = socket.gethostbyaddr(addr)[0]
        shared[idx] = indxObjc
        return True
    except BaseException:
        indxObjc['addressName'] = 'N/A'
        shared[idx] = indxObjc
        return False


def gatherChannels(ids, session):
    toReturn = []
    for id in ids:
        chanInfo = False
        #query = text("SELECT * from channels WHERE channelid=:channID")
        #result = connection.execute(query, channID=id)
        channel = session.query(daqbrokerDatabase.channels).filter_by(channelid=id).first()
        if channel:
            obj={}
            for field in channel.__dict__:
                if not field.startswith('_'):
                    obj[field] = getattr(channel, field)
            chanInfo=obj
        chanInfo["instrument"]=channel.chann.meta.Name
        chanInfo["metaid"] = channel.chann.metaid
        #for row in result:
        #    chanInfo = dict(zip(row.keys(), row))
        #    query2 = text("SELECT Name from instruments WHERE instid=:channInst")
        #    result2 = connection.execute(query2, channInst=row["instid"])
        #    for row2 in result2:
        #        chanInfo["instrument"] = row2["Name"]
        toReturn.append(chanInfo)
    return toReturn


def reversed_lines(file):
    newline_char_set = set(['\r', '\n'])
    tail = ""
    for block in reversed_blocks(file):
        if block is not None and len(block) > 0:
            # First split the whole block into lines and reverse the list
            reversed_lines = block.splitlines()
            reversed_lines.reverse()

            # If the last char of the block is not a newline, then the last line
            # crosses a block boundary, and the tail (possible partial line from
            # the previous block) should be added to it.
            if block[-1] not in newline_char_set:
                reversed_lines[0] = reversed_lines[0] + tail

            # Otherwise, the block ended on a line boundary, and the tail is a
            # complete line itself.
            elif len(tail) > 0:
                reversed_lines.insert(0, tail)

            # Within the current block, we can't tell if the first line is complete
            # or not, so we extract it and save it for the next go-round with a new
            # block. We yield instead of returning so all the internal state of this
            # iteration is preserved (how many lines returned, current tail, etc.).
            tail = reversed_lines.pop()

            for reversed_line in reversed_lines:
                yield reversed_line

    # We're out of blocks now; if there's a tail left over from the last block we read,
    # it's the very first line in the file. Yield that and we're done.
    if len(tail) > 0:
        yield tail


def reversed_blocks(file, blocksize=4096):

    # Jump to the end of the file, and save the file offset.
    file.seek(0, os.SEEK_END)
    here = file.tell()

    # When the file offset reaches zero, we've read the whole file.
    while 0 < here:
        # Compute how far back we can step; either there's at least one
        # full block left, or we've gotten close enough to the start that
        # we'll read the whole file.
        delta = min(blocksize, here)

        # Back up to there and read the block; we yield it so that the
        # variable containing the file offset is retained.
        file.seek(here - delta, os.SEEK_SET)
        yield file.read(delta)

        # Move the pointer back by the amount we just handed out. If we've
        # read the last block, "here" will now be zero.
        here -= delta


def getLogEntries(start, end, id, workerList, index, base_dir):
    try:
        scoped = daqbrokerSettings.getScoped()
        session = scoped()
        theJob = session.query(daqbrokerSettings.jobs).filter_by(jobid=id).first()
        lines = []
        with open(os.path.join(base_dir, 'logFile.txt'), 'r') as fin:
            for line in reversed_lines(fin):
                try:
                    theTimeStr = line.split(' ')[0] + ' ' + line.split(' ')[1]
                    timeParse = arrow.get(theTimeStr, 'YYYY/MM/DD HH:mm:ss')
                    if timeParse.timestamp * 1000 < start:
                        break
                    if (timeParse.timestamp * 1000 >= start) and (timeParse.timestamp * 1000 <= end):
                        lines.append(line)
                except Exception as e:
                    continue
        workerList[index] = lines
        theJob.status = 1
        theJob.data = index
        session.commit()
    except Exception as e:
        traceback.print_exc()
        session.rollback()


def checkPaths(context, OLDBPATH, OLDIPATH, OLDAPATH, logPort):
    #localConn = sqlite3.connect('localSettings')
    #localConn.row_factory = dict_factory
    #globals = None
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    globals = session.query(
        daqbrokerSettings.Global).filter_by(
        clock=session.query(
            func.max(
                daqbrokerSettings.Global.clock))).first()
    if globals:
        if globals.backupfolder == OLDBPATH or OLDBPATH == '':
            OLDBPATH = globals.backupfolder
        else:
            try:
                if os.path.isdir(globals.backupfolder):
                    emptyDirectory(globals.backupfolder)
                    for directory in os.listdir(globals.backupfolder):
                        oldPath = os.path.join(globals.backupfolder, directory)
                        newPath = os.path.join(globals.backupfolder, directory)
                        os.rename(oldPath, newPath)
                    OLDBPATH = globals.backupfolder
                    theLogSocket = context.socket(zmq.REQ)
                    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                    toSend = {
                        'req': 'LOG',
                        'type': 'INFO',
                        'process': 'PRODUCER',
                        'message': 'Finished migrating into new backup folder',
                        'method': 'producer'}
                    theLogSocket.send(json.dumps(toSend).encode())
                    theLogSocket.close()
                else:
                    theLogSocket = context.socket(zmq.REQ)
                    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                    toSend = {
                        'req': 'LOG',
                        'type': 'WARNING',
                        'process': 'PRODUCER',
                        'message': 'Could not find new backup folder, returning to old one',
                        'method': 'producer'}
                    theLogSocket.send(json.dumps(toSend).encode())
                    theLogSocket.close()
                    globals.backupfolder = OLDBPATH
            except BaseException:
                theLogSocket = context.socket(zmq.REQ)
                theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                toSend = {
                    'req': 'LOG',
                    'type': 'WARNING',
                    'process': 'PRODUCER',
                    'message': 'Could not migrate to new backup folder, returning to old one',
                    'method': 'producer'}
                theLogSocket.send(json.dumps(toSend).encode())
                theLogSocket.close()
                globals.backupfolder = OLDBPATH
        if globals.importfolder == OLDIPATH or OLDIPATH == '':
            OLDIPATH = globals.importfolder
        else:
            try:
                if os.path.isdir(globals.importfolder):
                    emptyDirectory(globals.importfolder)
                    for directory in os.listdir(globals.importfolder):
                        oldPath = os.path.join(globals.importfolder, directory)
                        newPath = os.path.join(globals.importfolder, directory)
                        os.rename(oldPath, newPath)
                    OLDBPATH = globals.importfolder
                    theLogSocket = context.socket(zmq.REQ)
                    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                    toSend = {
                        'req': 'LOG',
                        'type': 'INFO',
                        'process': 'PRODUCER',
                        'message': 'Finished migrating into new import folder',
                        'method': 'producer'}
                    theLogSocket.send(json.dumps(toSend).encode())
                    theLogSocket.close()
                else:
                    theLogSocket = context.socket(zmq.REQ)
                    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                    toSend = {
                        'req': 'LOG',
                        'type': 'WARNING',
                        'process': 'PRODUCER',
                        'message': 'Could not find to new import folder, returning to old one',
                        'method': 'producer'}
                    theLogSocket.send(json.dumps(toSend).encode())
                    theLogSocket.close()
                    globals.importfolder = OLDIPATH
            except BaseException:
                theLogSocket = context.socket(zmq.REQ)
                theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                toSend = {
                    'req': 'LOG',
                    'type': 'WARNING',
                    'process': 'PRODUCER',
                    'message': 'Could not migrate to new import folder, returning to old one',
                    'method': 'producer'}
                theLogSocket.send(json.dumps(toSend).encode())
                theLogSocket.close()
                globals.importfolder = OLDIPATH
        if globals.tempfolder == OLDAPATH or OLDAPATH == '':
            OLDAPATH = globals.tempfolder
        else:
            try:
                if os.path.isdir(globals.tempfolder):
                    emptyDirectory(globals.tempfolder)
                    for directory in os.listdir(globals.tempfolder):
                        oldPath = os.path.join(globals.tempfolder, directory)
                        newPath = os.path.join(globals.tempfolder, directory)
                        os.rename(oldPath, newPath)
                    OLDBPATH = globals.tempfolder
                    theLogSocket = context.socket(zmq.REQ)
                    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                    toSend = {
                        'req': 'LOG',
                        'type': 'INFO',
                        'process': 'PRODUCER',
                        'message': 'Finished migrating into new addon folder',
                        'method': 'producer'}
                    theLogSocket.send(json.dumps(toSend).encode())
                    theLogSocket.close()
                else:
                    theLogSocket = context.socket(zmq.REQ)
                    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                    toSend = {
                        'req': 'LOG',
                        'type': 'WARNING',
                        'process': 'PRODUCER',
                        'message': 'Could not find to new temporary file folder, returning to old one',
                        'method': 'producer'}
                    theLogSocket.send(json.dumps(toSend).encode())
                    theLogSocket.close()
                    globals.tempfolder = OLDAPATH
            except BaseException:
                theLogSocket = context.socket(zmq.REQ)
                theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                toSend = {
                    'req': 'LOG',
                    'type': 'WARNING',
                    'process': 'PRODUCER',
                    'message': 'Could not migrate to new temporary file folder, returning to old one',
                    'method': 'producer'}
                theLogSocket.send(json.dumps(toSend).encode())
                theLogSocket.close()
                globals.tempfolder = OLDAPATH
    session.commit()
    return (OLDBPATH, OLDIPATH, OLDAPATH)


def emptyDirectory(path):
    if(os.path.isdir(path)):
        dirList = os.listdir(path)
        for inside in dirList:
            if os.path.isdir(os.path.join(path, inside)):
                emptyDirectory(os.path.join(path, inside))
                os.rmdir(os.path.join(path, inside))
            else:
                os.remove(os.path.join(path, inside))
    else:
        os.remove(path)


def getCOMData(device, parseInterval, command, baud, par, bytes, stop, id, workerList, toStore):
    """Auxiliary function used by the :py:func:`getPeripheralData` function to collect data from a local COM port

    :param device: (String) identifier of the device's serial port
    :param parseInterval: (Integer) period in seconds between data gathering
    :param command: (String) command to send the peripheral port in case data is collected by request and not streamed
    :param baud: (String) serial baud rate
    :param par: (String) serial parity
    :param bytes: (String) serial byte length
    :param stop: (String) serial stop bit
    :param id: (Integer) Unused. Defaults to -1
    :param workerList: (List) Unused. Defaults to []
    :param toStore: (Boolean) Unused. Defaults to True

    :returns: Dict object with the following keys:
            | ``status`` : status code of the request (1: done; 0: underway (error); -1: exception)
            | ``error`` : empty string if no exceptions, a traceback if an exception occurred
            | ``data`` : data from the requested resource

    """

    theNode = {"active": True, "name": "localhost"}
    if theNode["active"]:
        try:
            if theNode["name"] == "localhost":
                if stop == "0":
                    stopBits = serial.STOPBITS_ONE
                if stop == "1":
                    stopBits = serial.STOPBITS_ONE_POINT_FIVE
                if stop == "2":
                    stopBits = serial.STOPBITS_ONE_TWO
                if(not command == ""):
                    ser = serial.Serial(device, baudrate=baud, bytesize=bytes, parity=par, stopbits=stopBits, timeout=5)
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
                if not toStore:
                    for i, p in enumerate(workerList):
                        if p["id"] == id:
                            sideways = workerList[i]
                            sideways['status'] = 1
                            sideways['data'] = {'status': 0, 'error': "", "reply": data}
                            workerList[i] = sideways
                    return 0
                else:
                    return {'status': 0, 'error': "", "reply": data}
            else:  # Gotta play here first
                context = zmq.Context()
                for i, p in enumerate(workerList):
                    if p["id"] == id:
                        sideways = workerList[i]
                        sideways['status'] = 1
                        sideways['data'] = {'status': 0, 'error': "", "reply": "remote request"}
                        workerList[i] = sideways
                return 0
        except Exception as e:
            traceback.print_exc()
            if toStore:
                for i, p in enumerate(workerList):
                    if p["id"] == id:
                        sideways = workerList[i]
                        sideways['status'] = -1
                        sideways['error'] = str(e)
                        workerList[i] = sideways
            else:
                return {'status': -1, 'error': str(e), "reply": ""}


def getPortData(port, parseInterval, command, id, workerList, toStore):
    """Auxiliary function used by the :py:func:`getPeripheralData` function to collect data from a local COM port

    :param port: (String) network port of the resource
    :param parseInterval: (Integer) period in seconds between data gathering
    :param command: (String) command to send the peripheral port in case data is collected by request and not streamed
    :param id: (Integer) Unused. Defaults to -1
    :param workerList: (List) Unused. Defaults to []
    :param toStore: (Boolean) Unused. Defaults to True

    :returns: Dict object with the following keys:
            | ``status`` : status code of the request (1: done; 0: underway (error); -1: exception)
            | ``error`` : empty string if no exceptions, a traceback if an exception occurred
            | ``reply`` : data from the requested resource

    """
    theNode = {"active": True, "name": "localhost"}
    if theNode["active"]:
        if theNode["name"] == "localhost":
            try:
                client = SOCKETS.socket(SOCKETS.AF_INET, SOCKETS.SOCK_STREAM)
                if(not command == ""):
                    client.settimeout(5)
                else:
                    client.settimeout(parseInterval / 2)
                server_address = ('localhost', port)
                client.connect(server_address)
                if(not command == ""):
                    client.send(command.encode())
                time.sleep(1)
                reply = ""
                recieved = client.recv(4096)
                reply = reply + recieved.decode()
                if not toStore:
                    for i, p in enumerate(workerList):
                        if p["id"] == id:
                            sideways = workerList[i]
                            sideways['status'] = 1
                            sideways['data'] = {'status': 0, 'error': "", "reply": reply}
                            workerList[i] = sideways
                    return 0
                else:
                    return {'status': 0, 'error': "", "reply": reply}
            except Exception as e:
                if not toStore:
                    traceback.print_exc()
                    for i, p in enumerate(workerList):
                        if p["id"] == id:
                            sideways = workerList[i]
                            sideways['status'] = -1
                            sideways['data'] = str(e)
                            workerList[i] = sideways
                else:
                    return {'status': -1, 'error': str(e), "reply": ""}
        else:  # No toStore testing here as there are no remote requests to this function with a True toStore parameter
            try:
                context = zmq.Context()
                portServer = random.randrange(8000, 8999)
                checkSocket = SOCKETS.socket()
                checkSocket.settimeout(1)
                checkSocket.connect((theNode["address"], theNode["port"]))
                ipLocal = checkSocket.getsockname()[0]
                checkSocket.close()
                machine = "tcp://*:" + str(portServer)
                machine2 = "tcp://" + theNode["address"] + ":" + str(theNode["port"])
                message = {
                    'order': 'GETPORTDATA',
                    'server': ipLocal,
                    'sendBack': portServer,
                    'port': port,
                    'command': command,
                    'parseInterval': parseInterval}
                client = context.socket(zmq.PUSH)
                server = context.socket(zmq.REP)
                if(not command == ""):
                    server.setsockopt(zmq.RCVTIMEO, 5000)
                else:
                    server.setsockopt(zmq.RCVTIMEO, parseInterval * 1000)
                server.bind(machine)
                client.connect(machine2)
                client.send_json(message)
                getBack = server.recv_json()
                for i, p in enumerate(workerList):
                    if p["id"] == id:
                        sideways = workerList[i]
                        sideways['status'] = 1
                        sideways['data'] = getBack["portData"]
                        workerList[i] = sideways
                client.close()
                server.close()
            except Exception as e:
                traceback.print_exc()
                for i, p in enumerate(workerList):
                    if p["id"] == id:
                        sideways = workerList[i]
                        sideways['status'] = -1
                        sideways['error'] = str(e)
                        workerList[i] = sideways
    else:
        return {
            'status': -1,
            'error': "This node is currently not active, please make sure the agent application is running on it and consult your network operator",
            "reply": ""}


def sendNodeQuery(version, ntp):
    """Auxiliary function used by the :py:func:`checkAddresses` function to send a broadcast request to all local area network DAQBroker client machines. This function is used to find unconnected local machines

    :param version: (String) version string
    :param ntp: (Dict) contains information on the current NTP server

    :returns: (List) list of available local area network nodes, including address, unique identifier and display name

    """
    multicast_group = ('224.224.224.224', 10090)
    # Create the datagram socket
    sock = SOCKETS.socket(SOCKETS.AF_INET, SOCKETS.SOCK_DGRAM)
    # Set a timeout so the socket does not block indefinitely when trying
    # to receive data.
    sock.settimeout(5)
    # Set the time-to-live for messages to 1 so they do not go past the
    # local network segment.
    ttl = struct.pack('b', 1)
    sock.setsockopt(SOCKETS.IPPROTO_IP, SOCKETS.IP_MULTICAST_TTL, ttl)
    try:
        base_dir = '.'
        if getattr(sys, 'frozen', False):
            base_dir = os.path.join(sys._MEIPASS)
        # Send data to the multicast group
        info = {
            'service': 'DAQBRoker server',
            'version': version,
            'id': snowflake.make_snowflake(
                snowflake_file=os.path.join(base_dir, 'snowflake')),
            'message': 'show',
            'ntp': ntp}
        toSend = json.dumps(info).encode()
        for i in range(0, 5):
            sent = sock.sendto(toSend, multicast_group)
            time.sleep(1)
        nodes = []
        while True:
            try:
                data, server = sock.recvfrom(10240)
                try:
                    processed = json.loads(data.decode())
                    if('id' in processed) and ('node' in processed):
                        alreadyFoundNode = False
                        for node in nodes:
                            if processed["id"] == node["id"]:
                                alreadyFoundNode = True
                                break
                        if not alreadyFoundNode:
                            nodes.append({'id': processed["id"],
                                          'node': processed["node"],
                                          'details': processed["details"],
                                          'serverAddr': processed["serverAddr"],
                                          'address': server[0],
                                          'port': processed["port"]})
                except BaseException:
                    # traceback.print_exc()
                    poop = 'poop'
            except BaseException:  # timeout
                # traceback.print_exc()
                break
    finally:
        sock.close()
        return nodes


def refreshNodes(goodNodes):
    for node in goodNodes:
        machine = "tcp://" + node['remote'] + ":" + str(node['remotePort'])
        zmq_socket = context.socket(zmq.PUSH)
        zmq_socket.setsockopt(zmq.LINGER, 1000)
        try:
            zmq_socket.connect(machine)
            work_message = {
                'order': "update",
                'server': node['local'],
                'sendBack': sendBack,
                'theNode': node['remote'],
                'extra': {
                    'serverNTP': daqbroObject.globals[0][5].decode(),
                    'tSync': node['NTP']}}
            zmq_socket.send_json(work_message)
            zmq_socket.close()
        except Exception as e:
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
                'process': 'PRODUCER',
                'message': str(e),
                'filename': filename,
                'lineno': lineno,
                'funname': funname,
                'line': line}
            theLogSocket.send(json.dumps(toSend).encode())
            theLogSocket.close()


def sendSubscriberEmails():
    try:
        for q, valDB in enumerate(daqbroObject.databases):
            if(int(valDB[1]) == 1):
                realvalDB = 'daqbro_' + valDB[0].decode()
                dbQuery = "USE " + realvalDB
                daqbroObject.db.query(dbQuery)
                daqbroObject.db.store_result()
                dbQuery = "SELECT start,run,summary,active FROM runlist WHERE start>" + \
                    str(time.time() * 1000 - (24 * 60 * 60 * 1000)) + " ORDER BY start"
                daqbroObject.db.query(dbQuery)
                r = daqbroObject.db.store_result()
                runs = r.fetch_row(0)
                textActive = 'none'
                textRuns = 'none'
                lastRunSearch = time.time()
                if(len(runs) > 0):
                    for u, run in enumerate(runs):
                        startStr = datetime.fromtimestamp(int(run[0]) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        if run[2] is None:
                            summary = 'None'
                        else:
                            summary = run[2].decode()
                        if int(run[3]) == 1:
                            textActive = 'Run ' + run[1].decode() + ' : Started - ' + startStr + \
                                ' | Summary :  ' + summary + '\n'
                        else:
                            textRuns = textRuns + 'Run ' + \
                                run[1].decode() + ' : Started - ' + startStr + ' | Summary :  ' + summary + '\n'
                    totalText = 'You are recieveing this email because you subscribed to DAQBroker\'s ' + valDB[0].decode() + ' database and it is a currently active database. As such, there have been experiments preformed since the previous day. Here is a small summary of what was done.\n\nCurrent active experiment: \n\n\t' + \
                        textActive + '\nOther experiments preformed:\n\n\t' + textRuns + '\n\nThis is an automatically generated message. Please contact your system administrator if you wish to not recieve these messages in the future'
                    msg = MIMEText(totalText)
                    s = smtplib.SMTP('localhost')
                    try:
                        for u, email in enumerate(daqbroObject.subscribers[realvalDB]):
                            msg['Subject'] = 'Daily experiment breakdown - ' + valDB[0].decode()
                            msg['From'] = 'noreply'
                            msg['To'] = email[0].decode()
                            s.send_message(msg)
                        s.quit()
                    except Exception as e:
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
                            'process': 'PRODUCER',
                            'message': str(e),
                            'filename': filename,
                            'lineno': lineno,
                            'funname': funname,
                            'line': line}
                        theLogSocket.send(json.dumps(toSend).encode())
                        theLogSocket.close()
    except Exception as e:
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
            'process': 'PRODUCER',
            'message': str(e),
            'filename': filename,
            'lineno': lineno,
            'funname': funname,
            'line': line}
        theLogSocket.send(json.dumps(toSend).encode())
        theLogSocket.close()


def checkUserPermissions():
    for q, valDB in enumerate(daqbroObject.databases):
        realvalDB = 'daqbro_' + valDB[0].decode()
        dbQuery = "USE " + realvalDB
        daqbroObject.db.query(dbQuery)
        daqbroObject.db.store_result()
        for x in range(0, len(daqbroObject.instruments[realvalDB])):
            try:
                dbQuery = "GRANT ALL ON `" + realvalDB + "`.`" + \
                    daqbroObject.instruments[realvalDB][x][0].decode() + "_data` TO '" + daqbroObject.instruments[realvalDB][x][4].decode() + "'@'%'"
                daqbroObject.db.query(dbQuery)
                daqbroObject.db.store_result()
            except Exception as e:
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
                    'process': 'PRODUCER',
                    'message': str(e),
                    'filename': filename,
                    'lineno': lineno,
                    'funname': funname,
                    'line': line}
                theLogSocket.send(json.dumps(toSend).encode())
                theLogSocket.close()


def getChannelData(
        channelid,
        startTime,
        endTime,
        fullResolution,
        screenSize,
        id,
        caching,
        workerList,
        form,
        toStore,
        emptyIndex):
    Session = sessionmaker(bind=form)
    session = Session()
    scoped = daqbrokerSettings.getScoped()
    localSession = scoped()
    # print(session)
    # print(channelid,
    #     startTime,
    #     endTime,
    #     fullResolution,
    #     screenSize,
    #     id,
    #     caching,
    #     form,
    #     toStore,
    #     emptyIndex)
    try:
        channel = session.query(daqbrokerDatabase.channels).filter_by(channelid=channelid).first()
        if channel:
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
                'name': channel.Name,
                'iname': channel.chann.meta.Name,
                'channelID': channelid,
                'channeltype': channel.channeltype,
                'remarks': channel.remarks,
                'metaid': channel.metaid,
                'data': []
            }
            (dataClass, customClass) = daqbrokerDatabase.createInstrumentTable(toReturn['iname'], [
                {'name': channel.Name, 'type': channel.channeltype}], False)
            if channel.channeltype == 3:
                tableRef = daqbrokerDatabase.daqbroker_database.metadata.tables[toReturn['iname']+'_custom']
                dataTable = customClass
            else:
                tableRef = daqbrokerDatabase.daqbroker_database.metadata.tables[toReturn['iname']+"_data"]
                dataTable = dataClass
            mapper(dataTable, tableRef)
            times = []
            for time in session.query(dataTable.clock).filter(dataTable.clock <= int(endTime)).filter(dataTable.clock > int(startTime)).filter(getattr(dataTable, channel.Name).isnot(None)).all():
                times.append(time[0])
            if fullResolution:
                jump = 1
            else:
                jump = int(math.ceil(len(times)/screenSize))
            times = [int(x) for i, x in enumerate(times) if i % jump == 0]
            delta = None
            delta2 = None
            M2 = None
            deltaTime = None
            delta2Time = None
            M2Time = None
            lastClock = None
            for i,row in enumerate(session.query(dataTable).filter(dataTable.clock.in_(times)).all()):
                if not (channel.channeltype == 1):
                    toReturn["data"].append([row.clock, float(getattr(row, channel.Name))])
                    if toReturn["max"]:
                        toReturn["max"] = max(toReturn["max"],toReturn["data"][-1][1])
                    else:
                        toReturn["max"] = toReturn["data"][-1][1]
                    if toReturn["min"]:
                        toReturn["min"] = min(toReturn["min"],toReturn["data"][-1][1])
                    else:
                        toReturn["min"] = toReturn["data"][-1][1]
                else:
                    toReturn["data"].append([row.clock, getattr(row, channel.Name)])
                if toReturn["maxTime"]:
                    toReturn["maxTime"] = max(toReturn["maxTime"], toReturn["data"][-1][0])
                else:
                    toReturn["maxTime"] = toReturn["data"][-1][0]
                if toReturn["minTime"]:
                    toReturn["minTime"] = min(toReturn["minTime"], toReturn["data"][-1][0])
                else:
                    toReturn["minClock"] = toReturn["data"][-1][0]
                if lastClock is not None:
                    if toReturn["maxTimeStep"] < row.clock - lastClock:
                        toReturn["maxTimeStep"] = row.clock - lastClock
                else:
                    toReturn["maxTimeStep"] = 0
                if lastClock is not None:
                    if toReturn["minTimeStep"] > row.clock - lastClock:
                        toReturn["minTimeStep"] = row.clock - lastClock
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
                    if not (channel.channeltype == 1):
                        toReturn["mean"] = float(getattr(row, channel.Name))
                    toReturn["stdTime"] = 0
                    toReturn["meanTime"] = 0
                else:
                    if not (channel.channeltype == 1):
                        delta = getattr(row, channel.Name) - toReturn["mean"]
                        toReturn["mean"] = toReturn["mean"] + delta / float(i)
                        delta2 = getattr(row, channel.Name) - toReturn["mean"]
                        M2 = M2 + delta * delta2
                    deltaTime = row.clock - lastClock - toReturn["meanTime"]
                    toReturn["meanTime"] = toReturn["meanTime"] + deltaTime / float(i)
                    delta2Time = row.clock - lastClock - toReturn["meanTime"]
                    M2Time = M2Time + deltaTime * delta2Time
                    if i > 1:
                        toReturn["std"] = math.sqrt(M2 / (i - 1))
                        toReturn["stdTime"] = math.sqrt(M2Time / (i - 1))
                lastClock = row.clock
            workerList[emptyIndex] = toReturn
            jobstable = daqbrokerSettings.daqbroker_settings_local.metadata.tables["jobs"]
            localSession.execute(jobstable.update().where(jobstable.c.jobid == id).values({'status':1}))
            #print(emptyIndex, len(toReturn["data"]), "DONE")
        else:
            jobstable = daqbrokerSettings.daqbroker_settings_local.metadata.tables["jobs"]
            localSession.execute(jobstable.update().where(jobstable.c.jobid == id).values({'status': -1,'error':"Could not find requested channel"}))
            workerList[emptyIndex] = {}
        localSession.commit()
        localSession.flush()
    except Exception as e:
        traceback.print_exc()
        localSession.rollback()
        try:
            localSession.execute(jobstable.update().where(jobstable.c.jobid == id).values({'status': -1, 'error': str(e)}))
            localSession.commit()
            workerList[emptyIndex] = {}
        except:
            traceback.print_exc()
            localSession.rollback
        #Maybe put an error part around here, but this will fail =(
    finally:
        localSession.remove()


def calculateExpressionData(
        expression,
        startTime,
        endTime,
        fullResolution,
        screenSize,
        id,
        caching,
        workerList,
        form,
        toStore,
        emptyIndex):
    try:
        a = Interpreter(no_for=True, no_while=True, no_print=True, no_delete=True, no_assert=True)
        connection = False
        toReturn = {}
        if caching == 1:
            engineURL = form['serverEngine'] + '://' + form['username'] + ':' + \
                form['password'] + "@" + form['serverName'] + "/" + form['database']
            engine = create_engine(engineURL)
            try:
                connection = engine.connect()
            except BaseException:
                connection = False
        else:
            connection = app.connect(form)
        if connection:
            forbiddenStrings = [
                'connection',
                'os.',
                'sh.',
                'multiprocessing.',
                'sys.']  # Must find more exploitation methods
            for badString in forbiddenStrings:
                if expression.find(badString) >= 0:
                    raise InvalidUsage("You are trying to do forbidden things! Please stop", status_code=500)
            funcDeclares = re.findall(r'ID\(\d*\)', expression)
            ids = list(set([int(re.search(r"\d+", x).group()) for x in funcDeclares]))
            gatheredChannels = gatherChannels(ids, connection)
            if False in gatheredChannels:
                raise InvalidUsage(
                    "A provided channel was not caught, make sure you are using the correct channel IDs an try again",
                    status_code=500)
            channelData = []
            for channel in gatheredChannels:
                channelData.append(
                    getChannelData(
                        channel["channelid"], startTime, endTime, fullResolution, screenSize, id, -1, [], form, toStore, -1))
            minStep = 0
            for i, channData in enumerate(channelData):
                if channData["minTimeStep"] is not None:
                    if not minStep:
                        minStep = channData["minTimeStep"]
                    else:
                        if channData["minTimeStep"] < minStep:
                            minStep = channData["minTimeStep"]
                if len(channData["data"]) < 1:
                    channelData[i]["data"] = [[startTime, channelData[i]["closestValueDown"]],
                                              [endTime, channelData[i]["closestValueDown"]]]
            if fullResolution:
                channelData = interpolateDataArray(channelData, minStep, startTime, endTime, -1)
            else:
                channelData = interpolateDataArray(channelData, minStep, startTime, endTime, screenSize)
            if fullResolution:
                timeList = linspace(int(startTime), int(endTime), int(
                    (int(endTime) - int(startTime)) / int(minStep))).tolist()
            else:
                timeList = linspace(int(startTime), int(endTime), int(screenSize)).tolist()
            dataToReturn = []
            for t, time in enumerate(timeList):
                exprVal = None
                returnVal = None
                toTest = expression
                for i, channid in enumerate(ids):
                    theChannel = [x for x in channelData if x["channelID"] == channid]  # Should only be one channel
                    if theChannel[0]["channeltype"] == 1:
                        toTest = toTest.replace("ID(" + str(channid) + ")", "'" +
                                                str(getDataArray(channid, t, channelData)) + "'")
                    else:
                        toTest = toTest.replace("ID(" + str(channid) + ")", str(getDataArray(channid, t, channelData)))
                returnVal = a(toTest, show_errors=False)
                if "exprVal" in a.symtable:
                    exprVal = a.symtable["exprVal"]
                    a.symtable["exprVal"] = None
                if len(a.error) > 0:
                    exprVal = None
                    returnVal = None
                if returnVal is None:
                    if exprVal is None:
                        dataToReturn.append([time, None])
                    else:
                        if isinstance(exprVal, Number):
                            dataToReturn.append([time, exprVal])
                        else:
                            dataToReturn.append([time, None])
                elif isinstance(returnVal, Number):
                    dataToReturn.append([time, returnVal])
                else:
                    dataToReturn.append([time, None])
            #	values=()
            #	for i,idChann in enumerate(ids):
            #		values=values+(getDataArray(id,t,channelData),)
            #	if math.isnan(float(func(*values))):#Cunundrum: Should I ignore these values, or should I keep them as None? - problem, Plotly interprets None --> null as actual ignored values and they look weird in the plot
            #		dataToReturn.append([time,None])
            #	else:
            #		dataToReturn.append([time,float(func(*values))])
            toReturn = {'data': dataToReturn, 'type': 'expression'}
            if caching == 1:
                workerList[emptyIndex] = toReturn
                thisUser = getUserDetails(form['username'], connection)
                if thisUser['type'] == 1:
                    jobsTable = "jobs"
                else:
                    jobsTable = form['username'] + "_userview_jobs"
                connection.execute(
                    text(
                        "UPDATE " +
                        jobsTable +
                        " SET status=:status WHERE jobid=:jobid"),
                    status=1,
                    jobid=id)
                return 0
            if caching == 0:
                return toReturn
        else:
            raise InvalidUsage('Error connecting to database', status_code=500)
    except Exception as e:
        if caching == 1:
            thisUser = getUserDetails(form['username'], connection)
            if thisUser['type'] == 1:
                jobsTable = "jobs"
            else:
                jobsTable = form['username'] + "_userview_jobs"
            connection.execute(
                text(
                    "UPDATE " +
                    jobsTable +
                    " SET status=:status WHERE jobid=:jobid"),
                status=-
                1,
                jobid=id)
        traceback.print_exc()
        if connection:
            connection.close()
        return -1


def interpolateDataArray(dataArray, minResolution, startTime, endTime, screenSize):
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
    # This can be milliseconds but it can also be hours and days. This can lead to bad interpolations in some cases.
    if resolution:
        # print(startTime,endTime,screenSize)
        if(screenSize < 0):  # I want to use the smallest resolution posible
            timeInt = linspace(int(startTime), int(endTime), int((int(endTime) - int(startTime)) / int(resolution)))
        else:  # Using screen size to limit resolution
            timeInt = linspace(int(startTime), int(endTime), int(screenSize))
        if type == 1:
            strings = [x for x in data[:, 1]]
            data = asarray([[int(x), id(strings[i])] for i, x in enumerate(data[:, 0])])
        intF = interp1d(data[:, 0], data, axis=0, kind="zero", fill_value=(data[0], data[-1]), bounds_error=False)
        newData = intF(timeInt)
        if type == 1:
            newData = [[x[0], ctypes.cast(int(x[1]), ctypes.py_object).value] for x in newData]
    else:  # This is for the case that EVERYTHING is empty, gotta find a good way to do this
        if type == 1:
            strings = [x for x in data[:, 1]]
            data = asarray([[int(x), id(strings[i])] for i, x in enumerate(data[:, 0])])
        timeInt = linspace(int(startTime), int(endTime), 10)
        intF = interp1d(data[:, 0], data, axis=0, kind="zero", fill_value=(data[0], data[-1]), bounds_error=False)
        newData = intF(timeInt)
        if type == 1:
            newData = [[x[0], ctypes.cast(int(x[1]), ctypes.py_object).value] for x in newData]
    if type == 1:
        del strings
    return newData


def getDataArray(channID, idx, channelData):
    foundChannel = False
    for channData in channelData:
        if channData["channelID"] == channID:
            return channData["data"][idx][1]


def getUserDetails(username, connection):
    """Auxiliary function used by several endpoints of the DAQBroker web application to gather database user information"""
    #session = daqbrokerSettings.scoped()
    #user = sele
    result = connection.execute(
        text("SELECT * FROM daqbroker_settings.users WHERE username=:theUser"),
        theUser=username)
    user = None
    for row in result:  # Should only return one, primary key and all
        user = dict(zip(row.keys(), row))
    return user


def parseMeta(server, db, instrument, meta, paths, logPort, lockList, session):
    try:
        database = db
        theContext = zmq.Context()
        if(meta.parsing[0].locked == False and meta.parsing[0].forcelock == False):
            remarks = json.loads(meta.parsing[0].remarks)
            metaremarks = json.loads(meta.remarks)
            metaType = meta.type
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
                meta.parsing[0].locked=True
                meta.lastAction=time.time()
                session.commit()
                customChannels = [x for x in meta.channels if x.channeltype == 3]
                if metaremarks["toParse"] =='1' or metaremarks["toParse"] =='true' or not metaremarks["toParse"] =='':  # This is for file parsing
                    if metaType == 0:  # File parsing
                        if metaremarks['parsingInfo']['separator'] == 'tab':
                            metaremarks['parsingInfo']['separator'] = '\t'
                        elif metaremarks['parsingInfo']['separator'] == 'comma':
                            metaremarks['parsingInfo']['separator'] = ','
                        elif metaremarks['parsingInfo']['separator'] == 'semicolon':
                            metaremarks['parsingInfo']['separator'] = ';'
                        elif metaremarks['parsingInfo']['separator'] == 'colon':
                            metaremarks['parsingInfo']['separator'] = ':'
                        elif metaremarks['parsingInfo']['separator'] == 'space':
                            metaremarks['parsingInfo']['separator'] = ' '
                        header = []
                        for channel in meta.channels:
                            if not channel.channeltype == 2:
                                header.append({'name': channel.Name,
                                               'alias': channel.alias,
                                               "type": channel.channeltype,
                                               'channelid': channel.channelid,
                                               'firstClock': channel.firstClock,
                                               'lastclock': channel.lastclock})
                        lastFound = 0
                        base_dir = '.'
                        if getattr(sys, 'frozen', False):
                            base_dir = os.path.join(sys._MEIPASS)
                        thePath = os.path.join(base_dir, paths["BACKUPPATH"], server, database, instrument["Name"], meta.name)
                        if 'getNested' in metaremarks:
                            if(metaremarks['getNested'] == "1" or metaremarks['getNested'] == "true" or metaremarks['getNested']):
                                walked = os.walk(thePath)
                                orderedFiles = []
                                for vals in walked:
                                    for file in vals[2]:
                                        orderedFiles.append(os.path.join(vals[0], file))
                            else:
                                def mtime(f): return os.stat(f).st_mtime
                                orderedFiles = list(sorted([os.path.join(thePath, x)
                                                            for x in os.listdir(thePath)], key=mtime, reverse=True))
                        else:
                            def mtime(f): return os.stat(f).st_mtime
                            orderedFiles = list(sorted([os.path.join(thePath, x)
                                                        for x in os.listdir(thePath)], key=mtime, reverse=True))
                        # reduce file list by comparing with pattern and extension
                        filesWithPattern = [
                            x for x in orderedFiles if fnmatch.fnmatch(
                                x,
                                '*' +
                                metaremarks["pattern"] +
                                '*.' +
                                metaremarks["extension"])]  # reduced list
                        foundSyncedFiles = [x for t in orderedFiles for x in remarks if t == x['name']]
                        foundSyncedFilesNames = [
                            x for t in remarks for x in orderedFiles if(
                                x == t['name'] and fnmatch.fnmatch(
                                    t['name'],
                                    '*' +
                                    metaremarks["pattern"] +
                                    '*.' +
                                    metaremarks["extension"]))]
                        notFoundSynced = list(set(filesWithPattern) - set(foundSyncedFilesNames))
                        #print(foundSyncedFiles)
                        for file in foundSyncedFiles:
                            j = remarks.index(file)
                            changes = False
                            linesParsed = int(remarks[j]["linesParsed"])
                            linesNotParsed = int(remarks[j]["linesNotParsed"])
                            lastParsedLine = int(remarks[j]["lastParsedLine"])
                            lastChangeDate = int(remarks[j]["lastChangeDate"])
                            parsedSize = int(remarks[j]["parsedSize"])
                            notParsedSize = int(remarks[j]["notParsedSize"])
                            totalLines = int(remarks[j]["totalLines"])
                            if 'lastTime' in remarks[j]:
                                lastTime = float(remarks[j]["lastTime"])
                            if 'parsedSize' not in file:
                                file['parsedSize'] = os.path.getsize(file['name'])
                            sizeDiff = file['parsedSize'] + file["notParsedSize"]
                            #if abs(os.path.getsize(file["name"]) - sizeDiff) > len(header) * 30
                            (lines, readSize) = collectFileLines(file['name'], metaremarks, header, offset=sizeDiff)
                            #print(len(lines),lines[0],lines[-1])
                            size = os.path.getsize(file['name'])
                            parseResult = parseFileLines(
                                lines,
                                header,
                                metaremarks['parsingInfo']['dataType'],
                                metaremarks,
                                instrument["Name"],
                                session,
                                db,
                                logPort,
                                meta.metaid)
                            linesParsed = linesParsed + parseResult["linesParsed"]
                            linesNotParsed = linesNotParsed + parseResult["linesNotParsed"]
                            lastParsedLine = lastParsedLine + linesParsed + linesNotParsed
                            totalLines = totalLines + len(lines)
                            parsedSize = parsedSize + parseResult["parsedSize"]
                            notParsedSize = notParsedSize + parseResult["notParsedSize"]
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
                                "totalLines": totalLines,
                                'lastTime': lastTime,
                                'parsedSize': parsedSize,
                                'notParsedSize': notParsedSize
                            }
                            remarks = sorted(remarks, key=lambda k: k['lastChangeDate'], reverse=True)
                            meta.parsing[0].remarks=json.dumps(remarks)
                        for file in notFoundSynced:
                            readSize = 0
                            lines = []
                            notDone = True
                            (lines, readSize) = collectFileLines(file, metaremarks, header)
                            if int(metaremarks['parsingInfo']['dataType']) == 1:
                                linesParse = lines
                            else:
                                linesParse = lines[int(metaremarks['parsingInfo']['headerLines']):]
                            #print(len(lines), lines[0], lines[-1])
                            parseResult = parseFileLines(linesParse,
                                                         header,
                                                         metaremarks['parsingInfo']['dataType'],
                                                         metaremarks,
                                                         instrument["Name"],
                                                         session,
                                                         database,
                                                         logPort,
                                                         meta.metaid)
                            #print(file, len(lines))
                            linesParsed = parseResult["linesParsed"]
                            linesNotParsed = parseResult["linesNotParsed"]
                            lastTime = 0
                            if "lastTime" in parseResult:
                                lastTime = float(parseResult["lastTime"])
                            else:
                                lastTime = 0
                            # Not always necessarily true but important to ensure that monitoring continues
                            lastParsedLine = parseResult["linesParsed"] + parseResult["linesNotParsed"]
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
                                            'parsedSize': parseResult["parsedSize"],
                                            'notParsedSize': parseResult["notParsedSize"]
                                            })
                            #print(parseResult["parsedSize"],readSize)
                            remarks = sorted(remarks, key=lambda k: k['lastChangeDate'], reverse=True)
                            meta.parsing[0].remarks = json.dumps(remarks)
                    if len(customChannels) > 0:
                        for channel in customChannels:
                            parseCustomChannel(instrument, channel, session)
                session.commit()
            except Exception as e:
                session.rollback()
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
                meta.parsing[0].locked = 0
                session.commit()
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
        # connection.close()
        for i, el in enumerate(lockList):
            if el['instrument'] == instrument["Name"] and el['meta'] == meta.name:
                temp = {'server':server,'database': database, 'instrument': instrument["Name"], 'meta': meta.name, 'locked': False}
                lockList[i] = temp

def collectFileLines(file,metaremarks,header,offset = 0):
    lines = []
    with open(file, 'rU') as f:
        if offset > 0:
            f.seek(offset)
        if int(metaremarks['parsingInfo']['dataType']) == 1:
            while len(lines) < int(metaremarks['parsingInfo']['colSize']) * len(header) * 2:
                line = f.readline()
                readSize = f.tell()
                if not line: break
                lines.append(line)
        else:
            while len(lines) < 1000:
                line = f.readline()
                readSize = f.tell()
                if not line: break
                lines.append(line)
        return (lines, readSize)

def interpolateDataArray(dataArray, minResolution, startTime, endTime, screenSize):
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
    # This can be milliseconds but it can also be hours and days. This can lead to bad interpolations in some cases.
    if resolution:
        # print(startTime,endTime,screenSize)
        if(screenSize < 0):  # I want to use the smallest resolution posible
            timeInt = linspace(int(startTime), int(endTime), int((int(endTime) - int(startTime)) / int(resolution)))
        else:  # Using screen size to limit resolution
            timeInt = linspace(int(startTime), int(endTime), int(screenSize))
        if type == 1:
            strings = [x for x in data[:, 1]]
            data = asarray([[int(x), id(strings[i])] for i, x in enumerate(data[:, 0])])
        intF = interp1d(data[:, 0], data, axis=0, kind="zero", fill_value=(data[0], data[-1]), bounds_error=False)
        newData = intF(timeInt)
        if type == 1:
            newData = [[x[0], ctypes.cast(int(x[1]), ctypes.py_object).value] for x in newData]
    else:  # This is for the case that EVERYTHING is empty, gotta find a good way to do this
        if type == 1:
            strings = [x for x in data[:, 1]]
            data = asarray([[int(x), id(strings[i])] for i, x in enumerate(data[:, 0])])
        timeInt = linspace(int(startTime), int(endTime), 10)
        intF = interp1d(data[:, 0], data, axis=0, kind="zero", fill_value=(data[0], data[-1]), bounds_error=False)
        newData = intF(timeInt)
        if type == 1:
            newData = [[x[0], ctypes.cast(int(x[1]), ctypes.py_object).value] for x in newData]
    if type == 1:
        del strings
    return newData

def getDataArray(channID, idx, channelData):
    for channData in channelData:
        if channData["channelID"] == channID:
            return channData["data"][idx][1]


def lcm(list):
    LCM = 1
    for i in list:
        LCM = LCM * i / gcd(LCM, i)
    return LCM


def parseCustomChannel(instrument, channel, session):
    try:
        #print(instrument, channel, session)
        tableRef = daqbrokerDatabase.daqbroker_database.metadata.tables[instrument["Name"] + "_custom"]
        (dataClass, customClass) = daqbrokerDatabase.createInstrumentTable(instrument["Name"], [{'name': channel.Name, 'type': channel.channeltype}], False)
        mapper(customClass,tableRef)
        a = Interpreter(no_for=True, no_while=True, no_print=True, no_delete=True, no_assert=True)
        expression = json.loads(channel.remarks)["customExpression"]
        forbiddenStrings = ['daqbroObject', 'connection', 'os.', 'sh.',
            'multiprocessing.', 'sys.']  # Must find more exploitation methods
        for badString in forbiddenStrings:
            if expression.find(badString) >= 0:
                raise InvalidUsage("You are trying to do forbidden things! Please stop", status_code=500)
        funcDeclares = re.findall(r'ID\(\d*\)', expression)
        ids = list(set([int(re.search(r"\d+", x).group()) for x in funcDeclares]))
        gatheredChannels = gatherChannels(ids, session)
        if False in gatheredChannels:
            print("Bad expression - someone's trying forbidden things")
            return -1
        maxClockResult=session.query(func.max(customClass.clock)).first()
        if maxClockResult[0]:
            maxClock=maxClockResult[0]
        else:
            maxClock=0
        #print(maxClock)
        metaids = []
        parseInts = []
        metaids = list(set([x["metaid"] for x in gatheredChannels]))
        for meta in session.query(daqbrokerDatabase.instmeta).filter(daqbrokerDatabase.instmeta.metaid.in_(metaids)):
            remarks=json.loads(meta.remarks)
            if "parseInterval" in remarks:
                parseInts.append(int(remarks["parseInterval"]))
        if len(parseInts) > 0:
            maxClock = maxClock - 2 * (lcm(parseInts) * 1000)
        # Getting the data from the channels
        channelData = []
        for gatheredChannel in gatheredChannels:
            if gatheredChannel["channeltype"]==3:
                theTable = daqbrokerDatabase.daqbroker_database.metadata.tables[gatheredChannel["instrument"]+"_custom"]
                #tableName = gatheredChannel["instrument"]+"_custom"
            else:
                theTable = daqbrokerDatabase.daqbroker_database.metadata.tables[gatheredChannel["instrument"] + "_data"]
                #tableName = gatheredChannel["instrument"] + "_data"
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
                'iname': gatheredChannel["instrument"],
                'channelID': gatheredChannel["channelid"],
                'channeltype': gatheredChannel["channeltype"],
                'remarks': gatheredChannel["remarks"],
                'metaid': gatheredChannel["metaid"],
                'data': []}
            delta = None
            delta2 = None
            M2 = None
            deltaTime = None
            delta2Time = None
            M2Time = None
            lastClock = None
            query = session.query(theTable.c.clock,getattr(theTable.c,gatheredChannel["Name"])).filter(theTable.c.clock >= maxClock).filter(theTable.c.clock <= time.time()*1000).filter(theTable.c.clock.isnot(None)).order_by(theTable.c.clock.asc()).limit(1000)
            for i,row in enumerate(query):
                toReturn["data"].append([row.clock, getattr(row,gatheredChannel["Name"])])
                if not (gatheredChannel["channeltype"] == 1):
                    if toReturn["max"]:
                        toReturn["max"] = max(toReturn["max"],getattr(row, gatheredChannel["Name"]))
                    else:
                        toReturn["max"]=getattr(theTable.c,gatheredChannel["Name"])
                    if toReturn["min"]:
                        toReturn["min"] = min(toReturn["min"], getattr(row, gatheredChannel["Name"]))
                    else:
                        toReturn["min"] = getattr(theTable.c, gatheredChannel["Name"])
                if toReturn["maxTime"]:
                    toReturn["maxTime"] = max(toReturn["maxTime"], float(row.clock))
                else:
                    toReturn["maxTime"] = float(row.clock)
                if toReturn["minTime"]:
                    toReturn["minTime"] = min(toReturn["minTime"], float(row.clock))
                else:
                    toReturn["minTime"] = float(row.clock)
                if lastClock is not None:
                    if toReturn["maxTimeStep"]:
                        toReturn["maxTimeStep"] =max(toReturn["maxTimeStep"], abs(float(row.clock) - lastClock))
                    else:
                        toReturn["maxTimeStep"] = abs(float(row.clock) - lastClock)
                    if toReturn["minTimeStep"]:
                        toReturn["minTimeStep"] =min(toReturn["minTimeStep"], abs(float(row.clock) - lastClock))
                    else:
                        toReturn["minTimeStep"] = abs(float(row.clock) - lastClock)
                if M2 is None:
                    M2 = 0
                    delta = 0
                    delta2 = 0
                    M2Time = 0
                    deltaTime = 0
                    delta2Time = 0
                    toReturn["std"] = 0
                    if not (gatheredChannel["channeltype"] == 1):
                        toReturn["mean"] = float(getattr(row,gatheredChannel["Name"]))
                    toReturn["stdTime"] = 0
                    toReturn["meanTime"] = 0
                else:
                    if not (gatheredChannel["channeltype"] == 1):
                        delta = float(getattr(row,gatheredChannel["Name"])) - toReturn["mean"]
                        toReturn["mean"] = toReturn["mean"] + delta / float(i)
                        delta2 = float(getattr(row,gatheredChannel["Name"])) - toReturn["mean"]
                        M2 = M2 + delta * delta2
                    deltaTime = (float(row.clock) - lastClock) - toReturn["meanTime"]
                    toReturn["meanTime"] = toReturn["meanTime"] + deltaTime / float(i)
                    delta2Time = (float(row.clock) - lastClock) - toReturn["meanTime"]
                    M2Time = M2Time + deltaTime * delta2Time
                    if i > 1:
                        toReturn["std"] = math.sqrt(M2 / (i - 1))
                        toReturn["stdTime"] = math.sqrt(M2Time / (i - 1))
                lastClock = float(row.clock)
                closestTop = session.query(theTable.c.clock,getattr(theTable.c,gatheredChannel["Name"])).filter(theTable.c.clock >= time.time()*1000).filter(getattr(theTable.c,gatheredChannel["Name"]).isnot(None)).limit(1).first()
                closestBottom = session.query(theTable.c.clock,getattr(theTable.c,gatheredChannel["Name"])).filter(theTable.c.clock <= maxClock).filter(getattr(theTable.c,gatheredChannel["Name"]).isnot(None)).limit(1).first()
                if closestBottom:
                    toReturn["closestValueDown"] = getattr(closestBottom, gatheredChannel["Name"])
                    toReturn["closestClockDown"] = closestBottom.clock
                if closestTop:
                    toReturn["closestValueUp"] = getattr(closestTop,gatheredChannel["Name"])
                    toReturn["closestClockUp"] = closestTop.clock
            if len(toReturn["data"])<1:
                toReturn=[[toReturn["closestClockDown"],toReturn["closestValueDown"]],[toReturn["closestClockUp"],toReturn["closestValueUp"]]]
            channelData.append(toReturn)
            minStep = 0
            maxChannClock = 0
            minChannClock = 10000000000000000000000
            for i, channData in enumerate(channelData):
                #print(len(channData["data"]))
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
             #print(channelData)
        #print(minStep,minChannClock,maxChannClock)
        channelData = interpolateDataArray(channelData, minStep, minChannClock, maxChannClock, -1)
        timeList = linspace(int(minChannClock), int(maxChannClock), int(
             (int(maxChannClock) - int(minChannClock)) / int(minStep)))
        timeList = [int(x) for x in timeList]
        emptyDict={}
        emptyDict[channel.Name] = None
        session.execute(tableRef.update().where(tableRef.c.clock > maxClock).values(emptyDict))
        rows=[]
        rowsObj=[]
        for t, theTime in enumerate(timeList):
            exprVal = None
            returnVal = None
            toTest = expression
            foundANone = False  # If one value is none this can come from a lot of sources, regardless, if I can't find the value of one channel I can't do anything for the value of the expression of the values. There is a LOT of work into making empty intervals have values so that is not going to be a problem for expresison analysis
            for i, channid in enumerate(ids):
                theChannel = [x for x in channelData if x["channelID"] == channid]  # Should only be one channel
                if getDataArray(channid, t, channelData) is None:
                    foundANone = True
                    break
                if theChannel[0]["channeltype"] == 2:
                    toTest = toTest.replace("ID(" + str(channid) + ")", "'" +
                                            str(getDataArray(channid, t, channelData)) + "'")
                else:
                    toTest = toTest.replace("ID(" + str(channid) + ")", str(getDataArray(channid, t, channelData)))
            row = None
            #print(returnVal)
            if not foundANone:
                returnVal = a(toTest, show_errors=False)
                if "exprVal" in a.symtable:
                    exprVal = a.symtable["exprVal"]
                    a.symtable["exprVal"] = None
                if len(a.error) > 0:
                    exprVal = None
                    returnVal = None
                if isinstance(exprVal, Number):
                    row = {'clock':theTime}
                    row[channel.Name] = returnVal
                elif isinstance(returnVal, Number):
                    row = {'clock':theTime}
                    row[channel.Name] = returnVal
            #print(theTime)
            if row:
                #stmt=session.merge(customClass(row))
                rows.append(row[channel.Name])
                rowsObj.append(row)

            else:
                rows.append(None)
        for each in session.query(customClass).filter(customClass.clock.in_(timeList)).all():
            setattr(each, channel.Name, rows[timeList.index(each.clock)])
            #rows[timeList.index(each.clock)]
            rowsObj[timeList.index(each.clock)]=None
            #print("HERE", each.clock)
        #print(rows)
        session.add_all([customClass(x) for x in rowsObj if x])
        if len(timeList) > 0:
            #print(theTime[0],theTime[-1])
            channTable = daqbrokerDatabase.daqbroker_database.metadata.tables["channels"]
            session.execute(channTable.update().where(channTable.c.channelid == channel.channelid).where(channTable.c.lastclock <= timeList[-1]).values(lastclock = timeList[-1]))
            session.execute(channTable.update().where(channTable.c.channelid == channel.channelid).where(or_(
                channTable.c.firstClock >= timeList[0],channTable.c.firstClock==0)).values(firstClock=timeList[0]))
        session.commit()
    except Exception as e:
        traceback.print_exc()
        session.rollback()


def parseFileLines(lines, header, parseType, metadata, instrument, session, database, logPort, metaid):
    timeStart = time.time()
    theContext = zmq.Context()
    parsedSize = 0
    theTable_data = daqbrokerDatabase.daqbroker_database.metadata.tables[instrument+"_data"]
    (dataClass,customClass) = daqbrokerDatabase.createInstrumentTable(instrument, header,False)
    mapper(dataClass, theTable_data)
    names = [x["name"] for x in header]
    if parseType == 0:
        returned = {}
        returned['linesParsed'] = 0
        returned['parsedSize'] = 0
        returned['notParsedSize'] = 0
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
        linesStore = {}
        dbQueryMiddle = ''
        goodLines = []
        newRows = []
        theTimes = []
        for i, line in enumerate(lines):
            try:
                lineStuff = line.replace('\n', '').split(metadata['parsingInfo']['separator'])
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
                if noFormFound:
                    timeNum = float(' '.join(timeStr)) * 1000  # There should only be one element to this list
                elif milliFound:
                    timeNum = float(' '.join(timeStr))  # There should also be only one element to this list
                else:
                    timeObj = arrow.get(' '.join(timeStr), ' '.join(timeFormat))
                    timeNum = (timeObj.timestamp + timeObj.microsecond / 1e6) * 1000
                lineTime = str(timeNum)
                if not (lineTime in linesStore):
                    linesStore[lineTime] = {}
                if is_number(lineTime):
                    returned['lastTime'] = lineTime
                    if float(lineTime) > linesGreatTime:
                        linesGreatTime = int(float(lineTime))
                    if float(lineTime) < linesLeastTime and float(lineTime) > 0:
                        linesLeastTime = int(float(lineTime))
                headGood = []
                row={'clock' : int(float(lineTime))}
                for k, head in enumerate(header):
                    try:
                        if(k < len(data)):
                            if(int(head["type"]) == 1):
                                theData = data[k].replace('\r', '')
                            else:
                                theData = float(data[k].replace('\r', ''))
                            if(theData == ''):
                                headGood.append(False)
                            else:
                                row[head["name"]] = theData
                                headGood.append(True)
                        else:
                            headGood.append(False)
                    except BaseException:
                        headGood.append(False)
                        traceback.print_exc()
                if len(row.keys()) > 1:
                    newRow = dataClass(row)
                    returned["linesParsed"] = returned["linesParsed"]+1
                    returned["parsedSize"] = returned["parsedSize"] + len(line.encode())
                    newRows.append(row)
                    theTimes.append(row['clock'])
                theLastLine = i
                q = q + 1
                if q * len(header) > 5000 * multiprocessing.cpu_count():
                    if len(newRows) > 0:
                        for row in session.query(dataClass).filter(dataClass.clock.in_(theTimes)):
                            for r, key in enumerate(newRows[theTimes.index(row.clock)]):
                                setattr(row, key, newRows[theTimes.index(row.clock)][key])
                            theTimes[theTimes.index(row.clock)] = 0
                        newLines = [dataClass(newRows[o]) for o, x in enumerate(theTimes) if
                                    x > 0]
                        session.add_all(newLines)
                        newRows = []
                        theTimes = []
                    if linesLeastTime > 1000000000000 and linesGreatTime > 0 and linesLeastTime < 10000000000000000000:  # At least SOMETHING was caught
                        channTable = daqbrokerDatabase.daqbroker_database.metadata.tables["channels"]
                        session.execute(
                            channTable.update().where(daqbrokerDatabase.channels.metaid == metaid).where(
                                daqbrokerDatabase.channels.lastclock < linesGreatTime).values(lastclock=linesGreatTime))
                        session.execute(
                            channTable.update().where(daqbrokerDatabase.channels.metaid == metaid).where(or_(
                                daqbrokerDatabase.channels.firstClock == 0,
                                daqbrokerDatabase.channels.firstClock > linesLeastTime)).values(
                                firstClock=linesLeastTime))
                    session.commit()
                    q = 0
                    dbQueryMiddle = ''
                    headGood = []
                    goodLines = []
            except Exception as e:
                returned["linesNotParsed"] = returned["linesNotParsed"] + 1
                returned["notParsedSize"] = returned["notParsedSize"] + len(line.encode())
                #traceback.print_exc()
                continue
        if q > 0:
            if len(newRows) > 0:
                for row in session.query(dataClass).filter(dataClass.clock.in_(theTimes)):
                    for r, key in enumerate(newRows[theTimes.index(row.clock)]):
                        setattr(row, key, newRows[theTimes.index(row.clock)][key])
                    theTimes[theTimes.index(row.clock)] = 0
                newLines = [dataClass(newRows[o]) for o, x in enumerate(theTimes) if
                            x > 0]
                session.add_all(newLines)
                newRows = []
                theTimes = []
            if linesLeastTime > 1000000000000 and linesGreatTime > 0 and linesLeastTime < 10000000000000000000:  # At least SOMETHING was caught
                channTable = daqbrokerDatabase.daqbroker_database.metadata.tables["channels"]
                session.execute(
                    channTable.update().where(daqbrokerDatabase.channels.metaid == metaid).where(
                        daqbrokerDatabase.channels.lastclock < linesGreatTime).values(lastclock=linesGreatTime))
                session.execute(
                    channTable.update().where(daqbrokerDatabase.channels.metaid == metaid).where(or_(
                        daqbrokerDatabase.channels.firstClock == 0,
                        daqbrokerDatabase.channels.firstClock > linesLeastTime)).values(firstClock=linesLeastTime))
            session.commit()
            q = 0
        returned['lastParsedLine'] = len(lines)
        returned['returnedValue'] = 1
        returned['errors'] = list(set(returned['errors']))
    elif int(parseType) == 1:
        try:
            returned = {}
            returned['linesParsed'] = 0
            returned['parsedSize'] = 0
            returned['notParsedSize'] = 0
            returned['linesNotParsed'] = 0
            returned['values'] = []
            returned['errors'] = []
            returned['lastTime'] = 0
            linesGreatTime = 0
            linesLeastTime = 10000000000000000000
            if metadata['parsingInfo']['timeFormat'].find(
                    'NOFORMAT') == -1:  # Didn't find a noformat string in the time format
                if metadata['parsingInfo']['timeFormat'].find(
                        'MILLISECOND') == -1:  # Didn't find a miliseconds string in the time format
                    timeFormatPos = [m.start() for m in re.finditer('%', metadata['parsingInfo']
                                                                    ['timeFormat'])]  # Array with positions of all %
                else:
                    timeFormatPos = [metadata['parsingInfo']['timeFormat'].find('MILLISECOND')]
            else:  # Found a noformat string in the time format
                timeFormatPos = [metadata['parsingInfo']['timeFormat'].find('NOFORMAT')]
            timeCols = []
            timeColsFormat = []
            prevItem = 0
            prevCol = 0
            for (i, item) in enumerate(timeFormatPos):
                timeCols.append(prevCol + metadata['parsingInfo']['timeFormat'].count('@', prevItem, item))
                prevItem = item
                prevCol = timeCols[i]
            timeColsFormatPre = metadata['parsingInfo']['timeFormat'].split('@')
            timeColsFormat = [x for x in timeColsFormatPre if not x == '']
            timeCols = list(set(timeCols))
            #print(lines)
            linesStore = {}
            for i in range(0, int((len(lines)) / int(metadata['parsingInfo']['colSize']))):
                try:
                    theSlice=''
                    theSlice = lines[i * int(metadata['parsingInfo']['colSize']):(i + 1)
                                     * int(metadata['parsingInfo']['colSize'])]
                    theNewLine = metadata['parsingInfo']['separator'].join(theSlice).replace('\n', '')
                    lineStuff = theNewLine.split(metadata['parsingInfo']['separator'])
                    data = lineStuff
                    #print(theSlice)
                    #print(lineStuff)
                    timeStr = ''
                    for (i, item) in enumerate(timeCols):
                        timeStr = timeStr + lineStuff[timeCols[i]] + '@'
                        timeStr = timeStr.replace('\n', '').replace('\r', '')
                    timeStrFormat = '@'.join(timeColsFormat) + '@'
                    if metadata['parsingInfo']['timeFormat'].find('NOFORMAT') >= 0:
                        lineTime = str(int(float(timeStr[0:(len(timeStr) - 1)]) * 1000))
                    elif metadata['parsingInfo']['timeFormat'].find('MILLISECOND') >= 0:
                        # print(timeStr[0:(len(timeStr)-1)])
                        lineTime = str(int(float(timeStr[0:(len(timeStr) - 1)])))
                    else:
                        timeObj = arrow.get(' '.join(timeStr), ' '.join(timeStrFormat))
                        timeNum = (timeObj.timestamp + timeObj.microsecond / 1e6) * 1000
                        lineTime = str(int(timeNum))
                    #print(lineTime)
                    if is_number(lineTime):
                        returned['lastTime'] = lineTime
                        if float(lineTime) > linesGreatTime:
                            linesGreatTime = float(lineTime)
                            valueToInput = lineStuff[int(metadata['parsingInfo']['headerPosition'])]
                        if float(lineTime) < linesLeastTime and float(lineTime) > 0:
                            linesLeastTime = float(lineTime)
                            valueToInput = lineStuff[int(metadata['parsingInfo']['headerPosition'])]
                    headerStr = lineStuff[int(metadata['parsingInfo']['headerPosition'])]
                    theHeaderValue = [x for x in header if x['alias'] == headerStr]
                    if not str(lineTime) in linesStore:
                        linesStore[str(lineTime)] = {}
                    if(len(theHeaderValue) > 0):
                        #print("FUCK!")
                        if (len(lineStuff) - 1) >= int(metadata['parsingInfo']['headerLines']):
                            theLineValue = lineStuff[int(metadata['parsingInfo']['headerLines'])]
                            linesStore[str(lineTime)][theHeaderValue[0]['name']] = theLineValue
                            #print(metadata['parsingInfo']['headerLines'], theLineValue)
                            returned['linesParsed'] = returned['linesParsed'] + int(metadata['parsingInfo']['colSize'])
                            returned['parsedSize'] = returned['parsedSize'] + sum([len(x.encode()) for x in theSlice])
                            #print(sum([len(x.encode()) for x in theSlice]))
                    if len(list(linesStore.keys())) > 10:
                        #print(linesStore.keys())
                        times = [int(x) for x in linesStore.keys() if len(linesStore[x].keys()) > 0]
                        for row in session.query(dataClass).filter(dataClass.clock.in_(times)):
                            for key in linesStore[str(row.clock)]:
                                setattr(row,key,linesStore[str(row.clock)][key])
                            del times[times.index(row.clock)]
                        newLines = [dataClass(dict(linesStore[str(x)],clock=int(x))) for x in times if len(linesStore[str(x)].keys()) > 0]
                        session.add_all(newLines)
                        linesStore = {}
                        if linesLeastTime > 1000000000000 and linesGreatTime > 0 and linesLeastTime < 10000000000000000000:  # At least SOMETHING was caught
                            channTable = daqbrokerDatabase.daqbroker_database.metadata.tables["channels"]
                            session.execute(
                                channTable.update().where(daqbrokerDatabase.channels.metaid == metaid).where(
                                    daqbrokerDatabase.channels.lastclock < linesGreatTime).values(
                                    lastclock=linesGreatTime))
                            session.execute(
                                channTable.update().where(daqbrokerDatabase.channels.metaid == metaid).where(or_(
                                    daqbrokerDatabase.channels.firstClock == 0,
                                    daqbrokerDatabase.channels.firstClock > linesLeastTime)).values(
                                    firstClock=linesLeastTime))
                        session.commit()
                except Exception as e:
                    session.rollback()
                    traceback.print_exc()
                    returned['linesNotParsed'] = returned['linesNotParsed'] + int(metadata['parsingInfo']['colSize'])
                    returned['notParsedSize'] = returned['notParsedSize'] + sum([len(x.encode()) for x in theSlice])
                    returned['errors'].append(str(e))
                    continue
            if len(list(linesStore.keys())) > 0:
                times = [int(x) for x in linesStore.keys() if len(linesStore[x].keys()) > 0]
                for row in session.query(dataClass).filter(dataClass.clock.in_(times)):
                    for key in linesStore[str(row.clock)]:
                        setattr(row, key, linesStore[str(row.clock)][key])
                    del times[times.index(row.clock)]
                newLines = [dataClass(dict(linesStore[str(x)],clock=int(x))) for x in times if len(linesStore[str(x)].keys()) > 0]
                session.add_all(newLines)
                if linesLeastTime > 1000000000000 and linesGreatTime > 0 and linesLeastTime < 10000000000000000000:  # At least SOMETHING was caught
                    channTable = daqbrokerDatabase.daqbroker_database.metadata.tables["channels"]
                    session.execute(
                        channTable.update().where(daqbrokerDatabase.channels.metaid == metaid).where(
                            daqbrokerDatabase.channels.lastclock < linesGreatTime).values(lastclock=linesGreatTime))
                    session.execute(
                        channTable.update().where(daqbrokerDatabase.channels.metaid == metaid).where(or_(
                            daqbrokerDatabase.channels.firstClock == 0,
                            daqbrokerDatabase.channels.firstClock > linesLeastTime)).values(firstClock=linesLeastTime))
                session.commit()
        except:
            traceback.print_exc()
    return returned

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def require_CSRF_protect(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if request.method == "POST":
            if '_csrf_token' in session:
                token = session["_csrf_token"]
            else:
                token = None
            #token = session.pop('_csrf_token', None)
            if not token == request.form.get('_csrf_token'):
                raise InvalidUsage('Error validating user session', status_code=400)
        return function(*args, **kwargs)
    return decorated_function


def require_admin(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        Session = sessionmaker(bind=current_user.engineObjSettings)
        session = Session()
        our_user = session.query(daqbrokerSettings.users).filter_by(username=current_user.username).first()
        if our_user.type != 1:
            raise InvalidUsage('Administrator privileges required', status_code=401)
        return function(*args, **kwargs)
    return decorated_function


def require_onetime_admin(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        Session = sessionmaker(bind=current_user.engineObjSettings)
        session = Session()
        our_user = session.query(daqbrokerSettings.users).filter_by(username=current_user.username).first()
        if not our_user.type == 1:
            foundServer = False
            for i, server in enumerate(current_app.config['servers']):
                if server["server"] == current_user.server and server["engine"] == current_user.engine and not server["username"] == "NONE" and not server["password"] == "NONE":
                    try:
                        current_user.engineObj = create_engine(
                            current_user.engine +
                            "://" +
                            server["username"] +
                            ":" +
                            server["password"] +
                            "@" +
                            current_user.server +
                            "/daqbro_" +
                            current_user.database)
                        foundServer = True
                    except Exception as e:
                        foundServer = False
                    break
                    raise InvalidUsage('No administrative support found', status_code=401)
            if not foundServer:
                raise InvalidUsage('No administrative support found', status_code=401)
        return function(*args, **kwargs)
    return decorated_function

def getSizeData(number):
    """Auxiliary function used by the :py:func:`getMachineDetails` function to turn a byte number into a human readable
    value in powers of bytes

    :param number: (Double) number of bytes to be turned into human-readable format

    :returns: (Dict) human-readable object with number and type of power of bytes (kB MB, etc...)

    """
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
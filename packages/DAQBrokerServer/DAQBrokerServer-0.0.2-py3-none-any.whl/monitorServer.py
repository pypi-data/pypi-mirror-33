import time
import zmq
import multiprocessing
import threading
import json
import os
import sys
import psutil
import traceback
import pyAesCrypt
import concurrent.futures
import serial
import daqbrokerDatabase
import daqbrokerSettings
import subprocess
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import bindparam
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from supportFuncs import *

if platform.system()=="Windows":
    import winreg
    registry = winreg.HKEY_LOCAL_MACHINE
    address = 'SOFTWARE\\Microsoft\\Cryptography'
    keyargs = winreg.KEY_READ | winreg.KEY_WOW64_64KEY
    key = winreg.OpenKey(registry, address, 0, keyargs)
    value = winreg.QueryValueEx(key, 'MachineGuid')
    winreg.CloseKey(key)
    globalID = value[0]
elif platform.system()=="Linux":
    globalID = check_output(["cat", "/var/lib/dbus/machine-id"]).decode().strip('\n')
else:
    sys.exit("Unsupported DAQBroker version")

class serverData:
    """
    Class containing the relevant monitoring information on a single database engine. This class includes the
    following members

    :ivar server: (string) server address
    :ivar engine: (string) server database engine
    :ivar password: (string) database password
    :ivar username: (string) database username
    :ivar databases: (dict) database information dict object. This object is
    :ivar db: (`sqlalchemy.engine.connection`_) database connection object

    .. _sqlalchemy.engine.connection: http://docs.sqlalchemy.org/en/latest/core/connections.html#sqlalchemy.engine.Connection

    """

    def __init__(
            self,
            server='localhost',
            engine='mysql',
            user='username',
            pword='password'):
        """ CONSTRUCTOR """
        self.engineFct = create_engine(
            engine + '://' + user + ":" + pword + "@" + server)
        self.engineSettings = create_engine(
            engine +
            '://' +
            user +
            ":" +
            pword +
            "@" +
            server +
            "/daqbroker_settings",
            isolation_level="READ_COMMITTED")
        self.SessionSettings = sessionmaker(bind=self.engineSettings)
        self.sessionSettings = self.SessionSettings()
        self.db = self.engineFct.connect()
        self.server = server
        self.engine = engine
        self.password = pword
        self.username = user
        self.databases = {}
        self.refreshDatabases()
        self.refreshGlobals()

    def refreshDatabases(self):
        self.user = self.sessionSettings.query(
            daqbrokerSettings.users).filter_by(
            username=self.username).first()
        dbResult = self.sessionSettings.query(daqbrokerSettings.databases)
        activeDBs = []
        for row in dbResult:
            if row.active:
                dbObject = {}
                activeDBs.append(row.dbname)
                if row.dbname not in self.databases:
                    Session = sessionmaker(
                        bind=create_engine(
                            self.engine +
                            '://' +
                            self.username +
                            ":" +
                            self.password +
                            "@" +
                            self.server +
                            "/daqbro_" +
                            row.dbname,
                            isolation_level="READ_COMMITTED"))
                    session = Session()
                    dbObject = {'session': session}
                    self.databases[row.dbname] = dbObject
                else:  # Should I do something with the already existing objects?
                    pass
        for db in self.databases:
            if db not in activeDBs:
                del self.databases[db]

    def refreshGlobals(self):
        """ Updates the database engine state. Goes through all DAQBroker databases, instruments, data sources and
        channels and gathers the most recent monitoring and data gathering information, updating the **databases**
        attribute"""
        for key in self.databases:
            self.databases[key]
            session = self.databases[key]["session"]
            #if 'instruments' not in self.databases[key]:
            self.databases[key]["instruments"] = []
            #if 'subscribers' not in self.databases[key]:
            self.databases[key]["subscribers"] = []
            for subscriber in session.query(daqbrokerDatabase.subscribers):
                theObjct1 = {}
                for field in subscriber.__dict__:
                    if not field.startswith('_'):
                        theObjct1[field] = getattr(subscriber, field)
                self.databases[key]["subscribers"].append(theObjct1)
            for instrument in session.query(daqbrokerDatabase.instruments).filter_by(active= True):
                theObjct2 = {}
                for field in instrument.__dict__:
                    if not field.startswith('_'):
                        theObjct2[field] = getattr(instrument, field)
                self.databases[key]["instruments"].append(theObjct2)
                self.databases[key]["instruments"][-1]["meta"] = []
                for source in instrument.sources:
                    theObjct3 = {}
                    for field in source.__dict__:
                        if not field.startswith('_'):
                            theObjct3[field] = getattr(source, field)
                    self.databases[key]["instruments"][-1]["meta"].append(
                        theObjct3)
                    self.databases[key]["instruments"][-1]["meta"][-1]["remarks"] = json.loads(
                        self.databases[key]["instruments"][-1]["meta"][-1]["remarks"])
                    self.databases[key]["instruments"][-1]["meta"][-1]["parsing"] = []
                    self.databases[key]["instruments"][-1]["meta"][-1]["channels"] = []
                    for parsing in source.parsing:
                        theObjct4 = {}
                        for field in parsing.__dict__:
                            if not field.startswith('_'):
                                theObjct4[field] = getattr(parsing, field)
                        self.databases[key]["instruments"][-1]["meta"][-1]["parsing"].append(
                            theObjct4)
                        self.databases[key]["instruments"][-1]["meta"][-1]["parsing"][-1]["remarks"] = json.loads(
                            self.databases[key]["instruments"][-1]["meta"][-1]["parsing"][-1]["remarks"])
                    for channel in source.channels:
                        theObjct5 = {}
                        for field in channel.__dict__:
                            if not field.startswith('_'):
                                theObjct5[field] = getattr(channel, field)
                        self.databases[key]["instruments"][-1]["meta"][-1]["channels"].append(
                            theObjct5)
                        self.databases[key]["instruments"][-1]["meta"][-1]["channels"][-1]["remarks"] = json.loads(
                            self.databases[key]["instruments"][-1]["meta"][-1]["channels"][-1]["remarks"])
                    if len(self.databases[key]["instruments"]
                           [-1]["meta"][-1]["parsing"]) < 1:
                        newParsing = daqbrokerDatabase.parsing(
                            clock=time.time() * 1000,
                            type=source.type,
                            locked=False,
                            forcelock=False,
                            remarks=json.dumps(
                                []))
                        source.parsing.append(newParsing)
                    if self.databases[key]["instruments"][-1]["meta"][-1]["type"] == 0 or self.databases[key]["instruments"][-1]["meta"][-1][
                            "type"] == 1 or self.databases[key]["instruments"][-1]["meta"][-1]["type"] == 2:  # Deal with file type metas
                        # Not locked for syncing
                        if not self.databases[key]["instruments"][-1]["meta"][-1]["lockSync"]:
                            if ((time.time() - self.databases[key]["instruments"][-1]["meta"][-1]["lastAction"]) >= int(self.databases[key]["instruments"][
                                    -1]["meta"][-1]["remarks"]["parseInterval"]) / 2) and not self.databases[key]["instruments"][-1]["meta"][-1]["sentRequest"]:
                                self.databases[key]["instruments"][-1]["meta"][-1]["sendSync"] = True
                            elif ((time.time() - self.databases[key]["instruments"][-1]["meta"][-1]["lastAction"]) >= 3 * int(self.databases[key]["instruments"][-1]["meta"][-1]["remarks"]["parseInterval"])) and self.databases[key]["instruments"][-1]["meta"][-1]["sentRequest"]:
                                source.sentRequest = False
                            else:
                                self.databases[key]["instruments"][-1]["meta"][-1]["sendSync"] = False
                            if "sendSync" not in self.databases[key]["instruments"][-1]["meta"][-1]:
                                self.databases[key]["instruments"][-1]["meta"][-1]["sendSync"] = False
                        else:
                            self.databases[key]["instruments"][-1]["meta"][-1]["sendSync"] = False
                        # Looking for parsing now
                        if self.databases[key]["instruments"][-1]["meta"][-1]["parsing"]:
                            if not self.databases[key]["instruments"][-1]["meta"][-1]["parsing"][-1]["forcelock"]:
                                #print((time.time() - self.databases[key]["instruments"][-1]["meta"][-1]["lastAction"]))
                                if ((time.time() - self.databases[key]["instruments"][-1]["meta"][-1]["lastAction"]) >= int(self.databases[key]["instruments"][-1][
                                        "meta"][-1]["remarks"]["parseInterval"]) / 2) and not self.databases[key]["instruments"][-1]["meta"][-1]["parsing"][-1]["locked"]:
                                    self.databases[key]["instruments"][-1]["meta"][-1]["toParse"] = True
                                else:
                                    self.databases[key]["instruments"][-1]["meta"][-1]["toParse"] = False
                            else:
                                self.databases[key]["instruments"][-1]["meta"][-1]["toParse"] = False
            session.commit()


def producer(servers, sendBack, logPort, isRemote, backupInfo, workerList, localPath):
    """Main monitoring process loop. This loop is responsible for persistently checking the available DAQBroker servers
    and creating a new server monitoring process (see :py:mod:`monitorServer.singleMonitor`) in case a new server is
    provided by a user.

    :param servers: (`multiporcessing.Manager().list`_) Contains a process-shared list of database servers under
    monitoring by DAQBroker
    :param sendBack: (Integer) network communications port. This value is sent to all remote DAQBroker clients to allow
    responses to be sent to the appropriate port
    :param logPort: (Integer) local event logging port
    :param isRemote: (Boolean) decides whether messages are sent to remote clients
    :param backupInfo: (`multiporcessing.Manager().list`_) process-shared dict with relevant backup information

    .. _multiporcessing.Manager().list: https://docs.python.org/2/library/multiprocessing.html#sharing-state-between-processes

    .. warning::

            This is a long running process and blocks execution of the main task, it should therefore be called on a
            separate process.

    """
    manager = multiprocessing.Manager()
    nodes = manager.list()
    nodes.append({'remote': '127.0.0.1',
                  'remotePort': 6666,
                  'local': "127.0.0.1",
                  'name': 'localhost',
                  'node': globalID})
    # nodes=[]
    paths = manager.dict()
    bufferSize = 64 * 1024
    password = "daqbroker"
    children = []
    context = zmq.Context()
    theLogSocket = context.socket(zmq.REQ)
    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
    toSend = {'req': 'LOG', 'type': 'INFO', 'process': 'COLLECTOR',
              'message': "started producer process", 'method': 'collector'}
    theLogSocket.send(json.dumps(toSend).encode())
    theLogSocket.close()
    timeStart = -30
    BACKUPPATH = ''
    IMPORTPATH = ''
    ADDONPATH = ''
    daqbrokerSettings.setupLocalVars(localPath)
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    while True:
        try:
            if time.time() - timeStart > 10:
                scoped = daqbrokerSettings.getScoped()
                session = scoped()
                for badJob in session.query(daqbrokerSettings.jobs).filter(daqbrokerSettings.jobs.clock < (time.time()-60)*1000).all():
                    workerList[int(badJob.data)] = -1
                    session.delete(badJob)
                session.commit()
                globalsObj = session.query(
                    daqbrokerSettings.Global).filter_by(
                    clock=session.query(
                        func.max(
                            daqbrokerSettings.Global.clock))).first()
                if globalsObj:
                    globals = {}
                    for field in globalsObj.__dict__:
                        if not field.startswith('_'):
                            globals[field] = getattr(globalsObj, field)
                    if 'remarks' in globals:
                        globals["remarks"] = json.loads(globals["remarks"])
                else:
                    globals = {
                        'clock': time.time(),
                        'version': '0.1',
                        'backupfolder': 'backups',
                        'importfolder': 'uploads',
                        'tempfolder': 'temp',
                        'ntp': None,
                        'commport': 9090,
                        'logport': 9092,
                        'remarks': {}}
                base_dir = '.'
                if getattr(sys, 'frozen', False):
                    base_dir = os.path.join(sys._MEIPASS)
                tempDir = os.path.join(base_dir, globals['tempfolder'])
                if not os.path.isdir(tempDir):
                    os.mkdir(tempDir)
                else:
                    for file in os.listdir(tempDir):
                        if os.path.isfile(os.path.join(tempDir, file)) and os.path.getmtime(os.path.join(tempDir, file)) <= time.time()-300:
                            os.remove(os.path.join(tempDir, file))
                timeStart = time.time()
                # Ensure the local folders are okay
                # Checking for altered backup, import and/or addon path
                newPaths = checkPaths(
                    context, BACKUPPATH, IMPORTPATH, ADDONPATH, logPort)
                BACKUPPATH = newPaths[0]
                IMPORTPATH = newPaths[1]
                ADDONPATH = newPaths[2]
                paths["BACKUPPATH"] = BACKUPPATH
                paths["IMPORTPATH"] = IMPORTPATH
                paths["ADDONPATH"] = ADDONPATH
                # Checking time - NTP, etc...
                checkTime(context, logPort)
                # Check nodes - only returns nodes that have good connections
                p = threading.Thread(
                    target=checkAddresses, args=(nodes, ))
                p.start()
                # Emptying shared array of available nodes
                # Check servers info and store in encrypted file and start/stop
                # monitoring of all possible databases
                children = checkServers(
                    servers,
                    children,
                    sendBack,
                    logPort,
                    isRemote,
                    nodes,
                    paths,
                    backupInfo)
                parent_pid = os.getpid()
                parent = psutil.Process(parent_pid)
                processes = []
                for child in parent.children():
                    processes.append(child)
                auxProcesses = processes
                for i, process in enumerate(auxProcesses):
                    try:
                        proc = psutil.Process(process["process"].pid)
                        if proc.status() == psutil.STATUS_ZOMBIE:
                            process["process"].terminate()
                            del processes[i]
                    except BaseException:
                        del processes[i]
                        continue
            session.commit()
            theLogSocket = context.socket(zmq.REQ)
            theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
            toSend = {
                'req': 'KEEPALIVE',
                'type': 'KEEPALIVE',
                'process': 'PRODUCER',
                'message': 'NOTHING',
                'filename': "NOTHING",
                'lineno': "NOTHING",
                'funname': "NOTHING",
                'line': "NOTHING"}
            theLogSocket.send(json.dumps(toSend).encode())
            theLogSocket.close()
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
                'process': 'PRODUCER',
                'message': str(e),
                'filename': filename,
                'lineno': lineno,
                'funname': funname,
                'line': line}
            theLogSocket.send(json.dumps(toSend).encode())
            theLogSocket.close()


def checkServers(
        servers,
        children,
        sendBack,
        logPort,
        isRemote,
        nodes,
        paths,
        backupInfo):
    """Function periodically called by :py:func:`producer`. This function checks the **servers** variable and the
    existing instances of :py:func:`singleMonitor` functions for a server unassigned to a monitor and if so starts a
    new instance of :py:func:`singleMonitor` for said server. This function keeps all database servers supplied to
    DAQBroker updated

    :param servers: (`multiporcessing.Manager().list`_) Contains a process-shared list of database servers under
    monitoring by DAQBroker
    :param children: (List) list of objects defining the existing :py:func:`singleMonitor` processes associated with
    each database server.
    :param sendBack: (Integer) network communications port. This value is sent to all remote DAQBroker clients to allow
    responses to be sent to the appropriate port
    :param logPort: (Integer) local event logging port
    :param isRemote: (Boolean) decides whether messages are sent to remote clients
    :param nodes: (`multiporcessing.Manager().list`_) Contains a process-shared list of existing and active DAQBroker
    client applications connected to the server.
    :param paths: (dict) contains the available DAQBroker paths as stored by the users on the local settings file

    .. _multiporcessing.Manager().list: https://docs.python.org/2/library/multiprocessing.html#sharing-state-between-processes

    """
    base_dir = '.'
    if getattr(sys, 'frozen', False):
        base_dir = os.path.join(sys._MEIPASS)
    if len(servers) > 0:
        try:
            password = str(
                snowflake.make_snowflake(
                    snowflake_file=os.path.join(base_dir, 'snowflake')))
            bufferSize = 64 * 1024
            file = open(os.path.join(base_dir, "secretPlain"), "w")
            file.write('[')
            theString = ''
            for server in servers:
                theString = theString + json.dumps(server) + ','
            file.write(theString.strip(','))
            file.write(']')
            file.close()
            time.sleep(1)
            pyAesCrypt.encryptFile(
                os.path.join(base_dir, "secretPlain"), os.path.join(base_dir, "secretEnc"), password, bufferSize)
            os.remove(os.path.join(base_dir, "secretPlain"))
        except BaseException:
            poop = "poop"
    for server in servers:
        foundProcess = False
        for i, child in enumerate(children):
            if child["server"] == server["server"] and child["engine"] == server["engine"]:
                foundProcess = True
                if server["monActive"]:
                    process = None
                    if psutil.pid_exists(child['pid']):
                        try:
                            process = psutil.Process(child['pid'])
                        except BaseException:
                            process = None
                    if not process:
                        p = multiprocessing.Process(
                            target=singleMonitor,
                            args=(
                                server["server"],
                                server["engine"],
                                server["username"],
                                server["password"],
                                sendBack,
                                logPort,
                                isRemote,
                                nodes,
                                paths,
                                backupInfo))
                        p.start()
                        children[i]["pid"] = p.pid
                    if time.time() - children[i]["timeStart"] > 3600:
                        try:
                            process = psutil.Process(child['pid'])
                            childs = process.children()
                            for p in childs:
                                p.terminate()  # maybe kill?
                            process.kill()
                            p = multiprocessing.Process(
                                target=singleMonitor,
                                args=(
                                    server["server"],
                                    server["engine"],
                                    server["username"],
                                    server["password"],
                                    sendBack,
                                    logPort,
                                    isRemote,
                                    nodes,
                                    paths,
                                    backupInfo))
                            p.start()
                            children[i]["pid"] = p.pid
                            children[i]["timeStart"] = time.time()
                        except BaseException:
                            traceback.print_exc()
                else:
                    process = None
                    if psutil.pid_exists(child['pid']):
                        try:
                            process = psutil.Process(child['pid'])
                        except BaseException:
                            process = None
                    if process:
                        childs = process.children()
                        for p in childs:
                            p.terminate()  # maybe kill?
                        process.kill()
                        del children[i]
                break
        if not foundProcess:
            if server["monActive"]:
                p = multiprocessing.Process(
                    target=singleMonitor,
                    args=(
                        server["server"],
                        server["engine"],
                        server["username"],
                        server["password"],
                        sendBack,
                        logPort,
                        isRemote,
                        nodes,
                        paths,
                        backupInfo))
                p.start()
                children.append({"timeStart": time.time(),
                                 "pid": p.pid,
                                 "server": server["server"],
                                 "engine": server["engine"]})
    return children


def singleMonitor(
        server,
        engine,
        username,
        password,
        sendBack,
        logPort,
        isRemote,
        nodes,
        paths,
        backupInfo):
    """Single database engine monitoring function. This function is responsible for continuously updating the status of
     a database engine and triggering the automated DAQBroker monitoring mechanisms. It periodically runs several
     housekeeping tasks on the global database settings but most importantly it constantly retrieves instrument data
     from an internal :py:class:`serverData` object and decides appropriately what action must be taken for each
     instrument in each database.

    :param server: (String) database server address
    :param engine: (String) database server engine
    :param username: (String) database server username
    :param password: (String) database server password
    :param sendBack: (Integer) network communications port. This value is sent to all remote DAQBroker clients to allow
     responses to be sent to the appropriate port
    :param logPort: (Integer) local event logging port
    :param isRemote: (Boolean) decides whether messages are sent to remote clients
    :param nodes: (`multiporcessing.Manager().list`_) Contains a process-shared list of existing and active DAQBroker
    client applications connected to the server.
    :param paths: (dict) contains the available DAQBroker paths as stored by the users on the local settings file

    .. _multiporcessing.Manager().list: https://docs.python.org/2/library/multiprocessing.html#sharing-state-between-processes

    .. warning::

            This is a long running process and blocks execution of the main task, it should therefore be called on a
            separate process.

    """
    daqbroObject = serverData(
        server=server,
        engine=engine,
        user=username,
        pword=password)
    context = zmq.Context()
    theLogSocket = context.socket(zmq.REQ)
    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
    toSend = {
        'req': 'LOG',
        'type': 'INFO',
        'process': 'COLLECTOR',
        'message': "started producer for server '" + server + "' running on '" + engine + "'",
        'method': 'collector'}
    theLogSocket.send(json.dumps(toSend).encode())
    theLogSocket.close()
    timeStart = -30
    deleteJobs = True
    manager = multiprocessing.Manager()
    workerpool = concurrent.futures.ThreadPoolExecutor(
        max_workers=multiprocessing.cpu_count() * 2)  # Using threads
    for i, db in enumerate(daqbroObject.databases):
        daqbroObject.databases[db]["session"].execute(
            daqbrokerDatabase.daqbroker_database.metadata.tables["parsing"].update().where(
                daqbrokerDatabase.parsing.locked).values(
                locked=False))
        daqbroObject.databases[db]["session"].commit()
    while True:
        try:
            if time.time() - timeStart > 10:
                #print(nodes)
                daqbroObject.refreshDatabases()
                deleteJobs = True
                timeStart = time.time()
                daqbroObject.sessionSettings.execute(
                    daqbrokerSettings.daqbroker_settings.metadata.tables["links"].delete().where(
                        daqbrokerSettings.links.clock < (
                            time.time() - 3600 * 24 * 7) * 1000))
            daqbroObject.refreshGlobals()
            nodeMsgs = {}
            for node in nodes:
                nodeMsgs[node["node"]] = {"order": "SYNC", 'directives': []}
            # #Check for instruments that need to have their data gathered
            #print(daqbroObject.databases)
            for i, db in enumerate(daqbroObject.databases):
                for j, instrument in enumerate(
                        daqbroObject.databases[db]["instruments"]):
                    for k, meta in enumerate(instrument["meta"]):
                        #print(meta["sendSync"])
                        #print(meta["node"])
                        #print(meta["type"])
                        #print(nodeMsgs)
                        if (meta["sendSync"] and meta["node"] in nodeMsgs):
                            meta[syncInst] = False
                            #daqbroObject.databases[i]["instruments"][j]["meta"][k]["syncInst"] = False
                            if meta["type"] == 1 or meta["type"] == 2:
                                nodeMsgs[meta["node"]]["directives"].append({'metaName': meta["name"],
                                                                             'sendBackPort': sendBack,
                                                                             'instrument': instrument["Name"],
                                                                             'metaid': meta["metaid"],
                                                                             'type': meta["type"],
                                                                             'database': db,
                                                                             "serverDB": server,
                                                                             "engine": engine,
                                                                             "remarks": meta["remarks"],
                                                                             'backupPort': backupInfo["port"],
                                                                             'backupUser': backupInfo["user"],
                                                                             'backupPass': backupInfo["pass"],
                                                                             'channels': meta["channels"]})
                            else:
                                nodeMsgs[meta["node"]]["directives"].append({'metaName': meta["name"],
                                                                             'sendBackPort': sendBack,
                                                                             'instrument': instrument["Name"],
                                                                             'metaid': meta["metaid"],
                                                                             'type': meta["type"],
                                                                             'database': db,
                                                                             "serverDB": server,
                                                                             "engine": engine,
                                                                             "remarks": meta["remarks"],
                                                                             'backupPort': backupInfo["port"],
                                                                             'backupUser': backupInfo["user"],
                                                                             'backupPass': backupInfo["pass"],
                                                                             'channels': []})
                            backingUp(
                                daqbroObject,
                                meta["metaid"],
                                db,
                                instrument["Name"],
                                paths,
                                server)
            if deleteJobs:
                deleteJobs = False
            # #Check for data gathering routines that need to be sent
            for msg in nodeMsgs:
                if len(nodeMsgs[msg]["directives"]) > 0:
                    for node in nodes:
                        if node["node"] == globalID:
                            if node["node"] == msg:
                                for directive in nodeMsgs[msg]["directives"]:
                                    if directive["type"] == 1 or directive["type"] == 2:
                                        workerpool.submit(
                                            getPeripheralData,
                                            directive["database"],
                                            directive["instrument"],
                                            directive["remarks"],
                                            directive["type"],
                                            directive["backupPort"],
                                            directive["backupUser"],
                                            directive["backupPass"],
                                            directive["metaName"],
                                            directive["metaid"],
                                            directive["sendBackPort"],
                                            directive["serverDB"],
                                            directive["engine"],
                                            directive["channels"])
                                    elif directive["type"] == 0:
                                        #print("HERERERERERERERERE")
                                        obj = workerpool.submit(
                                            syncInst,
                                            directive["sendBackPort"],
                                            directive["remarks"],
                                            directive["instrument"],
                                            directive["metaid"],
                                            directive["database"],
                                            logPort,
                                            directive["backupPort"],
                                            directive["backupUser"],
                                            directive["backupPass"],
                                            directive["serverDB"],
                                            directive["engine"],
                                            directive["metaName"])
                                        #print("WHATISGOINGONHERE?!")
                                break
                        else:
                            if node["name"] == msg:
                                for message in nodeMsgs[msg]["directives"]:
                                    message["server"] = node["local"]
                                machine = "tcp://" + \
                                    node['remote'] + ":" + str(node['remotePort'])
                                break
                    if not msg == globalID:
                        zmq_socket = context.socket(zmq.PUSH)
                        zmq_socket.setsockopt(zmq.LINGER, 1000)
                        zmq_socket.connect(machine)
                        zmq_socket.send_json(nodeMsgs[msg])
                        zmq_socket.close()
                        # print("SENT")
            # #Check for any instrument that needs parsing, should be the same as each instrument that needs backing up
            for i, db in enumerate(daqbroObject.databases):
                for j, instrument in enumerate(
                        daqbroObject.databases[db]["instruments"]):
                    foundCustoms = False
                    dbQuery = "DELETE FROM `" + \
                        instrument["Name"] + "_custom` WHERE "
                    for k, meta in enumerate(instrument["meta"]):
                        for channel in meta["channels"]:
                            if channel["channeltype"] == 2:
                                foundCustoms = True
                                dbQuery = dbQuery + "`" + \
                                    channel["Name"] + "` IS NULL AND"
                    if foundCustoms:
                        daqbroObject.databases[db]["session"].execute(
                            text(dbQuery.rstrip("AND")))
                daqbroObject.databases[db]["session"].commit()
        except Exception as e:
            traceback.print_exc()
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
                'process': 'DBMONITOR',
                'message': str(e),
                'filename': filename,
                'lineno': lineno,
                'funname': funname,
                'line': line}
            theLogSocket.send(json.dumps(toSend).encode())
            theLogSocket.close()
        finally:
            processes = []
            parent_pid = os.getpid()
            parent = psutil.Process(parent_pid)
            for child in parent.children():
                processes.append(child)
            auxProcesses = processes
            for i, process in enumerate(auxProcesses):
                try:
                    proc = psutil.Process(process["process"].pid)
                    if proc.status() == psutil.STATUS_ZOMBIE:
                        process["process"].terminate()
                        del processes[i]
                except BaseException:
                    del processes[i]
                    continue
        time.sleep(0.3)


def checkAddresses(nodes):
    """Function periodically called by :py:func:`producer`. This function checks the **nodes** variable and the locally
    stored entries of network DAQBroker client applications. It updates the process-shared variable with new nodes to
    make sure newly added nodes can be seamlessly used for instrument monitoring

    :param nodes: (`multiporcessing.Manager().list`_) Contains a process-shared list of existing and active DAQBroker
    client applications connected to the server.

    .. _multiporcessing.Manager().list: https://docs.python.org/2/library/multiprocessing.html#sharing-state-between-processes

    """
    try:
        scoped = daqbrokerSettings.getScoped()
        session = scoped()
        processes = []
        manager = multiprocessing.Manager()
        return_dict = manager.list()
        ntp = 'NONE'
        goodReturned = []
        smallestClock = time.time() - 24 * 60 * 60 * 7
        maxGlobal = session.query(
            daqbrokerSettings.Global).filter_by(
            clock=session.query(
                func.max(
                    daqbrokerSettings.Global.clock))).first()
        if maxGlobal:
            ntp = maxGlobal.ntp
        if ntp is None:
            ntp = {}
        allNodes = sendNodeQuery("0.1", ntp)
        details = getMachineDetails(ntp)
        localNode = session.query(
            daqbrokerSettings.nodes).filter_by(
            node=globalID).first()
        localNode.address = '127.0.0.1'
        localNode.lastActive = time.time()
        localNode.remarks = json.dumps(details)
        for i, row in enumerate(allNodes):
            node = session.query(
                daqbrokerSettings.nodes).filter_by(
                node=row["id"]).first()
            if node:
                node.address = row["address"]
                node.lastActive = time.time()
                node.remarks = json.dumps(row["details"])
            # else:
            #     newNode = daqbrokerSettings.nodes(
            #         node=row["id"],
            #         name=row["node"],
            #         address=row["address"],
            #         port=row["port"],
            #         local=row["serverAddr"],
            #         active=True,
            #         lastActive=time.time(),
            #         tsyncauto=False,
            #         remarks=row["details"]
            #     )
            #     session.add(newNode)
        for row in session.query(daqbrokerSettings.nodes).filter(
                daqbrokerSettings.nodes.lastActive >= smallestClock):
            foundNode = False
            for node in allNodes:
                if node["id"] == row.node:
                    foundNode = True
                    if i < len(nodes):
                        nodes[i] = {
                            'remote': row.address,
                            'remotePort': row.port,
                            'local': node["serverAddr"],
                            'name': node["node"],
                            'node': node["id"]}
                    else:
                        nodes.append({'remote': row.address,
                                      'remotePort': row.port,
                                      'local': node["serverAddr"],
                                      'name': node["node"],
                                      'node': node["id"]})
            if not foundNode and row.node != globalID:  # There's still 1hr until this node is essentially forgotten
                nodes.append({'remote': row.address,
                              'remotePort': row.port,
                              'local': row.local,
                              'name': row.name,
                              'node': row.node})
        session.commit()
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        poop = "poop"
        # return nodes


def checkTime(context, logPort):
    """Auxiliary function that updates the current machine time with an NTP server (if applicable) and updates the local
     settings file with the most recent local machine information

    :param context: (`zmq.context`_) context object to create network communications. Only used in this case for local
    communication with the event logging server
    :param logPort: (Integer) local event logging port

    .. _zmq.context: https://pyzmq.readthedocs.io/en/latest/api/zmq.html#zmq.Context

    """
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    globals = None
    maxGlobal = session.query(
        daqbrokerSettings.Global).filter_by(
        clock=session.query(
            func.max(
                daqbrokerSettings.Global.clock))).first()
    if maxGlobal:
        # theLogSocket = context.socket(zmq.REQ)
        # theLogSocket.connect("tcp://127.0.0.1:"+ str(logPort))
        # toSend={'req':'LOG','type':'INFO','process':'PRODUCER','message':'Checking nodes','method':'producer'}
        # theLogSocket.send(json.dumps(toSend).encode())
        # theLogSocket.close()
        theNTP = maxGlobal.ntp
        if ((not theNTP == '') and (not theNTP == 'NONE')):
            resultsMachine = getMachineDetails({'serverNTP': theNTP})
            if resultsMachine["timeInfo"]['serverDifference'] == 'N/A':
                theLogSocket = context.socket(zmq.REQ)
                theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
                toSend = {
                    'req': 'LOG',
                    'type': 'WARNING',
                    'process': 'PRODUCER',
                    'message': 'Could not synchronize computer time',
                    'method': 'producer'}
                theLogSocket.send(json.dumps(toSend).encode())
                theLogSocket.close()
        else:
            resultsMachine = getMachineDetails({})
        try:
            #maxGlobal = session.query(daqbrokerSettings.Global).filter_by(clock = session.query(func.max(daqbrokerSettings.Global.clock))).first()
            maxGlobal.clock = time.time()
            maxGlobal.remarks = json.dumps(resultsMachine)
            #localConn.execute("UPDATE global SET clock=?, remarks=? WHERE clock=(SELECT max(clock) as maxclock from global)",(time.time(),json.dumps(resultsMachine)))
            session.commit()
        except Exception as e:
            session.rollback()
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
                'process': 'PRODUCER',
                'message': str(e),
                'filename': filename,
                'lineno': lineno,
                'funname': funname,
                'line': line}
            theLogSocket.send(json.dumps(toSend).encode())
            theLogSocket.close()


def backingUp(serverObject, metaid, database, instrument, paths, server):
    """Auxiliary function used by the :py:func:`singleMonitor` function to update the database state when a remote
    instrument's data is being requested

    :param serverObject: (:py:class:`serverData`) Object containing the current database state
    :param metaid: (Integer) unique data source identifier
    :param database: (String) database name
    :param instrument: (String) instrument name
    :param paths: (Dict) contains local storage paths
    :param server: (String) database engine server name

    """
    base_dir = '.'
    if getattr(sys, 'frozen', False):
        base_dir = os.path.join(sys._MEIPASS)
    if not os.path.isdir(
        os.path.join(base_dir,
            paths["BACKUPPATH"],
            server,
            database,
            instrument)):
        os.makedirs(
            os.path.join(
                base_dir,
                paths["BACKUPPATH"],
                server,
                database,
                instrument))
    serverObject.databases[database]["session"].execute(
        daqbrokerDatabase.daqbroker_database.metadata.tables["instmeta"].update().where(
            daqbrokerDatabase.instmeta.metaid == metaid).values(
            lastAction=time.time()))


def getPeripheralData(
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
        channels):
    """Auxiliary function used by the :py:func:`singleMonitor` function to collect data from a local peripheral
    instrument (COM port or network port)

    :param database: (String) database name
    :param instrument: (String) instrument name
    :param meta: (Dict) contains the relevant information for the data source
    :param type: (Integer) type of peripheral to obtain data from
    :param backupPort: (Integer) a stored data backup network server port
    :param backupUser: (String) a stored data backup server username
    :param backupPass: (String) a stored data backup server password
    :param metaName: (String) data source name
    :param metaid: (Integer) unique data source identifier
    :param sendBackPort: (Integer) network communications port
    :param serverDB: (String) database engine server address
    :param engineDB: (String) database engine
    :param channels: (List) list of data channel objects

    """
    try:
        server = 'localhost'
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
        theFile = open(os.path.join('temp', server, instrument, metaName +
                                    '_' +
                                    str(datetime.datetime.now().day) +
                                    '_' +
                                    str(datetime.datetime.now().hour) +
                                    '.tmp'), 'a')
        if type == 1:
            returned = getPortData(int(meta["port"]), int(
                meta["parseInterval"]), meta["command"], -1, [], True)
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
                    meta["dataBits"]), meta["stopBits"], -1, [], True)
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
        syncDirectory(
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
        if consumer_sender:
            endMessage = {
                "server": serverDB,
                "engine": engineDB,
                "database": database,
                "instrument": instrument,
                "metaid": metaid,
                "order": "METASYNCOVER",
                "errors": errors}
            consumer_sender.send_json(endMessage)
            consumer_sender.close()


def getNTPTIme(server, timeback):
    """Auxiliary function used by the :py:func:`getPortData` function to collect time information from an NTP port

    :param server: Dict with NTP server information
    :param timeback: (`multiprocessing.Value`_) process-shared double, this value is set with the NTP time

    .. _multiprocessing.Value: https://docs.python.org/2/library/multiprocessing.html#sharing-state-between-processes
    """
    try:
        c = ntplib.NTPClient()
        timeback.value = c.request(server).tx_time
    except BaseException:
        timeback.value = 0


def getLocalTime(timeback):
    """Auxiliary function used by the :py:func:`getPortData` function to collect time information from an NTP port

    :param timeback: (`multiprocessing.Value`_) process-shared double, this value is set with the local time
    """
    timeback.value = time.time()


def getMachineDetails(extra):
    """Auxiliary function used by the :py:func:`checkTime` and :py:func:`checkAddresses` functions to collect local
    machine information and synchronize machine time (if applicable)

    :param extra: (Dict) NTP server information

    :returns: (Dict) containing the local machine information with CPU, ROM and RAM information

    """

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
                    _win_set_time(timeDiff)
                elif(platform.system() == 'Linux'):  # Running on linux machine
                    _linux_set_time(timeDiff)
                theTimeLocal = time.time()
                time2 = time.time()
                timeDiff = time2 - theTimeLocal
                theTimeDifference = timeDiff
            except Exception as e:
                #print(datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+ "[CONSUMER] ERROR - "+str(e))
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
            continue
    result["cpu"] = psutil.cpu_percent(interval=0.5)
    result["cpuMulti"] = psutil.cpu_percent(percpu=True)
    result["timeInfo"] = {
        'localTime': theTimeLocal,
        'serverDifference': theTimeDifference}
    return result


def _win_set_time(timeOffset):
    """Auxiliary function used by the :py:func:`getMachineDetails` function update the time in a Windows machine

    :param timeOffset: (Double) time offset to update

    :returns: ``False`` if unsuccessful. ``True`` if successful

    """
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
    """Auxiliary function used by the :py:func:`getMachineDetails` function update the time in a Linux machine
    (probably only in debian)

    :param timeOffset: (Double) time offset to update

    :returns: ``False`` if unsuccessful. ``True`` if successful
    """
    try:
        timestamp = time.time() + timeOffset
        toRun = 'date +%s -s @' + str(int(timestamp) + ' >/dev/null')
        a = subprocess.call(toRun.split(' '), stderr=None)
        return a
    except BaseException:
        # traceback.print_exc()
        return False

# Gets all the metadata from an instrument, sorts only the most recent and
# from different example files and parses that data
def syncInst(
        sendBackPort,
        instMeta,
        instrument,
        metaid,
        database,
        logPort,
        backupPort,
        backupUser,
        backupPass,
        serverDB,
        engineDB,
        metaName):
    """Auxiliary function used by the :py:func:`singleMonitor` function to collect data from a local file-based instrument

    :param sendBackPort: (Integer) local communications port
    :param instMeta: (Dict) information on the data source
    :param instrument: (String) instrument name
    :param metaid: (Integer) unique data source identifier
    :param database: (String) database name
    :param logPort: (Integer) local event logging port
    :param backupPort: (Integer) a stored data backup network server port
    :param backupUser: (String) a stored data backup server username
    :param backupPass: (String) a stored data backup server password
    :param serverDB: (String) database engine server address
    :param engineDB: (String) database engine
    :param metaName: (String) data source name

    """
    servAddr = "localhost"
    #print("FUCK IF THISIS THE PRTOBLEM")
    try:
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
        syncDirectory(
            servAddr,
            database,
            instrument,
            instMeta,
            backupPort,
            backupUser,
            backupPass,
            metaName)
    except Exception as e:
        #traceback.print_exc()
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
        if consumer_sender:
            endMessage = {
                "server": serverDB,
                "engine": engineDB,
                "database": database,
                "instrument": instrument,
                "metaid": metaid,
                "order": "METASYNCOVER",
                "errors": errors}
            consumer_sender.send_json(endMessage)
            consumer_sender.close()


def syncDirectory(
        server,
        database,
        instrument,
        meta,
        backupPort,
        backupUser,
        backupPass,
        metaName):
    scriptPath = os.getcwd()
    if(platform.system() == 'Windows'):  # Running on windows machine
        command1 = os.path.join(scriptPath, 'static', 'rsync', 'cygpath')
        command1 = command1 + ' ' + meta["path"]
        CREATE_NO_WINDOW = 0x08000000
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        winPath = subprocess.check_output(
            command1,
            universal_newlines=True,
            creationflags=CREATE_NO_WINDOW,
            startupinfo=si).replace(
            '\n',
            '')
        command = os.path.join(scriptPath, 'static', 'rsync', 'rsync') + \
            ' -a --no-p --append-verify --chmod=ugo=rwX --bwlimit=500'
        os.environ['RSYNC_PASSWORD'] = backupPass
        if 'getNested' in meta:
            if meta['getNested'] == "1" or meta['getNested'] == "true" or meta['getNested']:
                comamand = command + ' --include="*/" '
        command = command + ' --include="*' + meta["pattern"] + '*.' + meta["extension"] + '" --exclude="*" --port=' + str(
            backupPort) + ' ' + winPath + '/ ' + backupUser + '@' + server + '::daqbroker/' + server + '/' + database + '/' + instrument + '/' + metaName
        #print(command)
        with open(os.devnull, 'w') as devnull:
            output = subprocess.call(
                command + '>out',
                env=os.environ,
                shell=True,
                creationflags=CREATE_NO_WINDOW,
                startupinfo=si,
                stderr=devnull)
    else:
        command = 'rsync -a --no-p --chmod=ugo=rwX --append-verify --bwlimit=500'
        if 'getNested' in meta:
            if meta['getNested'] == "1" or meta['getNested'] == "true" or meta['getNested']:
                comamand = command + ' --include="*/" '
        command = command + ' --include="*' + meta["pattern"] + '*.' + meta["extension"] + '" --exclude="*" --port=' + str(
            backupPort) + ' ' + meta["path"] + '/ ' + backupUser + '@' + server + '::daqbroker/' + server + '/' + database + '/' + instrument + '/' + metaName
        with open(os.devnull, 'w') as devnull:
            output = subprocess.check_output(
                command.split(' '), env={
                    'RSYNC_PASSWORD': backupPass}, stderr=devnull)

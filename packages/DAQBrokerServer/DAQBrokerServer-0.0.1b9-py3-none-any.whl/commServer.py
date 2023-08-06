import time
import zmq
import multiprocessing
import json
import traceback
import sys
import concurrent.futures
import daqbrokerDatabase
import daqbrokerSettings
from sqlalchemy import text
from sqlalchemy import bindparam
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker, scoped_session
from supportFuncs import *


def collector(servers, port, logPort, backupInfo, localPath):
    """ Communications server main process loop. This process is responsible for listening for inbound DAQBroker client communications and handling the sent requests. Each client request will have a specific node identifier associated with it as well as an order to be fulfilled.

    :param servers: (`multiporcessing.Manager().list`_) process-shared list of database servers under monitoring by DAQBroker. They are used here to update the state of instruments in the databases
    :param port: (Integer) Port for network communications
    :param logPort: (Integer) The local event logging port. See :py:mod:`logServer` for more information
    :param backupInfo: (`multiporcessing.Manager().list`_) process-shared dict with relevant backup information

    .. _multiporcessing.Manager().list: https://docs.python.org/2/library/multiprocessing.html#sharing-state-between-processes

    .. warning::

            This is a long running process and blocks execution of the main task, it should therefore be called on a separate process.

    """
    manager = multiprocessing.Manager()
    context = zmq.Context()
    theLogSocket = context.socket(zmq.REQ)
    theLogSocket.connect("tcp://127.0.0.1:" + str(logPort))
    toSend = {'req': 'LOG', 'type': 'INFO', 'process': 'COLLECTOR',
              'message': "started collector server", 'method': 'collector'}
    theLogSocket.send(json.dumps(toSend).encode())
    theLogSocket.close()
    results_receiver = context.socket(zmq.PULL)
    results_receiver.bind("tcp://*:" + str(port))
    workerpool = concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 2)  # Using threads
    lockList = manager.list()  # Make a structure that is dependent of database
    timeStart = time.time()
    BACKUPPATH = ''
    IMPORTPATH = ''
    ADDONPATH = ''
    daqbrokerSettings.setupLocalVars(localPath)
    newPaths = checkPaths(context, BACKUPPATH, IMPORTPATH, ADDONPATH, logPort)
    paths = {"BACKUPPATH": newPaths[0], "IMPORTPATH": newPaths[1], "ADDONPATH": newPaths[2]}
    sessions = {}
    while True:
        try:
            result = results_receiver.recv_json()
            if 'order' in result:
                if result["order"] == "METASYNCOVER":  # Lock the instrument for parsing
                    #print(result)
                    for server in servers:
                        if server["server"] == result["server"] and server["engine"] == result["engine"]:
                            if server["server"]+server["engine"] not in sessions:
                                sessions[server["server"]+server["engine"]]={}
                            else:
                                if result["database"] not in sessions[server["server"]+server["engine"]]:
                                    serverURL = server["engine"] + "://" + server["username"] + ":" + \
                                                server["password"] + "@" + server["server"] + "/daqbro_" + result["database"]
                                    eng = create_engine(serverURL, connect_args={'connect_timeout': 120}, isolation_level ="READ_COMMITTED")
                                    sessions[server["server"] + server["engine"]][result["database"]] = {'session': scoped_session(sessionmaker(bind=eng)), 'engine': eng}
                            if server["server"]+server["engine"] in sessions:
                                if result["database"] in sessions[server["server"]+server["engine"]]:
                                    daqbrokerDatabase.daqbroker_database.metadata.reflect(bind=sessions[server["server"] + server["engine"]][result["database"]]["engine"])
                                    workerpool.submit(
                                        backupOver,
                                        sessions[server["server"] + server["engine"]][result["database"]]["session"],
                                        server,
                                        result["database"],
                                        result["metaid"],
                                        result["instrument"],
                                        logPort,
                                        lockList,
                                        paths)
            if time.time() - timeStart > 10:
                BACKUPPATH = ''
                IMPORTPATH = ''
                ADDONPATH = ''
                newPaths = checkPaths(context, BACKUPPATH, IMPORTPATH, ADDONPATH, logPort)
                paths = {"BACKUPPATH": newPaths[0], "IMPORTPATH": newPaths[1], "ADDONPATH": newPaths[2]}
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
                'process': 'COLLECTOR',
                'message': str(e),
                'filename': filename,
                'lineno': lineno,
                'funname': funname,
                'line': line}
            theLogSocket.send(json.dumps(toSend).encode())
            theLogSocket.close()


# Should be able to protect with string from xsfr (TODO LATER)
def backupOver(scopedSession, server, database, metaid, instrument, logPort, lockList, paths):
    """ Supporting function that updates the state of the database when a remote instrument's data backup is completed

    :param server: (Dict) server dictionary, contains the address and the database engine
    :param database: (String) database name
    :param metaid: (Integer) unique data source identifier
    :param instrument: (String) instrument name
    :param logPort: (String) database server address
    :param lockList: (String) database server address
    :param paths: (`multiporcessing.Manager().list`_) database server address

    .. _multiporcessing.Manager().list: https://docs.python.org/2/library/multiprocessing.html#sharing-state-between-processes

    """
    try:
        session = scopedSession()
        theMeta = session.query(daqbrokerDatabase.instmeta).filter_by(metaid=metaid).first()
        theMeta.sentRequest=False
        #session.commit()
        if theMeta:
            theMetaRemarks = json.loads(theMeta.remarks)
            theParsingRemarks = json.loads(theMeta.parsing[0].remarks)
            if theMetaRemarks['toParse']:
                parseThis = True
                thisIdx = -1
                notFound = True
                for q, el in enumerate(lockList):
                    # Found the entry, must alter this
                    #print(el)
                    if el['instrument'] == instrument and el["meta"] == theMeta.name and el["database"] == database and el["server"] == server["server"]:
                        if el['locked']:
                            parseThis = False
                        notFound = False
                        thisIdx = q
                        break
                if notFound:
                    lockList.append({'server': server["server"], 'database': database,
                                     'instrument': instrument, 'meta': theMeta.name, 'locked': False})
                if parseThis:
                    lockList[thisIdx] = {
                        'server': server["server"],
                        'database': database,
                        'instrument': instrument,
                        'meta': theMeta.name,
                        'locked': True}
                    #print("AMPARSING",instrument,metaid) #GOTTA START HERE NOW TO THE PARSEMETA FUNCTION
                    #theTable_data = daqbrokerDatabase.daqbroker_database.metadata.tables[instrument + "_data"]
                    #print(theTable_data.c)
                    parseMeta(server["server"], database, {
                             "Name": instrument, "instid": theMeta.meta.instid}, theMeta, paths, logPort, lockList, session)
        session.commit()
    except BaseException:
        traceback.print_exc()
        session.rollback()
        poop = "poop"

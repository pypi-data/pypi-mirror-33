import time
import json
import traceback
import multiprocessing
import shutil
import uuid
import os
import zmq
import sqlite3
import daqbrokerSettings
import app
import daqbrokerDatabase
import rsa
import pickle
from sqlalchemy import text, bindparam, create_engine, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy_views import CreateView, DropView
from sqlalchemy_utils.functions import database_exists
from sqlalchemy_utils.functions import drop_database
from sqlalchemy_utils.functions import create_database
from flask import Blueprint
from flask import request
from flask import render_template
from flask import session
from flask import jsonify
from flask import current_app
from flask_login import login_required
from flask_login import current_user
from bpApp import multiprocesses
from supportFuncs import *

adminBP = Blueprint('admin', __name__, template_folder='templates')

base_dir = '.'
if getattr(sys, 'frozen', False):
    base_dir = os.path.join(sys._MEIPASS)

@adminBP.route("/db", methods=['GET'])
@login_required
@require_admin
def db():
    # connection=connect(request)
    session['currentURL'] = url_for('admin.db')
    # engineURL=current_user.engine+'://'+current_user.username+':'+current_user.password+"@"+current_user.server+"/daqbroker_settings"
    return render_template('admin/main.html')


@adminBP.route("/local", methods=['GET'])
@login_required
@require_admin
def local():
    connection = connect(request)
    session['currentURL'] = url_for('admin.local')
    return render_template('admin/mainLocal.html')


@adminBP.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    if request.method == 'POST':
        return response
    else:
        return render_template("error.html", errorMsg=error.to_dict()["message"], errorNo=error.status_code)


@adminBP.route('/actProcess', methods=['POST'])
@login_required
def actProcess():
    """ Request to start or stop database monitoring processes

    .. :quickref: Act on DAQBroker processes; Preform actions on available DAQBroker processes

    :param procName: (String) DAQBroker subprocess to be acted on

            | ``Backup`` : Backup server process
            | ``Logger`` : Event logging process
            | ``Collector`` : Communication process
            | ``Producer`` : Database monitoring process

    :param action: (String) action to be preformed on **procName**

            | ``add`` : Start (if not already)
            | ``remove`` : Stop (if not already)

    :returns: JSON string containing the following keys:

            | ``alive`` : Boolean value defining whether the process is alive or not
            | ``name`` : Name of the process, same as **procName**

    """
    if('procName' in request.form):
        procName = request.form['procName']
    else:
        raise InvalidUsage('No process name provided', status_code=400)
    if('action' in request.form):
        action = request.form['action']
    else:
        raise InvalidUsage('No action provided', status_code=400)
    foundProcess = False
    for i, process in enumerate(multiprocesses):
        if process["name"] == procName:
            foundProcess = True
            toReturn = {}
            toReturn["name"] = process["name"]
            try:
                theProcess = psutil.Process(process['pid'])
            except BaseException:
                theProcess = None
            try:
                if action == 'remove':  # Terminate process
                    if theProcess:
                        for child in theProcess.children(recursive=True):  # or parent.children() for recursive=False
                            child.terminate()
                        theProcess.kill()
                        theProcess.wait()
                    else:
                        raise InvalidUsage('Process is already terminated', status_code=400)
                elif action == 'add':  # Start process
                    if not theProcess:
                        if procName == 'infinite':  # Maybe create an array of dicts with necessary parameters
                            p = multiprocessing.Process(target=infinite)
                            p.start()
                            multiprocesses[i]["pid"] = p.pid
                        elif procName == 'Backup':
                            p = multiprocessing.Process(target=startBackup, args=('static/rsync',))
                            p.start()
                            multiprocesses[i]["pid"] = p.pid
                        theProcess = psutil.Process(multiprocesses[i]['pid'])
                    elif theProcess.is_running():
                        raise InvalidUsage('Process already started', status_code=400)
            except Exception as e:
                traceback.print_exc()
                raise InvalidUsage(str(e), status_code=500)
            break
    if not foundProcess:
        raise InvalidUsage("Could not find requested process", status_code=500)
    time.sleep(1)
    if theProcess:
        toReturn["alive"] = theProcess.is_running()
    else:
        toReturn["alive"] = False
    return jsonify(toReturn)


@adminBP.route("/queryGlobals", methods=['POST'])
@login_required
def queryGlobals():
    """ Query local machine storage for settings

    .. :quickref: Get local settings; Get local server settings

    :returns: JSON encoded string containing local machine settings. This is an object with the following keys:

            | ``clock`` : Timestamp of last alteration to settings
            | ``version`` : Version of the server application being used
            | ``backupfolder`` : Backup folder
            | ``importfolder`` : Imports folder
            | ``tempfolder`` : Temporary file folder
            | ``ntp`` : NTP server used for software synchronization
            | ``logport`` : Network port for logging server
            | ``commport`` : Network port for communication
            | ``remarks`` : JSON encoded string containing machine health information

    """
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    globalObj = session.query(
        daqbrokerSettings.Global).filter_by(
        clock=session.query(
            func.max(
                daqbrokerSettings.Global.clock))).first()
    if globalObj:
        globals = {}
        for field in globalObj.__dict__:
            if not field.startswith('_'):
                globals[field] = getattr(globalObj, field)
    else:
        globals = {
            'clock': time.time(),
            'version': '0.1',
            'backupfolder': 'backups',
            'importfolder': 'uploads',
            'addonfolder': 'addons',
            'ntp': None,
            'remarks': {},
            'commport': 9090,
            'logport': 9092,
            'isDefault': True}  # Default values, should I use this?
    return jsonify(globals)


@adminBP.route("/setPorts", methods=['POST'])
@login_required
@require_admin
def setPorts():
    """ Request to alter DAQBroker's network ports

    .. :quickref: Get/Set ports; Get/Set DAQBroker network ports

    :param commport: Integer containing the requested port of the communications port
    :param logport: Integer containing the requested port of the log port

    """
    if('commport' in request.form):
        commport = request.form['commport']
    elif('commport' in request.args):
        commport = request.args['commport']
    else:
        commport = None
    if('logport' in request.form):
        logport = request.form['logport']
    elif('logport' in request.args):
        logport = request.args['logport']
    else:
        logport = None
    if((not logport) and (not commport)):
        raise InvalidUsage("No port name provided to change", status_code=400)
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    globalObj = session.query(
        daqbrokerSettings.Global).filter_by(
        clock=session.query(
            func.max(
                daqbrokerSettings.Global.clock))).first()
    if logport:
        globalObj.logport = logport
    if commport:
        globalObj.commport = commport
    session.commit()
    return jsonify("done")


@adminBP.route("/checkNTPServers", methods=['POST'])
@login_required
@require_admin
def checkNTPServers():
    """ Set or get the NTP servers used for software synchronization by DAQBroker

    .. :quickref: Get/Set NTP servers; Get/Set NTP servers

    :param addServer: string containing the address of the NTP server to add/update to the list of available servers
    :param setServer: string containing the address of the NTP server to set as the synchronization server
    :param port: Integer containing the port of the NTP server

    :returns: If **addServer** and **setServer** are not provided, returns a JSON encoded string of a list of available NTP servers. Each object in the list contains the following keys:

            | ``address`` : string containing the address of the NTP server
            | ``port`` : integer containing the NTP network port

    """
    addServer = False
    setServer = False
    returnQs = []
    if('addServer' in request.form):
        addServer = True
        toAddServer = request.form['addServer']
    elif('addServer' in request.args):
        addServer = True
        toAddServer = request.args['addServer']
    if('setServer' in request.form):
        setServer = True
        toSetServer = request.form['setServer']
    elif('setServer' in request.args):
        setServer = True
        toSetServer = request.args['setServer']
    if('port' in request.form):
        port = request.form['port']
    elif('port' in request.args):
        port = request.args['port']
    else:
        port = 123
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    if addServer or setServer:
        try:
            newNTP = daqbrokerSettings.ntp(clock=time.time(), server=toAddServer, port=port)
            getNTPTime(toAddServer)
        except:
            raise InvalidUsage('Could not contact NTP server', status_code=500)
        session.add(newNTP)
        session.commit()
        return jsonify("done")
    elif setServer and not addServer:
        currNTP = session.query(
            daqbrokerSettings.ntp).filter_by(
            clock=session.query(
                func.max(
                    daqbrokerSettings.ntp.clock))).first()
        currNTP = toSetServer
        return jsonify("done")
    elif addServer and setServer:
        raise InvalidUsage("Please provide only a server to add or to set, not both!", status_code=500)
    else:
        ntpServers = []
        for ntp in session.query(daqbrokerSettings.ntp):
            objc= {}
            for field in ntp.__dict__:
                if not field.startswith('_'):
                    objc[field] = getattr(ntp, field)
            ntpServers.append(objc)
        return jsonify(ntpServers)


@adminBP.route("/checkFolders", methods=['POST'])
@login_required
def checkFolders():
    """ Get or set the folders available to use as backup, import or temporary folder

    .. :quickref: Get/Set folders; Get/Set usable server folders

    :param addFolder: String containing the folder to be added to the list of available folders
    :param setFolder: String containing the folder to be set as a specific type of folder
    :param folderChange (optional): An integer defining the path to be set. Can be set to 0 (backup), 1 (import) or 2 (temp). If not supplied, no folder is changed

    :returns: If **folderChange** and **addFolder** are not provided, returns a JSON encoded string of a list of available folders. Each object in the list contains the following keys:

            | ``path`` : string containing the address of the NTP server

    """
    addFolder = False
    setFolder = False
    returnQs = []
    if('addFolder' in request.form):
        addFolder = True
        toAddFolder = request.form['addFolder']
    elif('addFolder' in request.args):
        addFolder = True
        toAddFolder = request.args['addFolder']
    if('setFolder' in request.form):
        setFolder = True
        toSetFolder = request.form['setFolder']
    elif('setFolder' in request.args):
        setFolder = True
        toSetFolder = request.args['setFolder']
    if setFolder or addFolder:
        if('folderChange' in request.form):
            folderChange = request.form['folderChange']
        elif('folderChange' in request.args):
            folderChange = request.args['folderChange']
        else:
            raise InvalidUsage('No folder type supplied', status_code=500)
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    globalObj = session.query(
        daqbrokerSettings.Global).filter_by(
        clock=session.query(
            func.max(
                daqbrokerSettings.Global.clock))).first()
    try:
        if(addFolder and not setFolder):
            theFolder = session.query(daqbrokerSettings.folder).filter_by(path=toAddFolder)
            if not theFolder:
                theFolder = daqbrokerSettings.folder(clock=time.time(), path=toAddFolder, type=0, remarks='{}')
                session.add(theFolder)
            if int(folderChange) == 0:
                globalObj.backupfolder=toAddFolder
            elif int(folderChange) == 1:
                globalObj.importfolder=toAddFolder
            elif int(folderChange) == 2:
                globalObj.tempfolder = toAddFolder
            else:
                raise InvalidUsage('Invalid folder type supplied', status_code=500)
            session.commit()
            if os.path.isdir(toAddFolder):
                toReturn = {'error': 0}
            else:
                toReturn = {
                    'error': 0,
                    'warning': 'Path not found on server, make sure this path exists before using it!'}
            return jsonify(toReturn)
        elif(setFolder and not addFolder):
            if int(folderChange) == 0:
                globalObj.backupfolder = toAddFolder
            elif int(folderChange) == 1:
                globalObj.importfolder = toAddFolder
            elif int(folderChange) == 2:
                globalObj.tempfolder = toAddFolder
            else:
                raise InvalidUsage('Invalid folder type supplied', status_code=500)
            session.commit()
            if os.path.isdir(toSetFolder):
                toReturn = {'error': 0}
            else:
                toReturn = {
                    'error': 0,
                    'warning': 'Path not found on server, make sure this path exists before using it!'}
            return jsonify(toReturn)
        else:
            folders = []
            for folder in session.query(daqbrokerSettings.folder):
                objc = {}
                for field in folder.__dict__:
                    if not field.startswith('_'):
                        objc[field] = getattr(folder, field)
                folders.append(objc)
                folders[-1]["good"]=os.path.isdir(folders[-1]["path"])
            return jsonify(folders)
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        raise InvalidUsage(str(e), status_code=500)


@adminBP.route("/checkUsers", methods=['POST'])
@login_required
def checkUsers():
    """ Get a list of available DAQBroker users

    .. :quickref: List users; List of server DAQBroker users

    :returns: JSON list of user objects. A user object has the following attributes

            | ``username`` : (String) user name
            | ``type`` : (String) type of user. Visit PLACEHOLDER for definition of user types

    """
    users = []
    Session = sessionmaker(bind=current_user.engineObjSettings)
    session = Session()
    result = session.query(daqbrokerSettings.users)
    for row in result:
        theObjct = {}
        for field in row.__dict__:
            if not field.startswith('_'):
                theObjct[field] = getattr(row, field)
        # instruments.append(json.dumps(row,cls=AlchemyEncoder))
        users.append(theObjct)
    return jsonify(users)


@adminBP.route("/queryUsers", methods=['POST'])
@login_required
@require_admin
def queryUsers():
    """ Get a list of available DAQBroker users

    .. :quickref: List users; List of server DAQBroker users

    :returns: JSON list of user objects. A user object has the following attributes

            | ``username`` : (String) user name
            | ``type`` : (String) type of user. Visit PLACEHOLDER for definition of user types

    """
    users = []
    Session = sessionmaker(bind=current_user.engineObjSettings)
    session = Session()
    result = session.query(daqbrokerSettings.users)
    for row in result:
        theObjct = {}
        for field in row.__dict__:
            if not field.startswith('_'):
                theObjct[field] = getattr(row, field)
        # instruments.append(json.dumps(row,cls=AlchemyEncoder))
        users.append(theObjct)
    return jsonify(users)


@adminBP.route("/deleteUser", methods=['POST'])
@login_required
@require_admin
def deleteUser():
    """ Delete an existing DAQBroker user

    .. :quickref: Delete user; Delete a DAQBroker user

    :param: userToDelete : (String) Name of user to delete

    """
    Session = sessionmaker(bind=current_user.engineObjSettings)
    session = Session()
    if('userToDelete' in request.form):
        username = request.form['userToDelete']
    elif('userToDelete' in request.args):
        username = request.args['userToDelete']
    else:
        raise InvalidUsage('No username provided', status_code=500)
    theUser = session.query(daqbrokerSettings.users).filter_by(username=username).first()
    #result = connection.execute(text("SELECT * FROM daqbroker_settings.users WHERE username=:uname").bindparams(uname=username))
    #session.execute(text("DROP USER :uname").bindparams(uname=username))
    if "mysql" in current_user.engine:  # Is a mysql server:
        session.execute(text("DROP USER :uname").bindparams(uname=username))
    elif "postgres" in current_user.engine:  # Is a Postgres server
        session.execute(text("SET ROLE DAQBROKER_ADMIN"))
        #session.execute(text("REASSIGN OWNED BY "+username+" TO "+current_user.username))
        #session.execute(text("DROP OWNED BY "+username))
        result = session.query(daqbrokerSettings.databases)
        for row in result:
            newURL = current_user.uriHome + "/daqbro_" + row.dbname
            iteratorEngine = create_engine(newURL)
            # SessionStupid = sessionmaker(bind=iteratorEngine)
            # sessionStupid = Session()
            # sessionStupid.execute(text("REVOKE ALL PRIVILEGES ON DATABASE FROM "+username))
            # session.execute(text("REVOKE ALL PRIVILEGES ON DATABASE daqbro_"+row.dbname+" FROM "+username))
        session.execute(text("DROP USER " + username))
        drop_database(current_user.uriHome + "/" + username)
    elif "oracle" in current_user.engine:  # Is a Oracle server
        session.execute(text("DROP USER " + username))
    elif "mssql" in current_user.engine:  # Is a MS SQL server
        session.execute(text("DROP USER " + username))
    else:
        raise InvalidUsage('Unsupported database engine for user accounts', status_code=500)
    result = session.query(daqbrokerSettings.databases)
    session.delete(theUser)
    session.commit()
    return jsonify('done')


@adminBP.route("/submitUserData", methods=['POST'])
@login_required
@require_admin
def submitUserData():
    """ Create/Edit a DAQBroker user account. Only system administrators are allowed to create new users.

    .. :quickref: Create/Edit user account; Create or edit a DAQBroker user account

    :param: newUser : (Boolean) Tests to insert or edit an existing user
    :param: newName : (String) New username to change/add
    :param: oldName : (String) Old username. To use with True **newUser**
    :param: userType : (Integer) User type to change/add

            | ``0`` : Adminstrator
            | ``1`` : Operator
            | ``2`` : User
            | ``3`` : Guest

    :param: newPassword : (String) User password to change/add

    """
    thisSession = create_engine(current_user.uriSettings, isolation_level="AUTOCOMMIT")
    Session = sessionmaker(bind=thisSession)
    session = Session()
    if 'newUser' in request.form:
        newUser = request.form['newUser']
    elif 'newUser' in request.args:
        newUser = request.args['newUser']
    else:

        raise InvalidUsage('No action specified', status_code=400)
    if 'newName' in request.form:
        newName = request.form['newName']
    elif 'newName' in request.args:
        newName = request.args['newName']
    else:

        raise InvalidUsage('No new user name specified', status_code=400)
    if 'userType' in request.form:
        userType = request.form['userType']
    elif 'userType' in request.args:
        userType = request.args['userType']
    else:

        raise InvalidUsage('No user type specified', status_code=400)
    if 'newPassword' in request.form:
        newPassword = request.form['newPassword']
    elif 'newPassword' in request.args:
        newPassword = request.args['newPassword']
    else:

        raise InvalidUsage('No new password provided', status_code=400)
    if 'oldName' in request.form:
        oldName = request.form['oldName']
    elif 'oldName' in request.args:
        oldName = request.args['oldName']
    else:
        raise InvalidUsage('No username provided', status_code=400)
    try:
        if newUser == 'true':  # Create new user
            addNewUser(newName, userType, newPassword, current_user, session)
        elif newUser == 'false':  # Edit existing user
            currentUser = session.query(daqbrokerSettings.users).filter_by(username=oldName).first()
            if not (newName == oldName):
                if "mysql" in current_user.engine:  # Is a mysql server:
                    session.execute(text("RENAME USER :oldname TO :newName"), oldname=oldName, newname=newName)
                elif "postgres" in current_user.engine:  # Is a Postgres server
                    session.execute(text("SET ROLE DAQBROKER_ADMIN"))
                    session.execute(text("ALTER USER " + oldName + " RENAME TO " + newName))
                    session.execute(text("ALTER DATABASE " + oldName + " RENAME TO " + newName))
                elif "oracle" in current_user.engine:  # Is a Oracle server
                    session.execute(
                        text(
                            "update sys.user$ set name='" +
                            newName +
                            "' where user#=N and name='" +
                            oldName +
                            "';"))
                elif "mssql" in current_user.engine:  # Is a MS SQL server
                    session.execute(text("ALTER LOGIN " + oldName + " WITH NAME = " + newName + ";"))
                else:
                    raise InvalidUsage('Unsupported database engine for user accounts', status_code=500)
                currentUser.username = newName
            if not currentUser.type == int(userType):
                if "mysql" in current_user.engine:  # Is a mysql server:
                    session.execute(text("REVOKE ALL PRIVILEGES, GRANT OPTION FROM :username"), {'username': newName})
                    if userType == '1':  # Administrator
                        session.execute(text("GRANT ALL ON `daqbro\_%`.* TO :username WITH GRANT OPTION"),
                                        {'username': newName})
                        session.execute(
                            text("GRANT ALL ON `daqbroker_settings`.* TO :username WITH GRANT OPTION"), {'username': newName})
                        session.execute(text("GRANT CREATE USER ON *.* TO :username WITH GRANT OPTION"),
                                        {'username': newName})
                    elif userType == '2':  # Operator
                        session.execute(text("GRANT SELECT ON `daqbro\_%`.* TO :username"), {'username': newName})
                        session.execute(text("GRANT SELECT ON `daqbroker_settings`.* TO :username"),
                                        {'username': newName})
                    elif userType == '3':  # User
                        session.execute(text("GRANT SELECT ON `daqbro\_%`.* TO :username"), {'username': newName})
                        session.execute(text("GRANT SELECT ON `daqbroker_settings`.* TO :username"),
                                        {'username': newName})
                elif "postgres" in current_user.engine:  # Is a Postgres server
                    session.execute(text("SET ROLE DAQBROKER_ADMIN"))
                    if userType == '1':  # Administrator
                        session.execute(text("GRANT DAQBROKER_ADMIN TO " + newName + ";"))
                    elif userType == '2':  # Operator
                        session.execute(text("REVOKE DAQBROKER_ADMIN FROM " + newName + ";"))
                        session.execute(text("ALTER USER " + newName + " NOCREATEDB NOCREATEROLE"))
                        session.execute(text("GRANT DAQBROKER_OPERATOR TO " + newName + ";"))
                    elif userType == '3':  # User
                        session.execute(text("REVOKE DAQBROKER_ADMIN FROM " + newName + ";"))
                        session.execute(text("REVOKE DAQBROKER_OPERATOR FROM " + newName + ";"))
                        session.execute(text("ALTER USER " + newName + " NOCREATEDB NOCREATEROLE"))
                        session.execute(text("GRANT DAQBROKER_USER TO " + newName + ";"))
                elif "oracle" in current_user.engine:  # Is a Oracle server
                    session.execute(text("REVOKE ALL PRIVILEGES FROM " + newName + ";"))
                elif "mssql" in current_user.engine:  # Is a MS SQL server
                    session.execute(text("REVOKE ALL FROM " + newName + ";"))
                else:
                    raise InvalidUsage('Unsupported database engine for user accounts', status_code=500)
                currentUser.type = int(userType)
            if not (newPassword == ''):
                if "mysql" in current_user.engine:  # Is a mysql server:
                    session.execute(
                        text("SET PASSWORD FOR :username = PASSWORD(:pword)"),
                        username=newName,
                        pword=newPassword)
                elif "postgres" in current_user.engine:  # Is a Postgres server
                    session.execute(text("ALTER USER " + newName + " WITH PASSWORD '" + newPassword + "';"))
                elif "oracle" in current_user.engine:  # Is a Oracle server
                    session.execute(text("ALTER USER " + newName + " IDENTIFIED BY " + newPassword + ";"))
                elif "mssql" in current_user.engine:  # Is a MS SQL server
                    session.execute(text("ALTER LOGIN " + newName + " WITH PASSWORD = '" + newPassword + "';"))
                else:
                    raise InvalidUsage('Unsupported database engine for user accounts', status_code=500)
        session.commit()
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        raise InvalidUsage(str(e), status_code=500)

    return jsonify('done')


@adminBP.route("/createDatabase", methods=['POST'])
@login_required
@require_admin
def createDatabase():
    """ Create a new DAQBroker database

    .. :quickref: Create databases; Create a new DAQBroker databases

    :param: newName : (String) new database name

    """
    resultDBs = []
    if 'newName' in request.form:
        newdbname = request.form['newName']
    elif 'newName' in request.args:
        newdbname = request.args['newName']
    else:

        raise InvalidUsage('No database name provided', status_code=500)
    try:
        dbCreated = False
        print(current_user.engineObj, current_user.engine, current_user.uriHome)
        create_database(current_user.uriHome + "/daqbro_" + newdbname)
        oldDB = current_user.database
        oldURI = current_user.uri
        current_user.database = newdbname
        current_user.uri = current_user.uriHome + '/daqbro_' + newdbname
        current_user.updateDB()
        dbCreated = True
        sessionDB = False
        current_user.engineObj.echo = True
        print(current_user.engineObj, current_user.engine, current_user.uriHome)
        #daqbrokerDatabase.daqbroker_database.metadata.clear()
        #daqbrokerDatabase.daqbroker_database.metadata.drop_all(current_user.engineObj)
        daqbrokerDatabase.daqbroker_database.metadata.reflect(bind=current_user.engineObj)
        daqbrokerDatabase.daqbroker_database.metadata.create_all(current_user.engineObj)
        if 'postgres' in current_user.engine:  # Fucking ridiculous postgres roles
            SessionNew = sessionmaker(bind=create_engine(current_user.uriHome + "/daqbro_" + newdbname))
            sessionNew = SessionNew()
            sessionNew.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO DAQBROKER_USER")
            sessionNew.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO DAQBROKER_USER")
            sessionNew.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO DAQBROKER_OPERATOR")
            sessionNew.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO DAQBROKER_OPERATOR")
            sessionNew.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO DAQBROKER_ADMIN")
            sessionNew.execute(
                "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO DAQBROKER_ADMIN")
            for tableName in daqbrokerDatabase.daqbroker_database.metadata.tables.keys():
                sessionNew.execute("ALTER TABLE " + tableName + " OWNER TO DAQBROKER_ADMIN")
            sessionNew.execute("ALTER DATABASE daqbro_" + newdbname + " OWNER TO DAQBROKER_ADMIN")
            sessionNew.commit()
        newDB = daqbrokerSettings.databases(dbname=newdbname, active=False)
        Session = sessionmaker(bind=current_user.engineObjSettings)
        sessionDB = Session()
        sessionDB.add(newDB)
        sessionDB.commit()
        current_user.engineObj.echo = False
        #connection.execute(text("INSERT INTO `daqbroker_settings`.`databases` VALUES(:dbname,'0')"),dbname=newdbname)
    except Exception as e:
        traceback.print_exc()
        current_user.engineObj.echo = False
        if sessionDB:
            sessionDB.rollback()
        if dbCreated:
            drop_database(current_user.uriHome + "/daqbro_" + newdbname)
        current_user.database = oldDB
        current_user.uri = oldURI
        current_user.updateDB()
        raise InvalidUsage(str(e), status_code=500)
    return jsonify('done')


@adminBP.route("/deleteDatabase", methods=['POST'])
@login_required
@require_admin
def deleteDatabase():
    """ Delete an existing DAQBroker database in the supplied database engine

    .. :quickref: Delete database; Deletes a DAQBroker database

    :param: dbname : (String) database name

    """
    if 'dbnameDelete' in request.form:
        theDBname = request.form['dbnameDelete']
    elif 'dbnameDelete' in request.args:
        theDBname = request.args['dbnameDelete']
    else:
        raise InvalidUsage('No database name provided', status_code=500)
    try:
        Session = sessionmaker(bind=current_user.engineObjSettings)
        theSession = Session()
        dbTable = daqbrokerSettings.daqbroker_settings.metadata.tables["databases"]
        theSession.execute(dbTable.update().where(dbTable.c.dbname == theDBname).values({'active': False}))
        time.sleep(5)
        if current_user.database == theDBname:
            current_user.database = None
            current_user.uri = current_user.uriHome
            current_user.engineObj = create_engine(current_user.uri)
            current_user.updateDB()
        theDB = theSession.query(daqbrokerSettings.databases).filter_by(dbname=theDBname).first()
        theSession.delete(theDB)
        drop_database(current_user.uriHome + "/daqbro_" + theDBname)
    except Exception as e:
        theSession.rollback()
        raise InvalidUsage(str(e), status_code=500)
    BACKUPPATH = ''
    IMPORTPATH = ''
    ADDONPATH = ''
    context = zmq.Context()
    newPaths = checkPaths(context, BACKUPPATH, IMPORTPATH, ADDONPATH, 15000)
    paths = {"BACKUPPATH": newPaths[0], "IMPORTPATH": newPaths[1], "ADDONPATH": newPaths[2]}
    pathDel = os.path.join(paths["BACKUPPATH"], current_user.server, theDBname)
    try:
        shutil.rmtree(pathDel)
    except BaseException:
        poop = "poop"

    theSession.commit()
    return jsonify('done')


@adminBP.route("/toggleDatabase", methods=['POST'])
@login_required
def toggleDatabase():
    """ Toggle the active state of an existing DAQBroker database. When active, databases will have their instruments monitored for new data.

    .. :quickref: Toggle database status; Toggle DAQBroker database monitoring status

    :param: dbname : (String) database name

    """
    Session = sessionmaker(bind=current_user.engineObjSettings)
    session = Session()
    if 'dbname' in request.form:
        dbname = request.form['dbname']
    elif 'dbname' in request.args:
        dbname = request.args['dbname']
    else:
        raise InvalidUsage('No database name provided', status_code=500)
    try:
        theDatabase = session.query(daqbrokerSettings.databases).filter_by(dbname=dbname).first()
        theDatabase.active = not theDatabase.active
    except Exception as e:
        session.rollback()
        raise InvalidUsage(str(e), status_code=500)
    session.commit()
    return jsonify('done')


@adminBP.route("/setupSettings", methods=['POST'])
@login_required
def setupSettings():
    """ Create a global settings DAQBroker database on a supplied database server

    .. :quickref: Create global settings; create global DAQBroker settings database

    """
    try:
        databaseCreated = False
        engineURL = current_user.engine + '://' + current_user.username + ':' + \
            current_user.password + "@" + current_user.server + "/daqbroker_settings"
        create_database(engineURL)
        dbEngine = create_engine(engineURL)
        databaseCreated = True
        daqbrokerSettings.daqbroker_settings.metadata.create_all(dbEngine)
        mainUser = daqbrokerSettings.users(username=current_user.username, type=1)
        Session = sessionmaker(bind=dbEngine)
        session = Session()
        session.add(mainUser)
        if 'postgres' in current_user.engine:  # Fucking ridiculous postgres
            session.execute("CREATE ROLE DAQBROKER_OPERATOR")
            session.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO DAQBROKER_OPERATOR")
            session.execute("CREATE ROLE DAQBROKER_ADMIN")
            session.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO DAQBROKER_ADMIN")
            session.execute("ALTER USER DAQBROKER_ADMIN CREATEROLE CREATEDB")
            session.execute("CREATE ROLE DAQBROKER_USER")
            session.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO DAQBROKER_USER")
            session.execute("ALTER DATABASE daqbroker_settings OWNER TO DAQBROKER_ADMIN")
            for tableName in app.tablesToActSettings:
                session.execute("ALTER TABLE " + tableName + " OWNER TO DAQBROKER_ADMIN")
        session.commit()
        return jsonify('done')
    except Exception as e:
        if databaseCreated:
            drop_database(engineURL)
            session.rollback()
        raise InvalidUsage(str(e), status_code=500)
    else:
        raise InvalidUsage("Could not connect to database", status_code=400)


@adminBP.route("/testAdminOneTime", methods=['POST'])
@login_required
@require_onetime_admin
def testAdminOneTime():
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    current_user.updateDB()
    return jsonify("done")


@adminBP.route("/toggleMonitoring", methods=['POST'])
@login_required
def setMonitoring():
    """ Toggle the database monitoring loop of a supplied DAQBroker database. See PLACEHOLDER for more information about the server monitoring process

    .. :quickref: Toggle server monitoring process; Toggle server monitoring process

    """
    global servers
    connection = connect(request)
    if connection:
        engineURL = current_user.engine + '://' + current_user.username + ':' + \
            current_user.password + "@" + current_user.server + "/daqbroker_settings"
        if database_exists(engineURL):
            thisUser = getUserDetails(current_user.username, connection)
            if thisUser['type'] == 1:

                foundServer = False
                for i, server in enumerate(current_app.config['servers']):
                    if server["server"] == current_user.server and server["engine"] == current_user.engine:
                        temp = server
                        temp["monActive"] = not temp["monActive"]
                        current_app.config['servers'][i] = temp
                        foundServer = True
                        break
                if foundServer:
                    return jsonify("done")
                else:
                    raise InvalidUsage("Server info not found", status_code=500)
            else:

                raise InvalidUsage("This page is not for you, smarty pants", status_code=403)
        else:
            raise InvalidUsage(
                "Could not find DAQBroker settings with supplied credentials, please contact your network administrator to ensure your server and credentials are appropriate",
                status_code=403)
    else:
        raise InvalidUsage("Could not connect to database", status_code=400)


def grantUserPrivileges(session, database, privileges, username, tablename, user):
    if "mysql" in user.engine:  # Is a mysql server:
        session.execute(" GRANT " + ','.join(privileges) + " ON " + database + "." + tablename + " TO " + username)
    elif "postgres" in user.engine:  # Is a Postgres server
        if tablename == "*":
            session.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT " +
                            ','.join(privileges) + " ON tables TO " + username)
            session.execute("GRANT " + ','.join(privileges) + " ON ALL TABLES IN SCHEMA public TO " + username)
        else:
            session.execute("GRANT " + ','.join(privileges) + " ON " + tablename + " IN SCHEMA public TO " + username)
    elif "oracle" in user.engine:  # Is a Oracle server
        session.execute(" GRANT " + ','.join(privileges) + " ON " + tablename + " TO " + username)
    elif "mssql" in user.engine:  # Is a MS SQL server
        session.execute(" GRANT " + ','.join(privileges) + " ON " + tablename + " TO " + username)
    else:
        raise InvalidUsage('Unsupported database engine for user accounts', status_code=500)


def addNewUser(username, userType, newPassword, current_user, session):
    try:
        userDoesNotExist = True
        phoneyEngine = create_engine(
            current_user.engine +
            "://" +
            username +
            ":" +
            newPassword +
            "@" +
            current_user.server).connect()  # This should fail if the user doesn't exist
        userDoesNotExist = False
        # If the user exists we go into changing their privileges - MORE ON THAT LATER
    except BaseException:  # We're assuming the user doesn't exist and that's the error we have
        if userDoesNotExist:
            try:
                second = None
                allGood = True
                if "mysql" in current_user.engine:  # Is a mysql server:
                    session.execute(text("CREATE USER :username @:stupid IDENTIFIED BY :password"),
                                    {'stupid': '%', 'username': username, 'password': newPassword})
                    if userType == '1':
                        session.execute(text("GRANT ALL ON `daqbro\_%`.* TO :username WITH GRANT OPTION"),
                                        {'username': username})
                        session.execute(
                            text("GRANT ALL ON `daqbroker_settings`.* TO :username WITH GRANT OPTION"), {'username': username})
                        session.execute(text("GRANT CREATE USER ON *.* TO :username WITH GRANT OPTION"),
                                        {'username': username})
                    second = text("DROP USER :username").bindparams(username=username)
                elif "postgres" in current_user.engine:  # Is a Postgres server
                    session.execute(text("CREATE USER " + username + " WITH PASSWORD :password"),
                                    {'password': newPassword})
                    create_database(current_user.uriHome + "/" + username)
                    session.execute("ALTER DATABASE " + username + " OWNER TO DAQBROKER_ADMIN")
                    second = text("DROP ROLE " + username)
                    if userType == '1':  # Administrator
                        session.execute("ALTER USER " + username + " CREATEDB CREATEROLE")
                        session.execute("GRANT DAQBROKER_ADMIN TO " + username)
                    elif userType == '2':  # Operator
                        session.execute("GRANT DAQBROKER_OPERATOR TO " + username)
                    elif userType == '3':  # User
                        session.execute("GRANT DAQBROKER_USER TO " + username)
                elif "oracle" in current_user.engine:  # Is a Oracle server
                    session.execute(
                        text("CREATE USER :username IDENTIFIED BY :password"), {
                            'username': username, 'password': newPassword})
                    second = text("DROP USER :username").bindparams(username=username)
                elif "mssql" in current_user.engine:  # Is a MS SQL server
                    session.execute(
                        text("CREATE LOGIN :username WITH PASSWORD :password"), {
                            'username': username, 'password': newPassword})
                    second = text("DROP USER :username").bindparams(username=username)
                else:
                    raise InvalidUsage('Unsupported database engine for user accounts', status_code=500)
                theUser = daqbrokerSettings.users(username=username, type=int(userType))
                #print(theUser)
                session.add(theUser)
                session.commit()
            except BaseException:
                traceback.print_exc()
                allGood = False
                if second:
                    session.execute(second)
            if not allGood:
                raise InvalidUsage('There was a problem attempting to edit an existing user', status_code=500)
        else:
            raise InvalidUsage('There was a problem attempting to edit an existing user', status_code=500)

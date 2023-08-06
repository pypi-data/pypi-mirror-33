import time
import sys
import json
import traceback
import psutil
import uuid
import os
import hashlib
import sqlite3
import re
import daqbrokerSettings
import zipfile
import pathlib
from asteval import Interpreter
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import bindparam
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists
from sqlalchemy_utils.functions import drop_database
from sqlalchemy_utils.functions import create_database
from flask import Blueprint
from flask import request
from flask import render_template
from flask import redirect
from flask import send_from_directory, send_file
from flask import url_for
from flask import session
from flask import jsonify
from flask import current_app
from flask_login import current_user
#from server import scoped
from supportFuncs import *

multiprocesses = []

daqbroker = Blueprint('daqbroker', __name__, template_folder='templates')

base_dir = '.'
if getattr(sys, 'frozen', False):
    base_dir = os.path.join(sys._MEIPASS)

#login_manager = LoginManager()
# login_manager.init_app(current_app)
#login_manager.login_view = "daqbroker/login"


@daqbroker.route('/dist/<path:filename>')
@login_required
def custom_static(filename):
    return send_from_directory('dist', filename)


@daqbroker.route('/temp/<path:filename>')
@login_required
def custom_static1(filename):
    """ Request to access specific files in the backup directory

    .. :quickref: Get backup files; Get a specific file from a directory in the DAQBroker backup directory

    """
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    #connection = connect(request)
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
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
    #print(request.args)
    #print(filename.split('.'))
    if filename.split('.')[1]=='zip':
        #print("osijdfposdijfopsdfijdopsifjdopsfij")
        return send_file(os.path.join(globals['tempfolder'], filename),mimetype="zip", attachment_filename="downloaded_files.zip", as_attachment=True)
    else:
        return send_from_directory(globals['tempfolder'], filename)

@daqbroker.route('/downloads/<path:filename>')
@login_required
def custom_static2(filename):
    """ Request to access specific files in the backup directory

    .. :quickref: Get backup files; Get a specific file from a directory in the DAQBroker backup directory

    """

    #session = daqbrokerSettings.scoped()
    #connection = connect(request)
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
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
    return send_from_directory(globals['backupfolder'], filename)

@daqbroker.route('/multipleFileDownload', methods=['POST'])
@login_required
def multiFileDownload():
    """ Request to access multiple files in the backup directory

    .. :quickref: Get backup files; Get a specific file from a directory in the DAQBroker backup directory

    """
    try:
        processedRequest=request.get_json()
        scoped = daqbrokerSettings.getScoped()
        session = scoped()
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
        if 'files' in processedRequest:
            files = processedRequest['files']
        else:
            raise InvalidUsage('No file list specified', status_code=400)
        unique = uuid.uuid1()
        zipPath = os.path.join(globals['tempfolder'],str(unique)+'.zip')
        zipf = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)
        for file in files:
            thePath=pathlib.Path(globals['backupfolder']) / pathlib.Path(file)
            try:
                thePathString=thePath.resolve()
                zipf.write(str(thePathString), arcname=thePath.name)
            except:
                traceback.print_exc()
                thePathString = None
        zipf.close()
        #return send_file(unique,mimetype='zip', attachment_filename="downloaded_files.zip", as_attachment=True)
        return str(unique)+'.zip'
    except Exception as e:
        traceback.print_exc()
        raise InvalidUsage(str(e), status_code=400)

@daqbroker.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# @daqbroker.after_request
# def apply_caching(response):
#	response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
#	return response


@daqbroker.route("/collections", methods=['POST'])
@login_required
def collections():
    """ Get or set the available data channel collections

    .. :quickref: Get/Set collection; Get/Set data channel collections

    :param Placeholder : Placeholder parameter, not implemented, will be used create new collections

    :returns: If no parameter is supplied, a list of existing collections is presented. Each collection consists of an object with the following keys:

            | ``Name`` : string containing the address of the NTP server
            | ``channels`` : JSON encoded string containing the channel ID of each channel in the collection
            | ``remarks`` : further remarks regarding the collection (unused)

    """
    connection = connect(request)
    instruments = []
    if connection:
        newCollection = None
        editCollection = None
        if('newCollection' in request.form):
            newCollection = True
        elif('newCollection' in request.args):
            newCollection = True
        else:
            newCollection = False
        if('editCollection' in request.form):
            editCollection = True
        elif('editCollection' in request.args):
            editCollection = True
        else:
            editCollection = False
        if newCollection:
            #print("PUT NEW COLLECTION")

            return jsonify("done")
        elif editCollection:
            #print("EDIT COLLECTION")

            return jsonify("done")
        else:
            collections = []
            result = connection.execute("SELECT * FROM collections")
            for row in result:
                local2 = dict(zip(row.keys(), row))
                collections.append(local2)

            return jsonify(collections)
    else:
        raise InvalidUsage('Error connecting to database', status_code=500)


@daqbroker.route('/checkProcesses', methods=['POST'])
@login_required
def checkProcesses():
    """ Request to check the status of existing database processes. This list of processes is stored in memory. Should be used in conjunction with *actProcess*

    .. :quickref: Get DAQBroker processes; Get currently working DAQBroker subprocesses

    :returns: JSON encoded string containing a list of working DAQBroker subprocesses. Each element of that list will be an object containing the following keys:

            | ``name`` : Name of the process
            | ``pid`` : PID of the process on the server machine
            | ``description`` : Small description of the purpose of the process

    """
    toReturn = []
    for process in multiprocesses:
        temp = process
        try:
            theProcess = psutil.Process(process['pid'])
            temp["alive"] = theProcess.is_running()
        except BaseException:
            temp["alive"] = False
        toReturn.append(temp)
    return jsonify(toReturn)


@daqbroker.route('/getCurrentUser', methods=['POST'])
@login_required
def getCurrentUser():
    """ Request the current user and its type

    .. :quickref: Get current user; Get currently logged in user in the current used server

    :returns: JSON encoded string of currently connected server:

            | ``username`` : Name of the user
            | ``type`` : type of user

    """
    toReturn = []
    for process in multiprocesses:
        temp = process
        try:
            theProcess = psutil.Process(process['pid'])
            temp["alive"] = theProcess.is_running()
        except BaseException:
            temp["alive"] = False
        toReturn.append(temp)
    return jsonify(toReturn)


@daqbroker.route("/checkExpression", methods=['POST'])
@login_required
def checkExpression():
    """ Evaluate the validity of a data manipulation expression

    .. :quickref: Test expression; Test validity of expression

    :param: expression: (String) A string containing properly formatted python code; limitations exist. Refer to PLACEHOLDER for data manipulation options

    :returns: JSON encoded list of unique channel identifiers

    """
    processRequest = request.get_json()
    a = Interpreter(no_for=True, no_while=True, no_print=True, no_delete=True, no_assert=True)
    if "expression" in processRequest:
        # expr=sympify(processRequest["expression"])
        # func=lambdify((),expr)
        # theFunction=Function("ID")# Must update this when I make more expressions
        # theAtoms=list(expr.atoms(theFunction))
        Session = sessionmaker(bind=current_user.engineObj)
        session = Session()
        forbiddenStrings = [
            'connection',
            'os.',
            'sh.',
            'multiprocessing.',
            'sys.']  # Must find more exploitation methods
        for badString in forbiddenStrings:
            if processRequest["expression"].find(badString) >= 0:
                raise InvalidUsage("You are trying to do forbidden things! Please stop", status_code=500)
        funcDeclares = re.findall(r'ID\(\d*\)', processRequest["expression"])
        ids = list(set([int(re.search(r"\d+", x).group()) for x in funcDeclares]))
        gatheredChannels = gatherChannels(ids, session)
        if False in gatheredChannels:
            raise InvalidUsage(
                "A provided channel was not caught, make sure you are using the correct channel IDs an try again",
                status_code=500)
        else:
            toTest = processRequest["expression"]
            for i, channid in enumerate(ids):
                toTest = toTest.replace("ID(" + str(channid) + ")", str(channid))
            a(toTest, show_errors=True)
            if len(a.error) > 0:
                for err in a.error:
                    raise InvalidUsage(err.get_error(), status_code=500)
            return jsonify(gatheredChannels)
    else:
        raise InvalidUsage('Expression not provided', status_code=500)


@daqbroker.route("/queryAdmin", methods=['POST'])
@login_required
def queryAdmin():
    """ Test if the current loged user to the database and engine has DAQBroker administrator privileges

    .. :quickref: Test administrator credentials; Test a connected user for administrator privileges

    :returns: JSON encoded user object

            | ``username`` : (String) unique user name
            | ``type`` : (Integer) type of user. See PLACEOHOLDER for available types

    """
    connection = connect(request)
    resultUser = {}
    if connection:
        resultUser = getUserDetails(current_user.username, connection)
    return jsonify(resultUser)


@daqbroker.route("/serveDists", methods=['POST'])
@login_required
def serveDists():
    """ Provides list of DAQBroker client application binary distributions - used for browser download

    .. :quickref: List available client binaries; Get list provided DAQBroker client application binaries

    :returns: JSON encoded directory structure of the "dists" folder

    """
    dirs = []
    for els in os.walk('dist'):
        filePathList = []
        firstPath = els[0]
        while True:
            temp = os.path.split(firstPath)
            filePathList.insert(0, temp[1])
            if temp[0] == '':
                break
            firstPath = temp[0]
        dirs.append((filePathList, els[1], els[2]))
    return jsonify(dirs)

#@daqbroker.route("/getDataCheck",methods=['POST'])
#@login_required
#def getDataCheck():
    #""" Get status and return data (if applicable) from a supplied job """
    #if 'id' in request.form:
    #    id=request.form['id']
    #elif 'id' in request.args:
    #    id=request.args['id']
    #else:
    #    raise InvalidUsage('No worker ID provided', status_code=500)
    #session=daqbrokerSettings.scoped()
    #thisUser=collector.backupFuncs.getUserDetails(current_user.username,connection)
    # if thisUser['type']==1:
    # jobsTable="jobs"
    # else:
    # jobsTable=current_user.username+"_userview_jobs"
    # result=connection.execute(text("SELECT * FROM "+jobsTable+" WHERE jobid=:jobid"),jobid=id)
    # p=None
    # for row in result:
    # p=dict(zip(row.keys(), row))
    # if p is None:
    # toReturn=-1

    # return jsonify(toReturn)
    # else:
    # if p["status"]==1: #Success! The data should be in p["data"]
    # toReturn=current_app.config['workers'][int(p["data"])]
    # current_app.config['workers'][int(p["data"])]=-1
    # #print(toReturn)
    # #del workers[i]

    # return jsonify(toReturn)
    # elif p["status"]==0: #Gathering still ongoing
    # toReturn=False

    # return jsonify(toReturn)
    # elif p["status"]==-1: #There was a problem with the gathering
    # toReturn=-1
    # workers[int(p["data"])]=-1
    # #del workers[i]

    # return jsonify(toReturn)
    # else: #Something went terribly wrong, getting rid of this, the user can try again
    # #del workers[i]
    # toReturn=-1

    # return jsonify(toReturn)
    # else:
    # raise InvalidUsage('Error connecting to the database', status_code=500)
    # #connection=connect(request)

# @daqbroker.route("/getDataAbort",methods=['POST'])
# @login_required
# def getDataAbort():
    # """ Abort the collection of data from a supplied job """
    # connection=connect(request)
    # if connection:
    # if 'id' in request.form:
    # id=request.form['id']
    # elif 'id' in request.args:
    # id=request.args['id']
    # else:

    # raise InvalidUsage('No worker ID provided', status_code=500)
    # thisUser=collector.backupFuncs.getUserDetails(current_user.username,connection)
    # if thisUser['type']==1:
    # jobsTable="jobs"
    # else:
    # jobsTable=current_user.username+"_userview_jobs"
    # connection.execute(text("DELETE FROM "+jobsTable+" WHERE jobid=:jobid"),jobid=id)
    # else:
    # raise InvalidUsage('Error connecting to database', status_code=500)

    # #print(len(workers))
    # return jsonify('done')


@daqbroker.route("/genLink", methods=['POST'])
@login_required
def genLink():
    """ Create a shareable link of a supplied interface state

    .. :quickref: Create links; Generate a shareable link

    :param: site : (String) endpoint name
    :param: var : (String) JSON encoded state variable

    :returns: (String ) unique shareable link

    """
    Session = sessionmaker(bind=current_user.engineObjSettings)
    session = Session()
    processRequest = request.get_json()
    if 'site' in processRequest:
        site = processRequest['site']
    else:
        raise InvalidUsage('No origin site provided', status_code=500)
    if 'var' in processRequest:
        var = processRequest['var']
    else:

        raise InvalidUsage('No state variable provided', status_code=500)
    try:
        unique = str(uuid.uuid1().hex)[0:20]
        newLink = daqbrokerSettings.links(clock=time.time(),linkid=unique,site=site,variable=json.dumps(var))
        session.add(newLink)
        #dbQuery = text("INSERT into daqbroker_settings.links VALUES (:clock,:uniqueStr,:siteStr,:varStr)")
        #result = connection.execute(dbQuery, clock=time.time() *
        #                            1000, uniqueStr=unique, siteStr=site, varStr=json.dumps(var))
        session.commit()
        return unique
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        raise InvalidUsage(str(e), status_code=500)


@daqbroker.route("/getLink", methods=['POST'])
@login_required
def getLink():
    """ Get the entry associated with a supplied shareable link

    .. :quickref: Get link info; Get shared info from provided link

    :param: link : (String) unique link

    :returns: Logical false if no link was found or timed out. JSON encoded link object with the following keys:

            | ``site`` : (String) endpoint name
            | ``variable`` : (String) JSON encoded state variable

    """
    Session = sessionmaker(bind=current_user.engineObjSettings)
    session = Session()
    processRequest = request.get_json()
    if 'link' in processRequest:
        link = processRequest['link']
    else:
        raise InvalidUsage('No link provided', status_code=400)
    theLinkData = False
    theLink = session.query(daqbrokerSettings.links).filter_by(linkid=link).first()
    if theLink:
        theLinkData = {}
        for field in theLink.__dict__:
            if not field.startswith('_'):
                theLinkData[field] = getattr(theLink, field)
        theLinkData["variable"] = json.loads(theLinkData["variable"])
        return jsonify(theLinkData)
    else:
        raise InvalidUsage("Link not found, make sure you're providing an unexpired link", status_code=500)
    #result = connection.execute(text("SELECT * FROM daqbroker_settings.links WHERE linkid=:theLink"), theLink=link)
    #for row in result:
    #    theLinkData = dict(zip(row.keys(), row))
    #    theLinkData["variable"] = json.loads(theLinkData["variable"])
    #return jsonify(theLinkData)


@daqbroker.route("/getLog", methods=['POST'])
@login_required
@require_onetime_admin
def getLog():
    """ Get the entries of logged events between a specific time interval.

    .. :quickref: Get logged events; Get logged events within time frame

    :param: timeLogStart: (Integer) start timestamp
    :param: timeLogEnd: (Integer) end timestamp


    :returns: List of event entries (strings) inside the requested time interval

    """
    processRequest = request.get_json()
    if not 'timeLogEnd' in processRequest:
        raise InvalidUsage("End time not provided", status_code = 400)
    if not 'timeLogStart' in processRequest:
        raise InvalidUsage("Start time not provided", status_code = 400)
    if not 'reqid' in processRequest:
        raise InvalidUsage("Unique request identifier not provided", status_code = 400)
    unique = str(uuid.uuid1().hex)
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    emptyIndex = next(i for i, val in enumerate(current_app.config['workers']) if val == -1)
    current_app.config['workers'][emptyIndex] = 0
    newJob = daqbrokerSettings.jobs(clock=time.time()*1000, jobid=unique, type=0, username=current_user.username, status=0, data=emptyIndex, reqid=processRequest["reqid"])
    session.add(newJob)
    session.commit()
    daqbrokerSettings.workerpool.submit(getLogEntries, int(processRequest['timeLogStart']), int(
                processRequest['timeLogEnd']), str(unique), current_app.config['workers'], emptyIndex, base_dir)
    return json.dumps({'id': str(unique), 'type': 'log entry'})


@daqbroker.route("/", methods=['GET'])
@login_required
def main():
    session['currentURL'] = url_for('instruments.main')
    return redirect(url_for('instruments.main'))
    # else:
    #	return redirect(url_for('daqbroker.login'))

# @daqbroker.route("/data",methods=['GET'])
# @login_required
# def data():
    # connection=connect(request)
    # session['currentURL']='data'
    # if connection:

    # return render_template('data/main.html')
    # else:
    # return redirect(url_for('daqbroker.login'))

# @daqbroker.route("/monitoring",methods=['GET'])
# @login_required
# def monitoring():
    # connection=connect(request)
    # session['currentURL']='monitoring'
    # if connection:

    # return render_template('monitoring/main.html')
    # else:
    # return redirect(url_for('daqbroker.login'))

# @daqbroker.route("/runs",methods=['GET'])
# @login_required
# def runs():
    # connection=connect(request)
    # session['currentURL']='runs'
    # if connection:

    # return render_template('runs/main.html')
    # else:
    # return redirect(url_for('daqbroker.login'))

# @daqbroker.route("/admin",methods=['GET'])
# @login_required
# def admin():
    # connection=connect(request)
    # session['currentURL']='admin'
    # if connection:
    # engineURL=current_user.engine+'://'+current_user.username+':'+current_user.password+"@"+current_user.server+"/daqbroker_settings"
    # if database_exists(engineURL):
    # thisUser=collector.backupFuncs.getUserDetails(current_user.username,connection)
    # if thisUser['type']==1:

    # return render_template('admin/main.html')
    # else:

    # raise InvalidUsage("This page is not for you, smarty pants", status_code=403)
    # else:
    # return render_template('main.html')
    # else:
    # return redirect(url_for('daqbroker.login'))

# @daqbroker.route("/adminLocal",methods=['GET'])
# @login_required
# def adminLocal():
    # connection=connect(request)
    # session['currentURL']='adminLocal'
    # if connection:
    # engineURL=current_user.engine+'://'+current_user.username+':'+current_user.password+"@"+current_user.server+"/daqbroker_settings"
    # if database_exists(engineURL):
    # thisUser=collector.backupFuncs.getUserDetails(current_user.username,connection)
    # if thisUser['type']==1:

    # return render_template('admin/mainLocal.html')
    # else:

    # raise InvalidUsage("This page is not for you, smarty pants", status_code=403)
    # else:
    # return render_template('main.html')
    # else:
    # return redirect(url_for('daqbroker.login'))


@daqbroker.route("/links/<theLink>", methods=['GET'])
@login_required
def links(theLink):
    connection = connect(request)
    session['currentURL'] = 'links'
    session['currentLink'] = theLink
    if connection:
        session.pop('currentLink')
        return render_template('links.html', data=theLink)
    else:
        return redirect(url_for('login'))


@daqbroker.route("/getLocalServers", methods=['POST'])
@require_CSRF_protect
def getLocalServers():
    """ Get a list of all available database servers to which users have already connected to

    .. :quickref: Get database servers; Get list of database servers to which the machine has made contact

    """
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    serversSelect = []
    for row in session.query(daqbrokerSettings.servers):
        obj = {}
        for field in row.__dict__:
            if not field.startswith('_'):
                obj[field] = getattr(row, field)
        serversSelect.append(obj)
        uri_test = row.engine + "://" + row.server
        if hasattr(current_user, 'conns'):
            for conn in current_user.conns:
                if(conn["id"] == hashlib.sha224(uri_test.encode()).hexdigest()):
                    # print(conn["conn"])
                    if conn["conn"]:
                        serversSelect[-1]["login"] = True
                break
        if "login" not in serversSelect[-1]:
            serversSelect[-1]["login"] = False
    return jsonify(serversSelect)


@daqbroker.route("/discoverSettings", methods=['POST'])
@login_required
def discoverSettings():
    """ Check whether a global settings database exists on supplied database server

    .. :quickref: Get DAQBroker settings; Get global DAQBroker settings

    :returns: JSON encoded list of session server objects with the following keys:

            | ``currentServer`` : (String) server address
            | ``currentEngine`` : (String) server database SQL engine
            | ``settingsExist`` : (Boolean) global settings database exists. Should only return False if a user has logged in for the first time to the engine
            | ``monActive`` : (Boolean) returns True if a server monitoring process is currently underway

    """
    global servers
    try:
        # engineURL=current_user.engine+'://'+current_user.username+':'+current_user.password+"@"+current_user.server+"/daqbroker_settings"
        toReturn = {
            'currentServer': current_user.server,
            'currentEngine': current_user.engine,
            'settingsExist': database_exists(
                current_user.uriSettings),
            'adminExist': False}
        # newEngine=create_engine(engineURL)
        Session = sessionmaker(bind=current_user.engineObjSettings)
        session = Session()
        if database_exists(current_user.uriSettings):
            theUser = session.query(daqbrokerSettings.users).filter_by(username=current_user.username).first()
            foundServer = False
            for i, server in enumerate(current_app.config['servers']):
                temp = server
                #print(theUser)
                if server["server"] == current_user.server and server["engine"] == current_user.engine:
                    toReturn['monActive'] = temp["monActive"]
                    foundServer = True
                    if theUser.type == 1:
                        temp['username'] = current_user.username
                        temp['password'] = current_user.password
                        current_app.config['servers'][i] = temp
                        toReturn['adminExist'] = True
                    else:
                        if server["username"] + server["password"] != "NONENONE":
                            toReturn['adminExist'] = True
                    break

            if not foundServer:
                serversTentative = {
                    'server': current_user.server,
                    'engine': current_user.engine,
                    'username': 'NONE',
                    'password': 'NONE',
                    "monActive": False}
                if theUser.type == 1:
                    serversTentative['username'] = current_user.username
                    serversTentative['password'] = current_user.password
                    serversTentative['monActive'] = True
                    toReturn['adminExist'] = True
                current_app.config['servers'].append({'server': current_user.server,
                                                      'engine': current_user.engine,
                                                      'username': serversTentative['username'],
                                                      'password': serversTentative['password'],
                                                      'monActive': serversTentative['monActive']})
                toReturn['monActive'] = current_app.config['servers'][-1]["monActive"]
            toReturn["username"] = current_user.username
        return jsonify(toReturn)
    except Exception as e:
        traceback.print_exc()
        raise InvalidUsage(str(e), status_code=500)


@daqbroker.route("/checkDatabases", methods=['POST'])
@login_required
@require_CSRF_protect
def checkDatabases():
    """ Get a list of existing DAQBRoker databases in a supplied database engine

    .. :quickref: List databases; List server DAQBroker databases

    :returns: JSON list of database objects. A database object has the following attributes

            | ``dbname`` : (String) name of the database
            | ``active`` : (Boolean) database flagged for instrument monitoring

    """
    engineURL = current_user.engine + '://' + current_user.username + ':' + \
        current_user.password + "@" + current_user.server + "/daqbroker_settings"
    newEngine = create_engine(engineURL)
    Session = sessionmaker(bind=newEngine)
    session = Session()
    resultDBs = []
    result = session.query(daqbrokerSettings.databases)
    for row in result:
        resultDBs.append({'dbname': row.dbname, 'active': row.active})
    return jsonify(resultDBs)

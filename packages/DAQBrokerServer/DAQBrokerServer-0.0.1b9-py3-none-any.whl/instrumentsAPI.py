import time
import traceback
import shutil
import uuid
import os
import json
import zmq
import daqbrokerDatabase
import daqbrokerSettings
from sqlalchemy import text
from sqlalchemy import bindparam
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from flask import Blueprint
from flask import request
from flask import render_template
from flask import session
from flask import jsonify
from flask_login import login_required
from flask_login import current_user
from alembic.migration import MigrationContext
from alembic.operations import Operations
from supportFuncs import *

instrumentsBP = Blueprint('instruments', __name__, template_folder='templates')

base_dir = '.'
if getattr(sys, 'frozen', False):
    base_dir = os.path.join(sys._MEIPASS)

@instrumentsBP.route("/", methods=['GET'])
@login_required
def main():
    session['currentURL'] = url_for('instruments.main')
    return render_template('main.html')


@instrumentsBP.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    if request.method == 'POST':
        return response
    else:
        return render_template("error.html", errorMsg=error.to_dict()["message"], errorNo=error.status_code)


@instrumentsBP.route("/queryInstrumentsFull", methods=['POST'])
@login_required
def queryInstrumentsFull():
    """ List of full instrument information in supplied database and engine

    .. :quickref: All Instrument Details; Get full information from all database instruments

    :returns: A JSON encoded list of basic instrument information. see :func:`queryInstDetails` for single object
    description

    """
    instruments = []
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    result = session.query(daqbrokerDatabase.instruments)
    for row in result:
        # print(row.toJSONSimple())
        theObjct = {}
        for field in row.__dict__:
            if not field.startswith('_'):
                theObjct[field] = getattr(row, field)
        # instruments.append(json.dumps(row,cls=AlchemyEncoder))
        instruments.append(theObjct)
        if instruments[-1]["log"]:
            instruments[-1]["log"] = json.loads(instruments[-1]["log"])
        else:
            instruments[-1]["log"] = []
        instruments[-1]["files"] = []
        for source in row.sources:
            theObjct2 = {}
            for field in source.__dict__:
                if not field.startswith('_'):
                    theObjct2[field] = getattr(source, field)
            instruments[-1]["files"].append(theObjct2)
            instruments[-1]["files"][-1]["remarks"] = json.loads(instruments[-1]["files"][-1]["remarks"])
            instruments[-1]["files"][-1]["channels"] = []
            instruments[-1]["files"][-1]["parsing"] = []
            for channel in source.channels:
                theObjct3 = {}
                for field in channel.__dict__:
                    if not field.startswith('_'):
                        theObjct3[field] = getattr(channel, field)
                instruments[-1]["files"][-1]["channels"].append(theObjct3)
                instruments[-1]["files"][-1]["channels"][-1]["remarks"] = json.loads(
                    instruments[-1]["files"][-1]["channels"][-1]["remarks"])
            for parse in source.parsing:
                theObjct3 = {}
                for field in parse.__dict__:
                    if not field.startswith('_'):
                        theObjct3[field] = getattr(parse, field)
                instruments[-1]["files"][-1]["parsing"].append(theObjct3)
                instruments[-1]["files"][-1]["parsing"][-1]["remarks"] = json.loads(instruments[-1]["files"][-1]["parsing"][-1]["remarks"])
        instruments[-1]["clockCounts"] = 0
        instruments[-1]["clockCountsCustom"] = 0
    return jsonify(instruments)


@instrumentsBP.route("/queryInstruments", methods=['POST'])
@login_required
def queryInstruments():
    """ List basic instrument information in supplied database and engine

    .. :quickref: Basic Instrument Details; Get basic information from all database instruments

    :returns: A JSON encoded list containing basic information of each instrument in a database as an object with the
    following keys :

            | ``Name`` : String the unique name of the instrument
            | ``instid`` : Integer containing a unique identifier of the instrument
            | ``active`` : Boolean containing the monitoring state of the instrument
            | ``description`` : String containing a description of the instrument, if supplied
            | ``username`` : String containing the username associated with the instrument
            | ``email`` : String containing the contact information (email, phone) of the person responsible of the
            instrument, if supplied
            | ``insttype`` : Integer containing the type of instrument (unused)
            | ``log`` : JSON encoded string of entries in a virtual instrument log book

    """
    instruments = []
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    result = session.query(daqbrokerDatabase.instruments)
    for row in result:
        # print(row.toJSONSimple())
        theObjct = {}
        for field in row.__dict__:
            if not field.startswith('_'):
                theObjct[field] = getattr(row, field)
        # instruments.append(json.dumps(row,cls=AlchemyEncoder))
        instruments.append(theObjct)
        if instruments[-1]["log"]:
            instruments[-1]["log"] = json.loads(instruments[-1]["log"])
        else:
            instruments[-1]["log"] = []
        instruments[-1]["clockCounts"] = 0
        instruments[-1]["clockCountsCustom"] = 0
    return jsonify(instruments)


@instrumentsBP.route("/queryInstDetails", methods=['POST'])
@login_required
def queryInstDetails():
    """ Get full instrument information on a specified instrument from a specified database

    .. :quickref: Instrument Details; Get Full information from single instrument

    :param: instid : (Integer) unique instrument identifier

    :returns: A JSON encoded object with full instrument information

            | ``Name`` : String the unique name of the instrument
            | ``instid`` : Integer containing a unique identifier of the instrument
            | ``active`` : Boolean containing the monitoring state of the instrument
            | ``description`` : String containing a description of the instrument, if supplied
            | ``username`` : String containing the username associated with the instrument
            | ``email`` : String containing the contact information (email, phone) of the person responsible of the
            instrument, if supplied
            | ``insttype`` : Integer containing the type of instrument (unused)
            | ``log`` : JSON encoded string of entries in a virtual instrument log book
            | ``files`` : List of instrument data source objects and their status:

                    | ``clock`` : (Integer) timestamp of the last edit to the source information
                    | ``name`` : (String) name of the data source
                    | ``metaid`` : (Integer) unique instrument data source identifier
                    | ``instid`` : (Integer) unique instrument identifier
                    | ``type`` : (Integer) type of data source :

                            | ``0`` : file(s)
                            | ``1`` : serial port
                            | ``2`` : network port
                            | ``3`` : user-supplied file

                    | ``node`` : (String) unique ID of a machine running a DAQBroker client
                    | ``remarks`` : (String) JSON encoded object with information of the data source
                    | ``sentRequest`` : (Boolean) request is being processed by a client machine
                    | ``lastAction`` : (Integer) timestamp of last automated monitoring action on source
                    | ``lasterrortime`` : (Integer) last timestamp of error collection (unused)
                    | ``lasterror`` : (String) last collected error (unused)
                    | ``lockSync`` : (Boolean) data source is set to not backup data
                    | ``channels`` : (List) objects containing definition of a data source's individual data channels:

                            | ``Name`` : (String) data channel name
                            | ``channelid`` : (Integer) unique channel identifier
                            | ``channeltype`` : (Integer) channel type

                                    | ``0`` : Number
                                    | ``1`` : Text
                                    | ``2`` : Custom

                            | ``valuetype`` : (Integer) NASA processing level
                            | ``units`` : (String) physical units
                            | ``instid`` : (Integer) unique instrument identifier
                            | ``description`` : (String) channel description
                            | ``active`` : (Boolean) accessible for all users
                            | ``remarks`` : (String) JSON encoded extra information
                            | ``metaid`` : (Integer) unique instrument data source identifier
                            | ``lastclock`` : (Integer) latest stored timestamp
                            | ``lastValue`` : (Double) value at latest stored timestamp
                            | ``fileorder`` : (Integer) order on file (used for source type 0)
                            | ``alias`` : (String) original name (kept when channel name changes)
                            | ``firstClock`` : (Integer) lowest stored timestamp

                    | ``parsing`` : (List) objects containing definition of a source's status of data collection. Each
                     object contains the following keys

                            | ``clock`` : (Integer) entry creation timestamp
                            | ``lastAction`` : (Integer) latest action timestamp
                            | ``metaid`` : (Integer) unique instrument data source identifier
                            | ``instid`` : (Integer) unique instrument identifier
                            | ``type`` : (Integer) same as ``files - type``
                            | ``locked`` : (Boolean) automated parsing underway
                            | ``forcelock`` : (Boolean) parsing locked by user
                            | ``remarks`` : (Integer) extra information

    """
    if('instid' in request.form):
        instid = request.form['instid']
    elif('instid' in request.args):
        instid = request.args['instid']
    else:
        raise InvalidUsage('No instrument ID provided', status_code=500)
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    theInstrument = session.query(daqbrokerDatabase.instruments).filter_by(instid=instid).first()
    #theInstrument.sources.sort(key = lambda x: x.metaid)
    instrument = {}
    for field in theInstrument.__dict__:
        if not field.startswith('_'):
            instrument[field] = getattr(theInstrument, field)
    # instruments.append(json.dumps(row,cls=AlchemyEncoder))
    instrument["files"] = []
    if instrument["log"]:
        instrument["log"] = json.loads(instrument["log"])
    else:
        instrument["log"] = []
    for source in theInstrument.sources:
        #source.channels.sort(key = lambda x : x.channelid)
        theObjct2 = {}
        for field in source.__dict__:
            if not field.startswith('_'):
                theObjct2[field] = getattr(source, field)
        instrument["files"].append(theObjct2)
        instrument["files"][-1]["remarks"] = json.loads(instrument["files"][-1]["remarks"])
        instrument["files"][-1]["channels"] = []
        instrument["files"][-1]["parsing"] = []
        for channel in source.channels:
            theObjct3 = {}
            for field in channel.__dict__:
                if not field.startswith('_'):
                    theObjct3[field] = getattr(channel, field)
            instrument["files"][-1]["channels"].append(theObjct3)
            instrument["files"][-1]["channels"][-1]["remarks"] = json.loads(
                instrument["files"][-1]["channels"][-1]["remarks"])
        for parse in source.parsing:
            theObjct3 = {}
            for field in parse.__dict__:
                if not field.startswith('_'):
                    theObjct3[field] = getattr(parse, field)
            instrument["files"][-1]["parsing"].append(theObjct3)
            instrument["files"][-1]["parsing"][-1]["remarks"] = json.loads(
                instrument["files"][-1]["parsing"][-1]["remarks"])
    return jsonify(instrument)


@instrumentsBP.route("/queryInstCreds", methods=['POST'])
@login_required
def queryInstCreds():
    """ Check if the provided credentials allow an instrument to be edited. Only the instrument creator and the system
    administrators can edit instruments

    .. :quickref: Test credentials; Test current credentials for instrument editing

    :param: instid: (Integer) unique instrument identifier

    :returns: A JSON encoded object with credential test results

            | ``username`` : (String) current username
            | ``type`` : (Integer) user type see PLACEHOLDER FOR AVAILABLE TYPES
            | ``error`` : (Boolean) if instrument belongs to user or not

    """
    returned = {'error': 0}
    if('instid' in request.form):
        instid = request.form['instid']
    elif('instid' in request.args):
        instid = request.args['instid']
    else:
        raise InvalidUsage('No instrument ID provided', status_code=500)
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    theInstrument = session.query(daqbrokerDatabase.instruments).filter_by(instid=instid).first()
    SessionSettings = sessionmaker(bind=current_user.engineObjSettings)
    sessionSettings = SessionSettings()
    theUser = sessionSettings.query(daqbrokerSettings.users).filter_by(username=current_user.username).first()
    returned["type"] = theUser.type
    if not theUser.type == 1:
        if theUser.username == theInstrument.username:
            returned['type'] = theUser.type
        else:
            returned['type'] = -1
    return jsonify(returned)


@instrumentsBP.route("/deleteChannel", methods=['POST'])
@login_required
@require_onetime_admin
def deleteChannel():
    """ Delete an instrument's data channel along with its data. Only instrument owners and system administrators can
    delete data channels

    .. :quickref: Delete data channel; Deletes an instrument data channel and its data

    :param: channelid: (Integer) unique instrument data channel identifier

    """
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    if('channelid' in request.form):
        channelid = request.form['channelid']
    elif('channelid' in request.args):
        channelid = request.args['channelid']
    else:
        raise InvalidUsage('No channel ID provided', status_code=500)
    try:
        result = session.query(daqbrokerDatabase.channels).filter_by(channelid=channelid).first()
        if current_user.type != 1:
            if result.chann.meta.username != current_user.username:
                raise InvalidUsage("You are not the instrument operator", status_code=400)
        session.delete(result)
        conn = current_user.engineObj.connect()
        ctx = MigrationContext.configure(conn)
        op = Operations(ctx)
        if result.channeltype == 1 or result.channeltype == 2:
            op.drop_column(result.chann.meta.Name + "_data", result.Name)
        else:
            op.drop_column(result.chann.meta.Name + "_custom", result.Name)
        conn.close()
        session.commit()
        return jsonify('done')
    except Exception as e:
        session.rollback()
        raise InvalidUsage('Error : ' + str(e), status_code=500)


@instrumentsBP.route("/setActiveInstrument", methods=['POST'])
@login_required
@require_onetime_admin
def setActiveInstrument():
    """ Toggles the current active monitoring state of an instrument

    .. :quickref: Toggle active state; Toggles an instrument on or off to be monitored

    :param: instid : (Integer) unique instrument identifier. Used to edit an existing instrument

    :returns: (Boolean) The resulting new monitoring state of the instrument
    """
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    if('instid' in request.form):
        instid = request.form['instid']
    elif('instid' in request.args):
        instid = request.args['instid']
    else:
        raise InvalidUsage('No instrument ID provided', status_code=500)
    try:
        theInstrument = session.query(daqbrokerDatabase.instruments).filter_by(instid=instid).first()
        if current_user.type != 1:
            if theInstrument.username != current_user.username:
                raise InvalidUsage("You are not this instrument's operator", status_code=400)
        theInstrument.active = not theInstrument.active
        session.commit()
        return jsonify(theInstrument.active)
    except Exception as e:
        session.rollback()
        raise InvalidUsage(str(e), status_code=400)


@instrumentsBP.route("/deleteInstrument", methods=['POST'])
@login_required
@require_onetime_admin
def deleteInstrument():
    """ Delete an instrument and its data. Only instrument owners and instrument administrators are allowed to delete
    instruments

    .. :quickref: Delete instrument; Deletes an instrument and its data

    :param: instid: (Integer) unique instrument identifier

    """
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    if request.is_json:
        requestCheck = request.get_json()
    else:
        requestCheck = request.form
    if 'instid' in requestCheck:
        instid = requestCheck['instid']
    else:
        raise InvalidUsage('No instrument ID provided', status_code=400)
    try:
        theInstrument = session.query(daqbrokerDatabase.instruments).filter_by(instid=instid).first()
        if current_user.type != 1:
            if theInstrument.username != current_user.username:
                raise InvalidUsage("You are not this instrument's operator", status_code=400)
        BACKUPPATH = ''
        IMPORTPATH = ''
        ADDONPATH = ''
        context = zmq.Context()
        newPaths = checkPaths(context, BACKUPPATH, IMPORTPATH, ADDONPATH, 15000)
        paths = {"BACKUPPATH": newPaths[0], "IMPORTPATH": newPaths[1], "ADDONPATH": newPaths[2]}
        pathDel = os.path.join(paths["BACKUPPATH"], current_user.server,
                               current_user.database, theInstrument.Name)
        try:
            shutil.rmtree(pathDel)
        except BaseException:
            traceback.print_exc()
        tablesDrop = []
        tablesDropKeys = []
        for table in daqbrokerDatabase.daqbroker_database.metadata.tables.keys():
            if table == theInstrument.Name + '_data' or table == theInstrument.Name + '_custom':
                tablesDrop.append(daqbrokerDatabase.daqbroker_database.metadata.tables[table])
                tablesDropKeys.append(table)
        daqbrokerDatabase.daqbroker_database.metadata.drop_all(current_user.engineObj, tables=tablesDrop)
        for table in tablesDropKeys:
            daqbrokerDatabase.daqbroker_database.metadata.remove(
                daqbrokerDatabase.daqbroker_database.metadata.tables[table])
        session.delete(theInstrument)
        session.commit()
        return jsonify('done')
    except Exception as e:
        session.rollback()
        raise InvalidUsage(str(e), status_code=400)


@instrumentsBP.route("/insertInstrument", methods=['POST'])
@login_required
@require_onetime_admin
def insertInstrument():
    """ Insert a new instrument or edit an existing instrument on a DAQBroker database. Guest users are not allowed to
    create instruments. Created instruments are

    .. :quickref: Create/Edit instrument; Creates or edits a DAQBroker instrument instrument

    :param: Name : (String) unique instrument name
    :param: instid : (Integer) unique instrument identifier. Used to edit an existing instrument
    :param: description : (String) description of the instrument and its
    :param: email : (String) contact information for the instrument operator
    :param: Files : (Optional) JSON encoded list of instrument data source objects. Each Contains the following keys:

            | ``name`` : (String) name of the data source
            | ``metaid`` : (Integer) unique data source identifier. Only used to edit existing data sources
            | ``type`` : (Integer) type of instrument data source
            | ``node`` : (String) unique network node identifier
            | ``remarks`` : (String) JSON encoded object of extra data source information
            | ``channels`` : (Optional) JSON encoded list of data channel objects. Each contains the following keys:

                    | ``Name`` : (String) data channel name
                    | ``channelid`` : (Integer) unique channel identifier. -1 if the channel is new. Positive integer
                    if the channel already exists
                    | ``description`` : (String) data channel description
                    | ``units`` : (String) data channel physical units
                    | ``channeltype`` : (Integer) type of data channel

                            | ``0`` : Number
                            | ``1`` : Text
                            | ``2`` : Custom

                    | ``active`` : (Boolean) channel is shown on interface
                    | ``fileorder`` : (Integer) Used to order channels in a data source
                    | ``alias`` : (String) Original data channel name. Kept constant when name changes
                    | ``remarks`` : (String) JSON encoded object with extra information
                    | ``oldname`` : (String) Old channel name. Used to detect changes in the channel name
                    | ``channeltypeOld`` : (Integer) Old channel type. Used to detect changes in the channel type

    """
    processRequest = request.get_json()
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    conn = current_user.engineObj.connect()
    ctx = MigrationContext.configure(conn)
    op = Operations(ctx)
    try:
        if 'instid' in processRequest:
            newInst = False
            instid = processRequest['instid']
            instrument = session.query(daqbrokerDatabase.instruments).filter_by(instid=instid).first()
        else:
            newInst = True
            maxInst = session.query(func.max(daqbrokerDatabase.instruments.instid)).one_or_none()
            # print(maxInst==None)
            if maxInst[0]:
                maxInstid = maxInst[0]
            else:
                maxInstid = 0
            instid = maxInstid + 1
            instrument = daqbrokerDatabase.instruments(
                Name=processRequest['Name'],
                instid=instid,
                active=False,
                description=processRequest['description'],
                username=current_user.username,
                email=processRequest['email'],
                insttype=0,
                log=None)
        # Now I have an object called "instrument" that I can use to add sources
        # and metadatas and to those metadatas I should be able to add channels.
        for file in processRequest['files']:
            if 'metaid' in file:
                metadata = session.query(daqbrokerDatabase.instmeta).filter_by(metaid=file["metaid"]).first()
                metadata.clock = time.time() * 1000
                metadata.name= file['name']
                metadata.type=file['type']
                metadata.node=file['node']
                metadata.remarks=json.dumps(file['remarks'])
            else:
                maxMeta = session.query(func.max(daqbrokerDatabase.instmeta.metaid)).first()
                if maxMeta[0]:
                    maxMetaid = maxMeta[0]
                else:
                    maxMetaid = 0
                metaid = maxMetaid + 1
                metadata = daqbrokerDatabase.instmeta(
                    clock=time.time() * 1000,
                    name=file['name'],
                    metaid=metaid,
                    type=file["type"],
                    node=file["node"],
                    remarks=json.dumps(
                        file['remarks']),
                    sentRequest=False,
                    lastAction=0,
                    lasterrortime=0,
                    lasterror='',
                    lockSync=False)
                instrument.sources.append(metadata)
            channelid = None
            if 'channels' in file:
                channelsInsert = []
                for channel in file['channels']:
                    if int(channel['channelid']) < 0:  # New channel - have to insert
                        maxChannel = session.query(func.max(daqbrokerDatabase.channels.channelid)).first()
                        if not channelid:
                            if maxChannel[0]:
                                maxChannelid = maxChannel[0]
                            else:
                                maxChannelid = 0
                            channelid = maxChannelid + 1
                        else:
                            channelid = channelid + 1
                        if 'remarks' in channel:
                            if len(channel["remarks"].keys())>0:
                                theRemarks = json.dumps(channel["remarks"])
                            else:
                                theRemarks = json.dumps({})
                        else:
                            theRemarks = json.dumps({})
                        theChannel = daqbrokerDatabase.channels(
                            Name=channel["Name"],
                            channelid=channelid,
                            channeltype=int(
                                channel["channeltype"]),
                            valuetype=0,
                            units=channel['units'],
                            description=channel['description'],
                            active=int(
                                channel['active']) == 1,
                            remarks=theRemarks,
                            lastclock=0,
                            lastValue=None,
                            firstClock=0,
                            fileorder=channel['fileorder'],
                            alias=channel['alias'])
                        metadata.channels.append(theChannel)
                        channelsInsert.append({'name': channel["Name"], 'type': int(channel["channeltype"])})
                        if not newInst:
                            extra = ''
                            if int(channel['channeltype']) == 1:
                                newType = daqbrokerDatabase.Float
                                extra = "\"" + channel["Name"] + "\"::double precision"
                                column = daqbrokerDatabase.Column(channel["Name"], newType)
                                op.add_column(processRequest['Name'] + "_data", column)
                            elif int(channel['channeltype']) == 2:
                                newType = daqbrokerDatabase.Text
                                column = daqbrokerDatabase.Column(channel["Name"], newType)
                                op.add_column(processRequest['Name'] + "_data", column)
                            elif int(channel['channeltype']) == 3:
                                extra = "\"" + channel["Name"] + "\"::double precision"
                                theType = daqbrokerDatabase.Float
                                column = daqbrokerDatabase.Column(channel["Name"], newType)
                                op.add_column(processRequest['Name'] + "_custom", column)
                    elif not newInst:
                        theChannel = session.query(
                            daqbrokerDatabase.channels).filter_by(
                            channelid=channel['channelid']).first()
                        theChannel.Name = channel["Name"]
                        theChannel.channeltype = int(channel["channeltype"])
                        theChannel.units = channel['units']
                        theChannel.description = channel['description']
                        theChannel.active = int(channel['active']) == 1
                        theChannel.fileorder = channel['fileorder']
                        theChannel.alias = channel['alias']
                        if (not channel['channeltypeOld'] == channel['channeltype']) or (
                                not channel['oldName'] == str(channel['Name'])):
                            if not channel['oldName'] == str(channel['Name']):
                                newName = str(channel['Name'])
                                oldName = channel['oldName']
                            else:
                                oldName = str(channel['Name'])
                                newName = None
                            if not channel['channeltypeOld'] == channel['channeltype']:
                                if channel['channeltype'] == 1 or channel['channeltype'] == 3:
                                    newType = daqbrokerDatabase.Float
                                    extra = "\"" + oldName + "\"::double precision"
                                else:
                                    newType = daqbrokerDatabase.Text
                                    extra = None
                            else:
                               newType = None
                            if not channel['channeltypeOld'] == channel['channeltype'] and channel['channeltype'] == 3:
                                if not newName:
                                    theName = oldName
                                else:
                                    theName = newName
                                if not newType:
                                    theType = daqbrokerDatabase.Float
                                else:
                                    theType = newType
                                column = daqbrokerDatabase.Column(theName, theType)
                                op.drop_column(processRequest['Name'] + "_data", oldName)
                                op.add_column(processRequest['Name'] + "_custom", column)
                            elif not channel['channeltypeOld'] == channel['channeltype'] and channel['channeltypeOld'] != 3:
                                if not newName:
                                    theName = oldName
                                else:
                                    theName = newName
                                if not newType:
                                    if channel['channeltypeOld'] == 1:
                                        theType = daqbrokerDatabase.Float
                                    else:
                                        theType = daqbrokerDatabase.Text
                                else:
                                    theType = newType
                                column = daqbrokerDatabase.Column(theName, theType)
                                op.drop_column(processRequest['Name'] + "_custom", oldName)
                                op.add_column(processRequest['Name'] + "_data", column)
                            else:
                                if channel['channeltype'] == 1 or channel['channeltype'] == 2:
                                    if extra:
                                        op.alter_column(
                                            processRequest['Name'] + "_data",
                                            oldName,
                                            new_column_name=newName,
                                            type_=newType,
                                            postgresql_using=extra)
                                    else:
                                        op.alter_column(
                                            processRequest['Name'] + "_data", oldName, new_column_name=newName, type_=newType)
                                else:
                                    if extra=='':
                                        op.alter_column(
                                            processRequest['Name'] + "_custom", oldName, new_column_name=newName, type_=newType)
                                    else:
                                        op.alter_column(
                                            processRequest['Name'] + "_data",
                                            oldName,
                                            new_column_name=newName,
                                            type_=newType,
                                            postgresql_using=extra)
                    elif newInst:
                        raise InvalidUsage("Cannot issue edit channels on new instrument", status_code=401)
        if newInst:
            daqbrokerDatabase.createInstrumentTable(processRequest['Name'], channelsInsert, True)
            session.add(instrument)
            daqbrokerDatabase.daqbroker_database.metadata.create_all(current_user.engineObj)
        session.commit()
        conn.close()
        current_user.updateDB()
        return jsonify('done')
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        # for statement in deleteStatements:
        #	connection.execute(statement)
        raise InvalidUsage(str(e), status_code=500)


@instrumentsBP.route("/editLogEntry", methods=['POST'])
@login_required
@require_onetime_admin
def editLogEntry():
    """ Edit an entry from an instrument virtual log book

    .. :quickref: Edit virtual log; Edit entry of an instrument's virtual log

    :param: instid: (integer) unique instrument identifier
    :param: entry: object containing the following keys:

            | ``oldDate`` : (Integer) original entry timestamp
            | ``date`` : (Integer) New entry timestamp (if same as ``oldDAte`` date doesn't change)
            | ``author`` : (String) Entry author
            | ``entry`` : (String) Entry text

    :param: operation: (string) operation to be preformed in **entry**

            | ``edit`` : Edit entry
            | ``remove`` : Remove entry

    """
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    processRequest = request.get_json()
    if('instid' in processRequest):
        instid = processRequest['instid']
    elif('instid' in processRequest):
        instid = processRequest['instid']
    else:

        raise InvalidUsage('No instrument ID provided', status_code=500)
    if('entry' in processRequest):
        entry = processRequest['entry']
    elif('entry' in processRequest):
        entry = processRequest['entry']
    else:

        raise InvalidUsage('No log entry provided', status_code=500)
    if('operation' in processRequest):
        operation = processRequest['operation']
    elif('operation' in processRequest):
        operation = processRequest['operation']
    else:

        raise InvalidUsage('No operation provided', status_code=500)
    try:
        theInst = session.query(daqbrokerDatabase.instruments).filter_by(instid=instid).first()
        if theInst.log:
            log = json.loads(theInst.log)
        else:
            log = []
        foundEntry = False
        for i, anEntry in enumerate(log):
            if anEntry['date'] == entry['oldDate']:
                foundEntry = True
                break
        if foundEntry:
            if operation == 'remove':
                del log[i]
            elif operation == 'edit':
                log[i]['date'] = entry['date']
                log[i]['author'] = entry['author']
                log[i]['entry'] = entry['entry']
            else:
                raise InvalidUsage('Unrecognized operation requested', status_code=500)
        else:

            raise InvalidUsage('Could not find requested entry', status_code=500)
        theInst.log = json.dumps(log)
        session.commit()
    except Exception as e:

        traceback.print_exc()
        raise InvalidUsage('Error : ' + str(e), status_code=500)

    return jsonify('done')


@instrumentsBP.route("/insertLogComment", methods=['POST'])
@login_required
@require_onetime_admin
def insertLogComment():
    """ Add an entry into an instrument's virtual log book

    .. :quickref: Add virtual log entry; Add an entry to an instrument's virtual log

    :param: instid: (integer) unique instrument identifier
    :param: entry: object containing the following keys:

            | ``date`` : (Integer) New entry timestamp (if same as ``oldDAte`` date doesn't change)
            | ``author`` : (String) Entry author
            | ``entry`` : (String) Entry text

    """
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    if('instid' in request.form):
        instid = request.form['instid']
    elif('instid' in request.args):
        instid = request.args['instid']
    else:
        raise InvalidUsage('No instrument ID provided', status_code=400)
    if('entry' in request.form):
        entry = request.form['entry']
    elif('entry' in request.args):
        entry = request.args['entry']
    else:
        raise InvalidUsage('No log entry provided', status_code=400)
    if('date' in request.form):
        date = request.form['date']
    elif('date' in request.args):
        date = request.args['date']
    else:
        raise InvalidUsage('No date provided', status_code=400)
    if('author' in request.form):
        author = request.form['author']
    elif('author' in request.args):
        author = request.args['author']
    else:
        raise InvalidUsage('No author provided', status_code=400)
    try:
        theInst = session.query(daqbrokerDatabase.instruments).filter_by(instid=instid).first()
        if theInst.log:
            log = json.loads(theInst.log)
        else:
            log = []
        log.append({'entry': entry, 'date': date, 'author': author})
        theInst.log = json.dumps(log)
        session.commit()
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        raise InvalidUsage('Error : ' + str(e), status_code=500)

    return jsonify('done')


@instrumentsBP.route("/editParsing", methods=['POST'])
@login_required
@require_onetime_admin
def resetParsing():
    """ Edit the existing parsing information of an instrument

    .. :quickref: Edit data source; Edit data source action information

    :param: instid: (integer) unique instrument identifier
    :param: metaid: (integer) unique instrument data source identifier
    :param: sourceResetTime: (integer) number of seconds to reset the parsing information
    :param: operation: (string) operation to be preformed

            | ``remove`` : Remove data source and associated data
            | ``reset`` : Reset processing information
            | ``lockP`` : Toggle lock data storage methods
            | ``lockB`` : Toggle lock file backup methods

    """
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    conn = current_user.engineObj.connect()
    ctx = MigrationContext.configure(conn)
    op = Operations(ctx)
    if('instid' in request.form):
        instid = request.form['instid']
    elif('instid' in request.args):
        instid = request.args['instid']
    else:
        raise InvalidUsage('No instrument ID provided', status_code=500)
    if('metaid' in request.form):
        metaid = request.form['metaid']
    elif('metaid' in request.args):
        metaid = request.args['metaid']
    else:

        raise InvalidUsage('No metadata ID provided', status_code=500)
    if('operation' in request.form):
        operation = request.form['operation']
    elif('operation' in request.args):
        operation = request.args['operation']
    else:
        raise InvalidUsage('No operation provided', status_code=500)
    instrument = []
    try:
        theMeta = session.query(daqbrokerDatabase.instmeta).filter_by(metaid=metaid).first()
        if operation == "remove":
            BACKUPPATH = ''
            IMPORTPATH = ''
            ADDONPATH = ''
            context = zmq.Context()
            newPaths = checkPaths(context, BACKUPPATH, IMPORTPATH, ADDONPATH, 15000)
            paths = {"BACKUPPATH": newPaths[0], "IMPORTPATH": newPaths[1], "ADDONPATH": newPaths[2]}
            pathDel = os.path.join(paths["BACKUPPATH"], current_user.server,
                                   current_user.database[7:], theMeta.meta.Name, theMeta.name)
            try:
                shutil.rmtree(pathDel)
            except BaseException:
                traceback.print_exc()
                poop = "poop"
            session.delete(theMeta)
            for channel in theMeta.channels:
                if channel.channeltype == 3:
                    op.drop_column(theMeta.meta.Name + "_custom", channel.Name)
                else:
                    op.drop_column(theMeta.meta.Name + "_data", channel.Name)
            daqbrokerDatabase.daqbroker_database.metadata.remove(
                daqbrokerDatabase.daqbroker_database.metadata.tables[theMeta.meta.Name + "_custom"])
            daqbrokerDatabase.daqbroker_database.metadata.remove(
                daqbrokerDatabase.daqbroker_database.metadata.tables[theMeta.meta.Name + "_data"])
            daqbrokerDatabase.daqbroker_database.metadata.reflect(current_user.engineObj, extend_existing=True)
        elif operation == 'reset':
            if('sourceResetTime' in request.form):
                sourceResetTime = int(request.form['sourceResetTime'])
            elif('sourceResetTime' in request.args):
                sourceResetTime = int(request.args['sourceResetTime'])
            else:
                sourceResetTime = 1000000000000000000000
            if sourceResetTime <= 0:
                sourceResetTime = 1000000000000000000000
            #print(theMeta.metaid, sourceResetTime)
            theParsing = theMeta.parsing
            for parsing in theParsing:
                if parsing.remarks:
                    theFiles = json.loads(parsing.remarks)
                    theFiles = [x for x in theFiles if (time.time() * 1000 - float(x["lastTime"]) >= sourceResetTime)]
                    parsing.remarks = json.dumps(theFiles)
            #print(theFiles)
        elif operation == 'lockP':
            theMeta.parsing.forcelock = not theMeta.parsing.forcelock
        elif operation == 'lockB':
            theMeta.parsing.sentRequest = not theMeta.parsing.lockSync
            theMeta.parsing.lockSync = not theMeta.parsing.lockSync
        else:
            raise InvalidUsage('Wrong operation provided', status_code=500)
        session.commit()
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        raise InvalidUsage('Error : ' + str(e), status_code=500)
    conn.close()
    return jsonify('done')


@instrumentsBP.route("/changeInstOp", methods=['POST'])
@login_required
def changeInstOp():
    """ Alter an existing instrument's operator. This action can only be preformed by a system administrator

    .. :quickref: Alter instrument's user; Alter an instrument's operator user

    :param: newUsername : (String) new instrument username
    :param: instid : (Integer) unique instrument identifier

    """
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    if('instid' in request.form):
        instid = request.form['instid']
    elif('instid' in request.args):
        instid = request.args['instid']
    else:

        raise InvalidUsage('No instrument ID provided', status_code=500)
    if('newUsername' in request.form):
        operation = request.form['newUsername']
    elif('newUsername' in request.args):
        operation = request.args['newUsername']
    else:
        raise InvalidUsage('No new username provided', status_code=500)
    try:
        theInst = session.query(daqbrokerDatabase.instruments).filter_by(instid=instid).first()
        theInst.username = operation
        session.commit()
    except Exception as e:
        session.rollback()
        raise InvalidUsage('Error : ' + str(e), status_code=500)
    return jsonify('done')


@instrumentsBP.route("/getInstLimits", methods=['POST'])
@login_required
def getInstLimits():
    """ Get largest and smallest stored time stamps

    .. :quickref: Get time limits; Get database largest and shortest stored timestamp

    :returns: JSON encoded object with the following keys:

            | ``max`` : (Integer) largest timestamp
            | ``min`` : (Integer) smallest timestamp

    """
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    processRequest = request.get_json()
    maxChann = session.query(
        func.max(daqbrokerDatabase.channels.lastclock)).first()
    minChann = session.query(
        func.min(daqbrokerDatabase.channels.firstClock)).first()
    if maxChann[0] is None:
        maxTime = time.time() * 1000
    else:
        maxTime = maxChann[0]
    if minChann[0] is None:
        minTime = time.time() * 1000 - 60000
    else:
        minTime = minChann[0]
    timesFinal = {'max': maxTime, 'min': minTime}
    return jsonify(timesFinal)


@instrumentsBP.route('/listInstFiles', methods=['POST'])
@login_required
def listInstFiles():
    """ Request to list an instrument's current data file structure

    .. :quickref: Get instrument files; Get instrument's stored data files

    :param instName: Name of the requested instrument

    :returns: JSON encoded string containing the collected file structure of the requested instrument.

    """
    #localConn = sqlite3.connect('localSettings')
    #localConn.row_factory = dict_factory
    #session=daqbrokerSettings.scoped()
    # dbQuery = "SELECT * FROM global a INNER JOIN (SELECT max(clock) clock FROM global) b ON a.clock=b.clock"
    # result = localConn.execute(dbQuery)
    # for row in result:
    #     globals = row
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
            globals["remarks"]=json.loads(globals["remarks"])
    else:
        globals = {
            'clock': time.time(),
            'version': '0.1',
            'backupfolder': 'backups',
            'importfolder': 'uploads',
            'tempfolder': 'addons',
            'ntp': None,
            'commport': 9090,
            'logport': 9092,
            'remarks': {}}
    if('instName' in request.form):
        instName = request.form["instName"]
    elif('instName' in request.args):
        instName = request.args["instName"]
    else:
        localConn.close()
        raise InvalidUsage('No instrument name supplied', status_code=400)
    folder = os.path.join(globals["backupfolder"], current_user.server, current_user.database, instName)
    dirs = get_directory_structure(folder)
    return jsonify(dirs)

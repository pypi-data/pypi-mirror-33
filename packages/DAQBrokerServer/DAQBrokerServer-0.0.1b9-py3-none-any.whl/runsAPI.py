import time
import json
import traceback
import sqlite3
import daqbrokerDatabase
import daqbrokerSettings
from sqlalchemy import text
from sqlalchemy import bindparam
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from flask import Blueprint
from flask import request
from flask import render_template
from flask import session
from flask import jsonify
from flask_login import login_required
from alembic.migration import MigrationContext
from alembic.operations import Operations
from supportFuncs import *

runsBP = Blueprint('runs', __name__, template_folder='templates')

base_dir = '.'
if getattr(sys, 'frozen', False):
    base_dir = os.path.join(sys._MEIPASS)

@runsBP.route("/", methods=['GET'])
@login_required
def main():
    connection = connect(request)
    session['currentURL'] = url_for('runs.main')
    return render_template('runs/main.html')


@runsBP.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    if request.method == 'POST':
        return response
    else:
        return render_template("error.html", errorMsg=error.to_dict()["message"], errorNo=error.status_code)


@runsBP.route("/insertRun", methods=['POST'])
@login_required
def insertRun():
    """ Insert/edit experimental run entries in the supplied DAQBroker database

    .. :quickref: Insert run; Insert experimental run

    :param: rows : List of run objects. A run object has the following information

            | ``action`` : (String) action to be  preformed on the run

                    | ``addActive`` : Create a new run and set to active status
                    | ``delete`` : Delete run
                    | ``inactive`` : Change a run to inactive status
                    | ``change`` : Edit a run
                    | ``addComment`` : Add a run comment

            | ``run`` : Object containing the run parameters and information. Use :py:meth:getRunListInfo to access each individual parameter. The exra run information, common to every database is the following

                    | ``run`` : (String) run defined encoded in the "run.stage" encoding (run 101 stage 2 is encoded "101.02")
                    | ``comments`` : (String) list of comment objects specific to a run. A common object contains the following attributes:

                            | ``author`` : (String) comment author name
                            | ``time`` : (Integer) timestamp of comment
                            | ``comment`` : (String) the comment

                    | ``author`` : (String - optional) comment author (to send only if action=``addComment``)
                    | ``date`` : (Integer - optional) comment timestamp(to send only if action=``addComment``)
                    | ``comment`` : (String - optional) comment (to send only if action=``addComment``)

            | ``action`` : Action to be  preformed on the run

    """
    processRequest = request.get_json()
    try:
        Session = sessionmaker(bind=current_user.engineObj)
        session = Session()
        #result = session.query(
        #    daqbrokerDatabase.runs).filter_by(
        #    clock=session.query(
        #        func.max(
        #            daqbrokerDatabase.runs.clock)).one_or_none()).first()
        for row in processRequest['rows']:
            if row['action'] == 'addActive':
                #newRun = daqbrokerDatabase.runlist(run = row["run"]["run"], start = row["run"]["start"],end = row["run"]["start"], active = True, lastUpdate =row["run"]["start"], summary = row["run"]["summary"])
                args = {}
                for key in row["run"]:
                    args[key] = row["run"][key]
                args["end"] = row["run"]["start"]
                args["active"] = True
                session.execute(daqbrokerDatabase.daqbroker_database.metadata.tables['runlist'].insert().values(args))
            elif row['action'] == 'delete':
                theRun = session.query(daqbrokerDatabase.runlist).filter_by(run=row['run']['run']).first()
                session.delete(theRun)
            elif row['action'] == 'inactive':
                args = {}
                for key in row["run"]:
                    if key != "run":
                        args[key] = row["run"][key]
                args['active'] = False
                args['end'] = time.time() * 1000
                session.execute(daqbrokerDatabase.daqbroker_database.metadata.tables['runlist'].update().where(
                    daqbrokerDatabase.daqbroker_database.metadata.tables['runlist'].c.run == row["run"]["run"]).values(args))
            elif row['action'] == 'change':
                args = {}
                for key in row["run"]:
                    if key != "run" and key != "oldRun":
                        args[key] = row["run"][key]
                session.execute(daqbrokerDatabase.daqbroker_database.metadata.tables['runlist'].update().where(
                    daqbrokerDatabase.daqbroker_database.metadata.tables['runlist'].c.run == row["run"]["run"]).values(args))
            elif row['action'] == 'addComment':
                theRun = session.query(daqbrokerDatabase.runlist).filter_by(run=row['run']['run']).first()
                commentPut = {'author': row["author"], 'time': row["date"], 'comment': row["comment"]}
                if theRun.comments is not None:
                    prettyComments = json.loads(theRun.comments)
                else:
                    prettyComments = []
                prettyComments.append(commentPut)
                theRun.comments = json.dumps(prettyComments)
        session.commit()
    except BaseException:

        traceback.print_exc()
        raise InvalidUsage('ERROR', status_code=500)
    return jsonify('done')


@runsBP.route("/getRunListInfo", methods=['POST'])
@login_required
def getRunListInfo():
    """ Get relevant information about the existing experimental run list and its parameters

    .. :quickref: Get most recent run list layout; Get most recent run list layout information

    :returns: A JSON encoded object representing a run list layout. Contains the following keys:

            | ``clock`` : (Integer) creation timestamp
            | ``lastUpdate`` : (Integer) last update timestamp
            | ``isLinked`` : (Boolean) to link with Google Spreadsheets (unused)
            | ``linkRemarks`` : (String) Google Spreadsheets link information (unused)
            | ``linkType`` : (Integer) Google Spreadsheets link type (unused)
            | ``runlistRemarks`` : List of experimental parameter objects see :py:meth:submitRunlistData for description of object

    """
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    result = session.query(
        daqbrokerDatabase.runs).filter_by(
        clock=session.query(
            func.max(
                daqbrokerDatabase.runs.clock)).first()[0]).first()
    info = {}
    if result:
        for field in result.__dict__:
            if not field.startswith('_'):
                info[field] = getattr(result, field)
        info['runlistRemarks'] = json.loads(info['runlistRemarks'])
    return jsonify(info)


@runsBP.route("/getRunList", methods=['POST'])
@login_required
def getRunList():
    """ Get a list of experimental run entries

    .. :quickref: Get run list; Get list of experimental runs

    :returns: A JSON encoded list with run objects. Use :py:meth:getRunListInfo to access the individual run parameters. The following keys are always present in each run object:

            | ``start`` : (Integer) run start timestamp
            | ``end`` : (Integer) run end timestamp
            | ``run`` : (String) run defined encoded in the "run.stage" encoding (run 101 stage 2 is encoded "101.02")
            | ``comments`` : (String) JSON encoded list of run comment objects see :py:meth:insertRun for definition of this object

    """
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    result = session.execute(select([daqbrokerDatabase.daqbroker_database.metadata.tables['runlist']]))
    runs = []
    for row in result:
        #print(row)
        run = {}
        for field in result.keys():
            run[field] = row[field]
        runs.append(run)
    return jsonify(runs)


@runsBP.route("/submitRunlistData", methods=['POST'])
@login_required
@require_onetime_admin
def submitRunlistData():
    """ Create/edit experimental run list layout. Insert/edit experimental parameters and parameter types. This request must send its parameters as a single JSON encoded string and the `content-type`_ header must be supplied as `application/json`_

    .. _content-type: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type
    .. _application/json: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types

    .. :quickref: Create/Edit run list; Create or edit the experimental run list layout

    :param: isNewRunlist : (Boolean) if runlist is new
    :param: clock : (Integer) creation timestamp
    :param: runlistType : (Integer) Run list type (unused)
    :param: runlistRemarks : Object containing global runlist information. Contains the following keys:

            | ``cols`` : List of experimental parameter objects. Experimental parameter objects contain the following keys:

                    | ``name`` : (String) name of the parameter
                    | ``type`` : (Integer) type of parameter

                            | ``0`` : Regular parameter
                            | ``3`` : Run Title identifier (optinal declaration)
                            | ``4`` : Option parameter

                    | ``parType`` : (Integer - optional) Type of regular parameter (only used if ``type=1``)

                            | ``0`` : Number
                            | ``1`` : Text

                    | ``parUnits`` : (Integer - optional) Physical parameter units (only used if ``type=1``)
                    | ``parOptions`` : (String - optional) JSON encoded string of parameter options (only used if ``type=1``)
                    | ``action`` : (String) Action to be preformed on parameter

                            | ``add`` : add parameter
                            | ``edit`` : edit parameter
                            | ``delete`` : delete parameter

    """
    newRunList = False
    processRequest = request.get_json()
    if 'isNewRunlist' in processRequest:
        newRunList = processRequest["isNewRunlist"]
    else:
        newRunList = True
    try:
        Session = sessionmaker(bind=current_user.engineObj)
        session = Session()
        conn = current_user.engineObj.connect()
        ctx = MigrationContext.configure(conn)
        op = Operations(ctx)
        result = session.query(
            daqbrokerDatabase.runs).filter_by(
            clock=session.query(
                func.max(
                    daqbrokerDatabase.runs.clock)).first()[0]).first()
        if not result:
            oldRemarks = {}
        else:
            oldRemarks = json.loads(result.runlistRemarks)
        #dbQuery=text("INSERT INTO runs VALUES(:clock,:clock,0,:linkRemarks,:runlistType,:runlistRemarks)")
        #startTableAlter="ALTER TABLE runlist "
        if newRunList:
            for i, col in enumerate(processRequest["runlistRemarks"]["cols"]):
                if ((not (int(col["type"]) == 1)) and (not (int(col["type"]) == 2)) and (not (int(col["type"]) == 3))):
                    if int(col["type"]) == 4:
                        newType = daqbrokerDatabase.Text
                    if int(col["type"]) == 0 and int(col["parType"]) == 1:
                        newType = daqbrokerDatabase.Text
                    if int(col["type"]) == 0 and int(col["parType"]) == 0:
                        newType = daqbrokerDatabase.Float
                    newCol = daqbrokerDatabase.Column(col["name"], newType)
                    op.add_column("runlist", newCol)
                processRequest["runlistRemarks"]["cols"][i]["action"] = "addOld"
        else:
            for i, col in enumerate(processRequest["runlistRemarks"]["cols"]):
                extra = ''
                #print(col)
                if not int(col["type"]) == 3:
                    if i >= len(oldRemarks["cols"]):
                        column = col
                    else:
                        column = oldRemarks["cols"][i]
                    if int(col["type"]) == 4:
                        newType = daqbrokerDatabase.Text
                    if int(col["type"]) == 0 and int(col["parType"]) == 1:
                        newType = daqbrokerDatabase.Text
                    if int(col["type"]) == 0 and int(col["parType"]) == 0:
                        extra = "\"" + column["name"] + "\"::double precision"
                        newType = daqbrokerDatabase.Float
                    if col['action'] == 'add':
                        newCol = daqbrokerDatabase.Column(col["name"], newType)
                        op.add_column("runlist", newCol)
                        processRequest["runlistRemarks"]["cols"][i]["action"] = "addOld"
                    elif col['action'] == 'edit':
                        if col["name"] != column["name"]:
                            op.alter_column(
                                "runlist",
                                oldRemarks["cols"][i]["name"],
                                new_column_name=col["name"],
                                type_=newType,
                                postgresql_using=extra)
                        else:
                            op.alter_column(
                                "runlist",
                                oldRemarks["cols"][i]["name"],
                                type_=newType,
                                postgresql_using=extra)
                    elif col['action'] == 'delete':
                        op.drop_column("runlist", col["name"])
                    #print("done")
            daqbrokerDatabase.daqbroker_database.metadata.remove(
                daqbrokerDatabase.daqbroker_database.metadata.tables["runlist"])
            daqbrokerDatabase.daqbroker_database.metadata.reflect(current_user.engineObj, extend_existing=True)
            processRequest["runlistRemarks"]["cols"] = [
                x for x in processRequest["runlistRemarks"]["cols"] if x['action'] != 'delete']
        newRuns = daqbrokerDatabase.runs(
            clock=processRequest["clock"],
            linkRemarks='',
            runlistRemarks=json.dumps(
                processRequest["runlistRemarks"]))
        session.add(newRuns)
        session.commit()
        conn.close()
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        raise InvalidUsage(str(e), status_code=500)
    return jsonify('done')

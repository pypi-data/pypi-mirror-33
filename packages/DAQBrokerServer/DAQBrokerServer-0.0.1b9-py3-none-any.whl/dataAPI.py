import time
import json
import traceback
import multiprocessing
import sqlite3
from sqlalchemy import text
from sqlalchemy import bindparam
from flask import Blueprint
from flask import request
from flask import render_template
from flask import session
from flask import jsonify
from flask import current_app
from flask_login import login_required
from flask_login import current_user
from supportFuncs import *

dataBP = Blueprint('data', __name__, template_folder='templates')

base_dir = '.'
if getattr(sys, 'frozen', False):
    base_dir = os.path.join(sys._MEIPASS)

@dataBP.route("/", methods=['GET'])
@login_required
def main():
    connection = connect(request)
    session['currentURL'] = url_for('data.main')
    return render_template('data/main.html')


@dataBP.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    if request.method == 'POST':
        return response
    else:
        return render_template("error.html", errorMsg=error.to_dict()["message"], errorNo=error.status_code)


@dataBP.route("/getPlotComments", methods=['POST'])
@login_required
def getPlotComments():
    """ Retrieve a list of comments associated with an existing data visualization

    .. :quickref: Get plot comments; Get list of comments associated with plot

    :param: plotid : (Integer) unique plot identifier
    :param: chanelid : (Integer - optional) unique channel identifier

    :returns: JSON encoded list of comment objects associated with the provided visualization. If the optional **channelid** parameter is provided, the search is limited to visualization comments specific to one data channel. A comment object contains the following keys:

            | ``clock`` : (Integer) comment timestamp
            | ``plotid`` : (Integer) unique visualization identifier
            | ``channelid`` : (Integer) unique channel identifier
            | ``comment`` : (String) comment
            | ``author`` : (String) comment author
            | ``remarks`` : (String) extra information (unused)

    """
    connection = connect(request)
    processRequest = request.get_json()
    comments = []
    if connection:
        channelid = None
        plotid = None
        if 'plotid' in request.form:
            plotid = request.form['plotid']
        elif 'plotid' in request.args:
            plotid = request.args['plotid']
        if plotid:
            if 'channelid' in request.form:
                channelid = request.form['channelid']
            elif 'channelid' in request.args:
                channelid = request.args['channelid']
        if channelid and plotid:
            dbQuery = text(
                "SELECT * FROM plotcomments WHERE plotid=:thePlot AND channelid=:theChannel").bindparams(theChannel=channelid, thePlot=plotid)
        elif plotid:
            dbQuery = text("SELECT * FROM plotcomments WHERE plotid=:thePlot").bindparams(thePlot=plotid)
        else:
            dbQuery = text("SELECT * FROM plotcomments")
        result = connection.execute(dbQuery)
        for row in result:
            localDict = dict(zip(row.keys(), row))
            comments.append(localDict)
    else:
        raise InvalidUsage('Error connecting to database', status_code=500)

    return jsonify(comments)


@dataBP.route("/getPlots", methods=['POST'])
@login_required
def getPlots():
    """ Get a list of saved data visualizations

    .. :quickref: Get visualization list; Get a list of saved data visualizations

    :returns: A JSON encoded list of visualizations. Each object contains the following keys:

            | ``plotname`` : (String) unique visualization name
            | ``plotid`` : (Integer) unique visualization identifier
            | ``channelids`` : (String) JSON encoded list of data channel identifiers
            | ``plottype`` : (Integer) type of plot

                    | ``0`` : Time series
                    | ``1`` : Time evolving historgram
                    | ``2`` : Histogram
                    | ``3`` : External

            | ``adminPlot`` : (Boolean) plot created by admin (unused)
            | ``active`` : (Boolean) active flag (unused)
            | ``remarks`` : (String) extra information for each **plottype**

    """
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    plots = []
    for row in session.query(daqbrokerDatabase.plots):
        plot = {}
        for field in row.__dict__:
            if not field.startswith('_'):
                plot[field] = getattr(row, field)
        plots.append(plot)
        plots[-1]["remarks"] = json.loads(plots[-1]["remarks"])
        plots[-1]["channelids"] = json.loads(plots[-1]["channelids"])
    return jsonify(plots)


@dataBP.route("/getLayouts", methods=['POST'])
@login_required
def getLayouts():
    """ Get a list of saved sets of data visualizations

    .. :quickref: Get layout list; Get a list of saved sets of data visualizations

    :returns: A JSON encoded list of sets of visualizations, called layouts. Each layout object contains the following keys:

            | ``Name`` : (String) unique layout name
            | ``layoutid`` : (Integer) unique layout identifier
            | ``plots`` : (String) JSON encoded list of visualization identifiers
            | ``format`` : (String) JSON encoded format of layout

    """
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    layouts = []
    for row in session.query(daqbrokerDatabase.layouts):
        layout = {}
        for field in row.__dict__:
            if not field.startswith('_'):
                layout[field] = getattr(row, field)
        layouts.append(layout)
        layouts[-1]["remarks"] = json.loads(layouts[-1]["remarks"])
        layouts[-1]["channelids"] = json.loads(layouts[-1]["channelids"])
    return jsonify(layouts)


@dataBP.route("/saveVisualization", methods=['POST'])
@login_required
@require_onetime_admin
def saveVisualization():
    """ Save a data visualization or a set of data visualizations

    .. :quickref: Create/Edit visualizations; Create or edit a visualization or a set of visualizations

    :param: visionType : (Integer) Type of visualization

            | ``0`` : Single data visualization
            | ``1`` : Set of visualizations (layout)

    :param: plotid : (Integer) unique identifier visualization. Used to edit visualizations. Only used if **visionType=0**
    :param: plotname : (String) unique visualization name. Only used if **visionType=0**
    :param: plottype : (Integer) creation timestamp. See :py:meth:getLayouts for types. Only used if **visionType=0**
    :param: channelids : (String) JSON encoded list of data channels used. Only used if **visionType=0**
    :param: remarks : (String) JSON encoded object of extra **plottype** information. Only used if **visionType=0**


    :param: layoutid : (Integer) unique identifier of created layout. Used to edit layouts. Only used if **visionType=1**
    :param: layoutname : (String) unique layout name. Only used if **visionType=1**
    :param: plots : (String) JSON encoded list of unique plot identifiers on layout. Only used if **visionType=1**
    :param: format : (String) JSON encoded object of layout information. Only used if **visionType=1**

    :returns: If **visionType=0** returns the unique identifier of the added or altered visualization. IOf **visionType=1** returns the unique identifier of added or altered layout

    """
    Session = sessionmaker(bind=current_user.engineObj)
    session = Session()
    processRequest = request.get_json()
    if 'visionType' in processRequest:
        visionType = processRequest['visionType']
    else:
        raise InvalidUsage('No visualization type provided', status_code=500)
    try:
        if int(visionType) == 0:  # Single Plot
            if 'plottype' in processRequest:
                plottype = processRequest['plottype']
            else:
                raise InvalidUsage('No plot type provided', status_code=500)
            if not ('plotid' in processRequest):
                maxPlot = session.query(func.max(daqbrokerDatabase.plots.plotid)).one_or_none()
                if maxPlot[0]:
                    theID = maxPlot[0]+1
                else:
                    theID = 0
                plot = daqbrokerDatabase.plots(
                    plotname=processRequest["plotname"],
                    plotid=theID,
                    channelids=json.dumps(processRequest["channelids"]),
                    remarks=json.dumps(processRequest["remarks"]),
                    plottype=processRequest["plottype"]
                )
                session.add(plot)
            else:
                theID = processRequest["plotid"]
                plotTable = daqbrokerDatabase.daqbroker_database.metadata.tables["plots"]
                valDict = {'plotname': processRequest["plotname"],
                           'channelids': json.dumps(processRequest["channelids"]),
                           'remarks': json.dumps(processRequest["remarks"]), 'plottype': processRequest["plottype"]}
                session.execute(plotTable.update().where(plotTable.c.plotid == int(processRequest["plotid"])).values(valDict))
        elif int(visionType) == 1:  # Layout
            if not ('layoutid' in processRequest):
                maxPlot = session.query(func.max(daqbrokerDatabase.layouts.layoutid)).one_or_none()
                if maxPlot[0]:
                    theID = maxPlot[0]+1
                else:
                    theID = 0
                layout = daqbrokerDatabase.layouts(
                    layoutname=processRequest["layoutname"],
                    plots=json.dumps(processRequest["plots"]),
                    format=json.dumps(processRequest["format"]),
                    layoutid=theID
                )
                session.add(layout)
            else:
                theID = processRequest["layoutid"]
                layoutTable = daqbrokerDatabase.daqbroker_database.metadata.tables["layouts"]
                valDict={'layoutname':processRequest["layoutname"],'plots':json.dumps(processRequest["plots"]),'format':json.dumps(processRequest["format"])}
                session.execute(layoutTable.update().where(layoutTable.c.layoutid == int(processRequest["layoutid"])).values(valDict))
        else:
            raise InvalidUsage('Incorrect visualization type provided', status_code=500)
        session.commit()
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        raise InvalidUsage('Incorrect visualization type provided', status_code=500)
    return jsonify(theID)


@dataBP.route("/getDataStream", methods=['POST'])
@login_required
def getDataStream():
    """ Start data collection job of a list of data channels

    .. :quickref: Create data collection jobs; Create a set of possibly long running data collection jobs

    :param: reqID : (String) Uniquely generated ID string to identify the requested jobs
    :param: jobRequests : JSON encoded list of request objects with the following keys:

            | ``startTime`` : (Integer) start timestamp
            | ``endTime`` : (Integer) end timestamp
            | ``type`` : (String) type of request

                    | ``data`` : Single channel data
                    | ``expression`` : Data from expression

            | ``screenSize`` : (Integer) size of display in pixels (used to decrease query load)
            | ``fullResolution`` : (Boolean) if true, get all data regardless of ``screenSize`` value
            | ``channelid`` : (Integer) unique data channel identifier (only used if ``type="data"``)
            | ``expression`` : (String) data manipulation expression (only used if ``type="expression"``)
            | ``expressionName`` : (String) expression name (only used if ``type="expression"``)
            | ``expressionIdx`` : (String) expression index in list of expressions (only used if ``type="expression"``)

    :returns: A JSON encoded list of an ongoing job objects with the following keys:

            | ``id`` : (String) unique job identifier
            | ``channelid`` : (Integer) unique channel identifier only returned if  (only used if ``type="data"``)

            | ``name`` : (String) same as ``expressionName`` only returned if  (only used if ``type="expression"``)
            | ``idx`` : (String) same as ``expressionIdx`` only returned if  (only used if ``type="expression"``)


    """
    processRequest = request.get_json()
    processWorkers = []
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    try:
        for jobRequest in processRequest['jobRequests']:
            unique = uuid.uuid1()
            theSession = {}
            # POST request check
            emptyIndex = next(i for i, val in enumerate(current_app.config['workers']) if val == -1)
            current_app.config['workers'][emptyIndex] = 0
            if jobRequest["type"] == 'data':
                daqbrokerSettings.workerpool.submit(
                    getChannelData,
                    jobRequest["channelid"],
                    jobRequest["startTime"],
                    jobRequest["endTime"],
                    0,
                    jobRequest["screenSize"],
                    str(unique),
                    int(1),
                    current_app.config['workers'],
                    current_user.engineObj,
                    False,
                    emptyIndex
                )
                processWorkers.append({'id': unique, 'channelID': jobRequest["channelid"]})
            elif jobRequest["type"] == 'expression':
                daqbrokerSettings.workerpool.submit(
                    calculateExpressionData,
                    jobRequest["expression"],
                    jobRequest["startTime"],
                    jobRequest["endTime"],
                    0,
                    jobRequest["screenSize"],
                    str(unique),
                    int(1),
                    current_app.config['workers'],
                    theSession,
                    False,
                    emptyIndex
                )
                processWorkers.append({'id': unique,
                                       'name': jobRequest["expressionName"],
                                       'idx': jobRequest["expressionIdx"]})
            #jobRequest["pid"] = p.pid
            if 'type' in jobRequest:  # Assume the job is only of data request if no type is presented
                jobtype = jobRequest['type']
            else:
                jobtype = 'data'
            newJob=daqbrokerSettings.jobs(
                clock=time.time() * 1000,
                jobid=str(unique),
                type=jobtype,
                username=current_user.username,
                status=0,
                data=emptyIndex,
                error='{}',
                reqid=processRequest['reqID']
            )
            session.add(newJob)
        session.commit()
        return jsonify(processWorkers)
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        raise InvalidUsage(str(e), status_code=500)

@dataBP.route("/getDataCheckStream", methods=['POST'])
@login_required
def getDataCheckStream():
    """ Get the data from provided list of existing jobs. See :py:meth:getDataStream for more information on generating a list jobs. Job results are stored in memory and the local database contains a reference to the memory position of that data if the job completed successfully

    .. :quickref: Collect job data; Collect data or running info from data collection jobs

    :param: jobs : JSON encoded list of job objects, containing the following keys:

            | ``id`` : (String) unique job identifier

    :returns: A job result object containing the following keys

            | ``id`` : (String) unique job identifier
            | ``type`` : (String) job type. See :py:meth:getDataStream for more information
            | ``data`` : (String) JSON encoded object of information data about the requested job
            | ``status`` : (integer) Status of the requested job

                    | ``0`` : Job underway
                    | ``1`` : Job finished, no errors
                    | ``-1`` : Job finished, with errors

    """
    processRequest = request.get_json()
    scoped = daqbrokerSettings.getScoped()
    localSession = scoped()
    jobs = []
    for job in localSession.query(daqbrokerSettings.jobs).filter(daqbrokerSettings.jobs.jobid.in_([x["id"] for x in processRequest["jobs"]])):
        #print(job.status, job.jobid, job.type, job.data, current_app.config["workers"][int(job.data)])
        if job.status == 1:
            jobs.append({'status': 1, 'id': job.jobid, 'data': current_app.config["workers"][int(job.data)], 'type': job.type})
            current_app.config["workers"][int(job.data)] = -1
            localSession.delete(job)
        elif job.status == -1:
            jobs.append({'status': -1, 'id': job.jobid, 'data': False, 'type': job.type})
            current_app.config["workers"][int(job.data)] = -1
            localSession.delete(job)
        elif not current_app.config["workers"][int(job.data)] in [-1, 0]: #IF the sqlite database failed with the job for some reason, WHY IS THIS HAPPENING?!
            jobs.append({'status': 1, 'id': job.jobid, 'data': current_app.config["workers"][int(job.data)], 'type': job.type})
            current_app.config["workers"][int(job.data)] = -1
        localSession.delete(job)
    localSession.commit()
    return jsonify(jobs)


@dataBP.route("/getDataAbortStream", methods=['POST'])
@login_required
def getDataAbortStream():
    """ Abort a set of supplied jobs. See 'getDataStream' for more information on generating a list jobs. This request interrupts ongoing jobs, deletes local database records and deletes data in memory

    .. :quickref: Abort jobs; Abort running data collection jobs

    :param: jobs : JSON encoded list of unique job identifiers

    """
    processRequest = request.get_json()
    scoped = daqbrokerSettings.getScoped()
    localSession = scoped()
    #thisUser = getUserDetails(current_user.username, connection)
    for job in processRequest:
        #jobsTable = daqbrokerSettings.daqbroker_settings.metadata.tables["jobs"]
        jobObj = localSession.query(daqbrokerSettings.jobs).filter_by(jobid=job).first()
        if jobObj:
            current_app.config['workers'][int(jobObj.data)] = -1
            localSession.delete(jobObj)
        #try:
        #   theProcess = psutil.Process(deets["pid"])
        #except BaseException:
        #   theProcess = None
        #if theProcess:
        #    theProcess.terminate()
        #for row in query:
        #    deets = json.loads(row["type"])
        #    try:
        #        theProcess = psutil.Process(deets["pid"])
        #    except BaseException:
        #        theProcess = None
        #    if theProcess:
        #        theProcess.terminate()
        #    current_app.config['workers'][int(row["data"])] = -1
        #connection.execute(text("DELETE FROM " + jobsTable + " WHERE jobid=:jobid"), jobid=job)
    localSession.commit()
    return jsonify('done')


@dataBP.route("/getDataAbortStreamRequest", methods=['POST'])
@login_required
def getDataAbortStreamRequest():
    """ Abort a single job. See 'getDataStream' for more information on generating a list jobs

    .. :quickref: Abort single job; Abort single running data collection jobs

    :param: jobs : JSON encoded list of unique job identifiers

    """
    connection = connect(request)
    processRequest = request.get_json()
    if connection:
        query = connection.execute(text("SELECT * FROM jobs WHERE reqid=:jobid"), jobid=processRequest['id'])
        for row in query:
            deets = json.loads(row["type"])
            try:
                theProcess = psutil.Process(deets["pid"])
            except BaseException:
                theProcess = None
            if theProcess:
                theProcess.terminate()
            current_app.config['workers'][int(row["data"])] = -1
        connection.execute(text("DELETE FROM jobs WHERE reqid=:jobid"), jobid=processRequest['id'])
    else:
        raise InvalidUsage('Error connecting to database', status_code=500)

    return jsonify('done')


@dataBP.route("/getDataCheck", methods=['POST'])
@login_required
def getDataCheck():
    """Auxiliary request used to check collect generic information from a job

    .. :quickref: Gata job data; Get data from a generic job

    :param id: (String) unique job identifier

    :returns: (String) JSON encoded string of the requested job's information, check :py:func:`getDataCheckStream` to get a reference of the returned object

    """
    if 'id' in request.form:
        id = request.form["id"]
    else:
        raise InvalidUsage("No id provided", status_code=400)
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    theJob = session.query(daqbrokerSettings.jobs).filter_by(jobid=id).first()
    if theJob:
        if theJob.status == 1: # Success! The data should be in p["data"]
            toReturn = {'status':1,'data':current_app.config['workers'][int(theJob.data)]}
            current_app.config['workers'][int(theJob.data)] = -1
            return jsonify(toReturn)
        elif theJob.status == 0:  # Gathering still ongoing
            toReturn = False
            return jsonify(toReturn)
        elif theJob.status == -1:  # There was a problem with the gathering
            toReturn = -1
            current_app.config["workers"][int(theJob.data)] = -1
            return jsonify(toReturn)
        else:  # Something went terribly wrong, getting rid of this, the user can try again
            toReturn = -1
            return jsonify(toReturn)
    else:
        raise InvalidUsage('Requested job not found, make sure you are using the correct ID', status_code=500)


@dataBP.route("/getDataAbort", methods=['POST', 'GET'])
@login_required
def getDataAbort():
    """Auxiliary request used to check abort a generic job

    .. :quickref: Abort job; Abort generic job

    :param id: (String) unique job identifier

    """
    if 'id' in request.form:
        id = request.form["id"]
    else:
        raise InvalidUsage("No id provided", status_code=400)
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    theJob = session.query(daqbrokerSettings.jobs).filter_by(jobid=id).first()
    if theJob:
        session.delete(theJob)
    else:
        raise InvalidUsage('Requested job not found, make sure you are using the correct ID', status_code=500)
    return jsonify('done')


@dataBP.route("/getData", methods=['POST'])
@login_required
def getData():
    """ Get data from a supplied data channel. The request can be asynchronous, returning a job or it can be sequential, returning the requested data. This request is tested with the flask is_xhr flag (DEPRECATED, NEED TO IMPROVE) to decide if the request is created as a long running job or a concurrent one. This test should decide if the request is being made from a command line or third-party program or if it is sent via an interface

    .. :quickref: Get channel data; Get data from specified channel

    :param: startTime : (Integer) start timestamp
    :param: endTime :(Integer) end timestamp
    :param: screenSize : (Integer) size of display in pixels (used to decrease query load)
    :param: fullResolution : (Boolean) if true, get all data regardless of ``screenSize`` value
    :param: channelid : (Integer) unique data channel identifier

    :returns: JSON encoded object with the requested data if ``is_xhr=False``:

            | ``type`` : (String) type of data requested, should default to "data"
            | ``closestClockDown`` : (Ineger) closest time stamp to **startTime** , used for interpolation needs in case of empty ranges
            | ``closestClockUp`` : (Ineger) closest time stamp to **endTime** , used for interpolation needs in case of empty ranges
            | ``closestValueDown`` : (Double or String) closest time stamp to **startTime** , used for interpolation needs in case of empty ranges
            | ``closestValueUp`` : (Double or String) closest time stamp to **endTime** , used for interpolation needs in case of empty ranges
            | ``min`` : (Double or String) minimum value in range
            | ``max`` : (Double or String) maximum value in range
            | ``mean`` : (Double or String) mean of data range (only works on number channels)
            | ``std`` : (Double or String) standard deviation of data range
            | ``minTime`` : (Double) minimum timestamp in range
            | ``maxTime`` : (Double) maximum timestamp in range
            | ``minTimeStep`` : (Double) minimum interval between timestamps in range
            | ``maxTimeStep`` : (Double) maximum interval between timestamps in range
            | ``meanTime`` : (Double) mean interval between timestamps in range
            | ``stdTime`` : (Double) standard deviation between timestamps in range (broken)
            | ``name`` : (String) data channel name
            | ``iname`` : (String) channel instrument name
            | ``channelID`` : (Integer) Unique channel identifier
            | ``channeltype`` : (Integer) same as ``type``
            | ``remarks`` : (String) JSON encoded object with extra information
            | ``metaid`` : (Integer) Unique data source identifier
            | ``query`` : (String) SQL query used to collect the data
            | ``data`` : List 2 element lists of [timestamp, value] inside the requested time range [**startTime**,**endTime**]

    JSON encoded job object if ``is_xhr=True``:

            | ``id`` : (String) unique job identifier
            | ``type`` : (String) type of request. Should default to "data" in this request

                    | ``data`` : Single channel data
                    | ``expression`` : Data from expression

    """
    connection = connect(request)
    #print(request.form)
    if connection:
        if 'channelid' in request.form:
            channelid = request.form['channelid']
            usingPost = True
        elif 'channelid' in request.args:
            channelid = request.args['channelid']
            usingPost = False
        else:
            raise InvalidUsage('No channel ID provided', status_code=500)
        if 'startTime' in request.form:
            startTime = request.form['startTime']
        elif 'startTime' in request.args:
            startTime = request.args['startTime']
        else:
            raise InvalidUsage('No start time provided', status_code=500)
        if 'endTime' in request.form:
            endTime = request.form['endTime']
        elif 'endTime' in request.args:
            endTime = request.args['endTime']
        else:
            raise InvalidUsage('No end time provided', status_code=500)
        if 'screenSize' in request.form:
            screenSize = int(request.form['screenSize'])
        elif 'screenSize' in request.args:
            screenSize = int(request.args['screenSize'])
        else:
            screenSize = 1000000000000000000000000
        if 'fullResolution' in request.form:
            fullResolution = request.form['fullResolution']
        elif 'fullResolution' in request.args:
            fullResolution = request.args['fullResolution']
        else:
            fullResolution = 0
        # if 'cached' in request.form:
            # cached=request.form['cached']
        # elif 'cached' in request.args:
            # cached=request.args['cached']
        if request.is_xhr:
            cached = 1
        else:
            cached = 0
        unique = uuid.uuid1()
        if int(cached) == 0:

            return jsonify(getChannelData(channelid, startTime, endTime, fullResolution, screenSize,
                                          unique, cached, current_app.config['workers'], request, False, -1))
        elif int(cached) == 1:
            if usingPost:
                theData = request.form
            else:
                theData = request.args
            theSession = {}
            # POST request check
            if('username' in request.form):
                thecurrent_user.username = request.form['username']
            elif('user' in request.form):
                thecurrent_user.username = request.form['user']
            else:
                thecurrent_user.username = current_user.username
            if('password' in request.form):
                thecurrent_user.password = request.form['password']
            elif('pass' in request.form):
                thecurrent_user.password = request.form['pass']
            else:
                thecurrent_user.password = current_user.password
            if('database' in request.form):
                thecurrent_user.database = request.form['database']
            if('serverName' in request.form):
                thecurrent_user.server = request.form['serverName']
            else:
                thecurrent_user.server = current_user.server
            if('serverEngine' in request.form):
                thecurrent_user.engine = request.form["serverEngine"]
            else:
                thecurrent_user.engine = current_user.engine
            # GET request check
            if('username' in request.args):
                thecurrent_user.username = request.args['username']
            elif('user' in request.args):
                thecurrent_user.username = request.args['user']
            else:
                thecurrent_user.username = current_user.username
            if('password' in request.args):
                thecurrent_user.password = request.args['password']
            elif('pass' in request.args):
                thecurrent_user.password = request.args['pass']
            else:
                thecurrent_user.password = current_user.password
            if('database' in request.args):
                thecurrent_user.database = request.args['database']
            else:
                thecurrent_user.database = current_user.database
            if('serverName' in request.args):
                current_user.server = request.args['serverName']
            else:
                thecurrent_user.server = current_user.server
            if('serverEngine' in request.args):
                thecurrent_user.engine = request.args['serverEngine']
            else:
                thecurrent_user.engine = current_user.engine
            try:
                emptyIndex = next(i for i, val in enumerate(current_app.config['workers']) if val == -1)
                current_app.config['workers'][emptyIndex] = 0
                connection.execute(text("INSERT INTO jobs VALUES(:clock,:jobid,:type,:username,:status,:data,:error)"), clock=time.time(
                ) * 1000, jobid=str(unique), type='dataChannel', username=current_user.username, status=0, data=emptyIndex, error='{}')
                p = multiprocessing.Process(
                    target=getChannelData,
                    args=(
                        channelid,
                        startTime,
                        endTime,
                        fullResolution,
                        screenSize,
                        str(unique),
                        int(cached),
                        current_app.config['workers'],
                        theSession,
                        False,
                        emptyIndex))
                p.start()
                # workers.append({'id':str(unique),'process':p.pid,'status':0,'data':[],'time':time.time()})

                return json.dumps({'id': str(unique), 'type': 'dataChannel'})
            except Exception as e:

                raise InvalidUsage(str(e), status_code=500)
        else:

            raise InvalidUsage('Wrong cached parameter', status_code=500)
    else:
        raise InvalidUsage('Error connecting to the database', status_code=500)


@dataBP.route("/getExpressionTrace", methods=['POST'])
@login_required
def getExpressionTrace():
    """ Collect manipulated data from a supplied expression. The request can be asynchronous returning an ongoing job or sequential returning the full processed data. This request is tested with the flask is_xhr flag (DEPRECATED, NEED TO IMPROVE) to decide if the request is created as a long running job or a concurrent one. This test should decide if the request is being made from a command line or third-party program or if it is sent via an interface

    .. :quickref: Get expression data; Get data from specified expression

    :param: startTime : (Integer) start timestamp
    :param: endTime :(Integer) end timestamp
    :param: screenSize : (Integer) size of display in pixels (used to decrease query load)
    :param: fullResolution : (Boolean) if true, get all data regardless of ``screenSize`` value
    :param: expression : (Integer) unique data channel identifier

    :returns: JSON encoded object with the requested data if ``is_xhr=False``:

            | ``type`` : type of data request. Should default to "expression"
            | ``data`` : List of 2 element lists of [timestamp, value] inside the requested time range [**startTime**,**endTime**]

    JSON encoded job object if ``is_xhr=True``:

            | ``id`` : (String) unique job identifier
            | ``type`` : (String) type of request. Should default to "expression"

                    | ``data`` : Single channel data
                    | ``expression`` : Data from expression
    """
    connection = connect(request)
    if connection:
        if 'expression' in request.form:
            expression = request.form['expression']
        elif 'expression' in request.args:
            expression = request.args['expression']
        else:

            raise InvalidUsage('No expression provided', status_code=500)
        if 'startTime' in request.form:
            startTime = request.form['startTime']
        elif 'startTime' in request.args:
            startTime = request.args['startTime']
        else:

            raise InvalidUsage('No start time provided', status_code=500)
        if 'endTime' in request.form:
            endTime = request.form['endTime']
        elif 'endTime' in request.args:
            endTime = request.args['endTime']
        else:
            raise InvalidUsage('No end time provided', status_code=500)
        if 'screenSize' in request.form:
            screenSize = int(request.form['screenSize'])
        elif 'screenSize' in request.args:
            screenSize = int(request.args['screenSize'])
        else:
            screenSize = 1000000000000000000000000
        if request.is_xhr:
            cached = 1
        else:
            cached = 0
        unique = uuid.uuid1()
        fullResolution = False
        if cached == 0:
            return calculateExpressionData(expression, startTime, endTime, fullResolution,
                                           screenSize, unique, int(cached), [], {}, False, -1)
        else:
            theSession = {}
            if('username' in request.form):
                thecurrent_user.username = request.form['username']
            elif('user' in request.form):
                thecurrent_user.username = request.form['user']
            else:
                thecurrent_user.username = current_user.username
            if('password' in request.form):
                thecurrent_user.password = request.form['password']
            elif('pass' in request.form):
                thecurrent_user.password = request.form['pass']
            else:
                thecurrent_user.password = current_user.password
            if('database' in request.form):
                thecurrent_user.database = request.form['database']
            if('serverName' in request.form):
                thecurrent_user.server = request.form['serverName']
            else:
                thecurrent_user.server = current_user.server
            if('serverEngine' in request.form):
                thecurrent_user.engine = request.form["serverEngine"]
            else:
                thecurrent_user.engine = current_user.engine
            # GET request check
            if('username' in request.args):
                thecurrent_user.username = request.args['username']
            elif('user' in request.args):
                thecurrent_user.username = request.args['user']
            else:
                thecurrent_user.username = current_user.username
            if('password' in request.args):
                thecurrent_user.password = request.args['password']
            elif('pass' in request.args):
                thecurrent_user.password = request.args['pass']
            else:
                thecurrent_user.password = current_user.password
            if('database' in request.args):
                thecurrent_user.database = request.args['database']
            else:
                thecurrent_user.database = current_user.database
            if('serverName' in request.args):
                current_user.server = request.args['serverName']
            else:
                thecurrent_user.server = current_user.server
            if('serverEngine' in request.args):
                thecurrent_user.engine = request.args['serverEngine']
            else:
                thecurrent_user.engine = current_user.engine
            emptyIndex = next(i for i, val in enumerate(current_app.config['workers']) if val == -1)
            current_app.config['workers'][emptyIndex] = 0
            connection.execute(text("INSERT INTO jobs VALUES(:clock,:jobid,:type,:username,:status,:data,:error)"), clock=time.time(
            ) * 1000, jobid=str(unique), type='expression', username=current_user.username, status=0, data=emptyIndex, error='{}')
            p = multiprocessing.Process(
                target=calculateExpressionData,
                args=(
                    expression,
                    startTime,
                    endTime,
                    fullResolution,
                    screenSize,
                    str(unique),
                    int(cached),
                    current_app.config['workers'],
                    theSession,
                    False,
                    emptyIndex))
            p.start()
            # workers.append({'id':str(unique),'process':p.pid,'status':0,'data':[],'time':time.time()})
            return json.dumps({'id': str(unique), 'type': 'expression'})
    else:
        raise InvalidUsage('Error connecting to database', status_code=500)

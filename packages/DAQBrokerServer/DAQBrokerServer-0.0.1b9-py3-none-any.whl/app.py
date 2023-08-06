import time
import sys
import json
import traceback
import logging
import multiprocessing
import ntplib
import socket
import psutil
import struct
import shutil
import uuid
import platform
#import sqlalchemy
import os
import math
import json
import signal
import sqlite3
import pyAesCrypt
import snowflake
import re
import ctypes
import inspect
import concurrent.futures
import hashlib
import daqbrokerDatabase
import daqbrokerSettings
from asteval import Interpreter
from concurrent_log_handler import ConcurrentRotatingFileHandler
from subprocess import call
from subprocess import check_output
#from bcrypt import gensalt
from logging.handlers import RotatingFileHandler
from functools import reduce
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import bindparam
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists
from sqlalchemy_utils.functions import drop_database
from sqlalchemy_utils.functions import create_database
from flask import Flask
from flask import Markup
from flask import request
from flask import render_template
from flask import redirect
from flask import send_from_directory
from flask import url_for
from flask import session
from flask import flash
from flask import jsonify
from flask import request_tearing_down
from flask_login import UserMixin
from flask_login import LoginManager
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user
from urllib.parse import urlparse
#from gevent.pywsgi import WSGIServer
from numpy import asarray, linspace
from scipy.interpolate import interp1d
from numbers import Number
from bpApp import daqbroker
from instrumentsAPI import instrumentsBP
from monitoringAPI import monitoringBP
from dataAPI import dataBP
from runsAPI import runsBP
from adminAPI import adminBP
from supportFuncs import *

usersArray = []
# tablesToAct=['instruments','channels','instmeta','parsing','plots','plotcomments','runs']
tablesToAct = [
    x[0] for x in inspect.getmembers(
        sys.modules["daqbrokerDatabase"],
        lambda member: inspect.isclass(member) and member.__module__ == "daqbrokerDatabase")]
tablesToActSettings = [
    x[0] for x in inspect.getmembers(
        sys.modules["daqbrokerSettings"],
        lambda member: inspect.isclass(member) and member.__module__ == "daqbrokerSettings")]

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = str(uuid.uuid4())
    return session['_csrf_token']


def getServer():
    if hasattr(current_user,'server'):
        return current_user.server
    else:
        return None

def getEngine():
    if hasattr(current_user, 'engine'):
        return current_user.engine
    else:
        return None

def getusertype():
    if hasattr(current_user, 'type'):
        return current_user.type
    else:
        return None

class User(UserMixin):
    def __init__(self, username, password, server, engine, database=None):
        try:
            self.id = None
            self.engine = engine
            self.username = username
            self.password = password
            self.server = server
            self.database = database
            self.uriHome = engine + "://" + username + ":" + password + "@" + server
            self.uri = engine + "://" + username + ":" + password + "@" + server
            self.uriSettings = engine + "://" + username + ":" + password + "@" + server + "/daqbroker_settings"
            self.authenticated = True
            if self.database:
                self.uri = engine + "://" + username + ":" + password + "@" + server + '/daqbro_' + self.database
            self.engineObj = create_engine(self.uri)
            self.engineObjSettings = create_engine(self.uriSettings)
            self.conn = self.engineObj.connect()
            self.active = True
            self.id = str(uuid.uuid4())
            self.type = None
        except Exception as e:
            self.engineObj = False
            self.engineObjSettings = False
            self.conn = False
            self.active = False
            self.id = None
            self.authenticated = False
            self.type = None
            message = Markup('<p class="errorExcept"><span style="color:#dc3545">Error : ' + str(e) + '</span></p>')
            flash(message)
            traceback.print_exc()
        finally:
            self.conns = [{'password': password,
                           'username': username,
                           'server': server,
                           'engine': engine,
                           'uriHome': engine + "://" + username + ":" + password + "@" + server,
                           'engineObj': self.engineObj,
                           'settinsObj': self.engineObjSettings,
                           'conn': self.conn,
                           'id': hashlib.sha224(engine.encode() + b"://" + server.encode()).hexdigest()}]
            #print(self.type)

    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return self.active

    def updateDB(self):
        if self.conn:
            self.conn.close()
        newURI = self.engine + "://" + self.server
        foundTheConnection = False
        for i, connection in enumerate(self.conns):
            if connection["id"] == hashlib.sha224(newURI.encode()).hexdigest():
                foundTheConnection = True
                try:
                    if self.engineObj:
                        self.engineObj.dispose()
                        daqbrokerDatabase.daqbroker_database = daqbrokerDatabase.newMetaData()
                    self.engineObj = create_engine(self.uri)
                    self.conn = self.engineObj.connect()
                    self.engineObjSettings = self.conns[i]["settinsObj"]
                    self.uriHome = self.conns[i]["uriHome"]
                    self.engine = self.conns[i]["engine"]
                    self.server = self.conns[i]["server"]
                    self.username = self.conns[i]["username"]
                    self.password = self.conns[i]["password"]
                    self.conns[i] = {
                        'password': self.conns[i]["password"],
                        'username': self.conns[i]["username"],
                        'server': self.conns[i]["server"],
                        'engine': self.conns[i]["engine"],
                        'uriHome': self.uriHome,
                        'engineObj': self.engineObj,
                        'settinsObj': self.engineObjSettings,
                        'conn': self.conn,
                        'id': hashlib.sha224(
                            newURI.encode()).hexdigest()}
                except Exception as e:
                    self.conn = False
                    message = Markup(
                        '<p class="errorExcept"><span style="color:#dc3545">Error : ' +
                        str(e) +
                        '</span></p>')
                    flash(message)
                    traceback.print_exc()
                break
        if not foundTheConnection:
            try:
                self.engineObj = create_engine(self.uri)
                self.engineObjSettings = create_engine(self.uriSettings)
                self.type = user.type
                self.conn = self.engineObj.connect()
                self.conns.append({'password': self.password,
                                   'username': self.username,
                                   'server': self.server,
                                   'engine': self.engine,
                                   'uriHome': self.uriHome,
                                   'engineObj': self.engineObj,
                                   'settinsObj': self.engineObjSettings,
                                   'conn': self.conn,
                                   'id': hashlib.sha224(newURI.encode()).hexdigest()})
            except Exception as e:
                self.conn = False
                message = Markup('<p class="errorExcept"><span style="color:#dc3545">Error : ' + str(e) + '</span></p>')
                flash(message)
                traceback.print_exc()

    def get_id(self):
        return self.id

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated


base_dir = '.'
if getattr(sys, 'frozen', False):
    base_dir = os.path.join(sys._MEIPASS)

def createApp(theServers=None, theWorkers=None, localEngine=None):
    logHandler = ConcurrentRotatingFileHandler(os.path.join(base_dir, 'server.log'), "a", maxBytes=10000, backupCount=1)
    logHandler.setLevel(logging.DEBUG)
    app = Flask(__name__, static_folder=os.path.join(base_dir, 'static'), template_folder=os.path.join(base_dir, 'templates'))
    app.register_blueprint(daqbroker, url_prefix='/daqbroker')
    app.register_blueprint(instrumentsBP, url_prefix='/instruments')
    app.register_blueprint(monitoringBP, url_prefix='/monitoring')
    app.register_blueprint(dataBP, url_prefix='/data')
    app.register_blueprint(runsBP, url_prefix='/runs')
    app.register_blueprint(adminBP, url_prefix='/admin')
    # app.register_blueprint(daqbroker,url_prefix='/daqbroker')
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(logHandler)
    app.secret_key = os.urandom(24)
    app.config['servers'] = theServers
    app.config['workers'] = theWorkers
    app.config['localEngine'] = localEngine

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        """ Something """
        found = False
        for user in usersArray:
            user.is_active()
            if user_id == user.id:
                if request.method == 'POST':
                    requestCheck = request.form
                else:
                    requestCheck = request.args
                if 'dbname' in requestCheck:
                    database = requestCheck["dbname"]
                elif 'database' in requestCheck:
                    database = requestCheck["database"]
                elif user.database:
                    database = user.database
                else:
                    database = None
                if 'username' in requestCheck:
                    user.username = requestCheck['username']
                elif 'user' in requestCheck:
                    user.username = requestCheck['user']
                if 'password' in requestCheck:
                    user.password = requestCheck['password']
                elif 'pass' in requestCheck:
                    user.password = requestCheck['pass']
                if 'serverName' in requestCheck:
                    user.server = requestCheck['serverName']
                elif 'server' in requestCheck:
                    user.server = requestCheck['server']
                elif 'newServerName' in requestCheck:
                    user.server = requestCheck['newServerName']
                if 'serverEngine' in requestCheck:
                    user.engine = requestCheck['serverEngine']
                elif 'engine' in requestCheck:
                    user.engine = requestCheck['engine']
                elif 'newServerEngine' in requestCheck:
                    user.engine = requestCheck['newServerEngine']
                Session = sessionmaker(bind=user.engineObjSettings)
                session = Session()
                thisUser = session.query(daqbrokerSettings.users).filter_by(username=user.username).first()
                if thisUser:
                    user.type = thisUser.type
                session.close()
                newURI = user.engine + "://" + user.username + ":" + user.password + "@" + user.server
                if database:
                    newURI = user.engine + "://" + user.username + ":" + user.password + "@" + user.server + '/daqbro_' + database
                if not (newURI == user.uri):
                    if database and (not database == user.database):
                        user.database = database
                        user.uri = user.engine + "://" + user.username + ":" + user.password + "@" + user.server + '/daqbro_' + user.database
                        user.uriHome = user.engine + "://" + user.username + ":" + user.password + "@" + user.server
                    user.updateDB()
                if user.database:
                    daqbrokerDatabase.daqbroker_database.metadata.reflect(user.engineObj, extend_existing=True)
                return user
        if not found:
            None

    @login_manager.unauthorized_handler
    def unauthorized():
        session["CURRENT_URL"] = request.path
        return redirect(url_for('login'), code=307)

    # @app.after_request
    # def apply_caching(response):
    #	session.pop('_csrf_token', None)
    #	response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    #	return response

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """ Start a session or update an existing session with a login with a given user to a specific database. A database server is defined by an address and a database engine. Only one user is allowed to be connected to a single database server at any time. This request is always run for session start automatically for any request. For single command line requests, these parameters MUST be supplied apart from the target request parameters unless the user uses already existing sessions, which is unusual. It is also required to run to connect to a new server, and the user does not have credentials for said server

        .. :quickref: Log to server; Login to a specified server and engine

        :param: username: (String) username
        :param: user: (String) alias of  **username**
        :param: password: (String) user password
        :param: pass: (String) alias of  **password**
        :param: serverName: (String) server address to connect to. Defaults to 'localhost'
        :param: server: (String) alias of  **serverName**
        :param: serverEngine: (String) server address to connect to
        :param: engine: (String) alias of  **serverEngine**
        :param: database: (String - optional) DAQBroker database to point server session
        :param: engine: (String - optional) alias of  **database**


        """
        browserList = [
            'aol',
            'ask',
            'baidu',
            'bing',
            'camino',
            'chrome',
            'firefox',
            'galeon',
            'google',
            'kmeleon',
            'konqueror',
            'links',
            'lynx',
            'mozilla',
            'msie',
            'msn',
            'netscape',
            'opera',
            'safari',
            'seamonkey',
            'webkit',
            'yahoo']
        if request.method == 'POST':
            if request.is_json:
                requestCheck = request.get_json()
            else:
                requestCheck = request.form
            allGood = True
            loginCreds = {}
            if 'username' in requestCheck:
                loginCreds['username'] = requestCheck['username']
            elif 'user' in requestCheck:
                loginCreds['username'] = requestCheck['user']
            else:
                allGood = False
            if 'password' in requestCheck:
                loginCreds['password'] = requestCheck['password']
            elif 'pass' in requestCheck:
                loginCreds['password'] = requestCheck['pass']
            else:
                allGood = False
            if 'serverName' in requestCheck:
                loginCreds['server'] = requestCheck['serverName']
            elif 'server' in requestCheck:
                loginCreds['server'] = requestCheck['server']
            elif 'newServerName' in requestCheck:
                loginCreds['server'] = requestCheck['newServerName']
            else:
                # allGood=False
                loginCreds['server'] = "localhost"
            if 'serverEngine' in requestCheck:
                loginCreds['engine'] = requestCheck['serverEngine']
            elif 'engine' in requestCheck:
                loginCreds['engine'] = requestCheck['engine']
            elif 'newServerEngine' in requestCheck:
                loginCreds['engine'] = requestCheck['newServerEngine']
            else:
                # allGood=False
                loginCreds['engine'] = 'mysql'
            if 'database' in requestCheck:
                loginCreds['database'] = requestCheck['database']
            if 'dbname' in requestCheck:
                loginCreds['database'] = requestCheck['dbname']
            if allGood:
                if 'database' in loginCreds:
                    user = User(
                        loginCreds['username'],
                        loginCreds['password'],
                        loginCreds['server'],
                        loginCreds['engine'],
                        loginCreds['database'])
                else:
                    user = User(
                        loginCreds['username'],
                        loginCreds['password'],
                        loginCreds['server'],
                        loginCreds['engine'])
                if user.id:
                    usersArray.append(user)
                    login_user(user)
                    scoped = daqbrokerSettings.getScoped()
                    localSession = scoped()
                    newServer = daqbrokerSettings.servers(server=loginCreds["server"], engine=loginCreds["engine"])
                    localSession.merge(newServer)
                    localSession.commit()
                else:
                    if request.user_agent.browser not in browserList:
                        raise InvalidUsage('Error connecting to database', status_code=500)
                    else:
                        return render_template('login.html')
                if "CURRENT_URL" in session:
                    next = session["CURRENT_URL"]
                    session.pop("CURRENT_URL", None)
                else:
                    next = None
                if not request.user_agent.browser:
                    return redirect(next or url_for('daqbroker.main'), code=307)
                else:
                    return redirect(next or url_for('daqbroker.main'))
            else:
                if request.user_agent.browser not in browserList:
                    raise InvalidUsage('Error connecting to database', status_code=500)
                else:
                    return render_template('login.html')
        else:
            return render_template('login.html')

    @app.route("/logout")
    def logout():
        """ End the user login session by loging out of all currnetly connected database servers

        .. :quickref: End session; End previously logged in session

        """
        message = Markup('<p class="loggedOut"><span style="color:#28a745">Successfully logged out</span></p>')
        flash(message)
        logout_user()
        return redirect(url_for('login'))

    app.jinja_env.globals['csrf_token'] = generate_csrf_token
    app.jinja_env.globals['daqbroker_server'] = getServer
    app.jinja_env.globals['daqbroker_engine'] = getEngine
    app.jinja_env.globals['daqbroker_usertype'] = getusertype

    return app

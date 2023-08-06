import concurrent.futures
import multiprocessing
from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Text, Binary, LargeBinary, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Currently an sqlite local file database - should allow users to provide an engine for this database maybe
localEngine = None #create_engine("sqlite:///localSettings")
Session = None #sessionmaker(bind=localEngine)
# Thread safe session factory (as long as you commit or rollback your changes every time)
scoped = None #scoped_session(Session)

def setupLocalVars(dbpath):

    global localEngine
    global Session
    global scoped

    localEngine = create_engine("sqlite:///" + dbpath)
    Session = sessionmaker(bind=localEngine)
    scoped = scoped_session(Session)

def getScoped():

    return scoped

daqbroker_settings = declarative_base()

workerpool = concurrent.futures.ThreadPoolExecutor(
        max_workers=multiprocessing.cpu_count() * 2)  # Using threads

#manager = multiprocessing.Manager()
#workers = manager.list()
#for i in range(0, 10000):
#    workers.append(-1)

class databases(daqbroker_settings):

    __tablename__ = "databases"
    dbname = Column(String(50), primary_key=True)
    active = Column(Boolean)


class users(daqbroker_settings):
    __tablename__ = "users"
    username = Column(String(25), primary_key=True)
    type = Column(Integer)


class links(daqbroker_settings):
    __tablename__ = "links"
    clock = Column(BigInteger)
    linkid = Column(String(25), primary_key=True)
    site = Column(Text)
    variable = Column(Text)

# Local machine-specific tables


daqbroker_settings_local = declarative_base()

# localConn.execute(" CREATE TABLE `global` ( `clock` bigint(20) NOT NULL, `version` varchar(10) NOT NULL, `backupfolder` varchar(100) NOT NULL, `importfolder` varchar(100) NOT NULL, `addonfolder` varchar(100) NOT NULL, `ntp` varchar(20) NOT NULL, `logport` int(20) NOT NULL, `commport` int(20) NOT NULL, `remarks` text NOT NULL, PRIMARY KEY (`version`)) ")


class Global(daqbroker_settings_local):
    __tablename__ = "global"
    clock = Column(BigInteger)
    version = Column(String(50), primary_key=True)
    backupfolder = Column(String(100))
    importfolder = Column(String(100))
    tempfolder = Column(String(100))
    ntp = Column(String(50))
    logport = Column(Integer)
    commport = Column(Integer)
    remarks = Column(Text)

# localConn.execute(" CREATE TABLE `servers` (`server` varchar(50), `engine` varchar(50), PRIMARY KEY (`server`,`engine`)) ")


class servers(daqbroker_settings_local):
    __tablename__ = "servers"
    server = Column(String(50), primary_key=True)
    engine = Column(String(50), primary_key=True)

# localConn.execute(" CREATE TABLE `ntp` ( `clock` bigint(20) NOT NULL, `server` varchar(30) NOT NULL, `port` int(11) NOT NULL, PRIMARY KEY (`server`))")


class ntp(daqbroker_settings_local):
    __tablename__ = "ntp"
    clock = Column(BigInteger)
    server = Column(String(50), primary_key=True)
    port = Column(Integer)

# localConn.execute(" CREATE TABLE `folder` ( `clock` bigint(20) NOT NULL, `path` varchar(100) NOT NULL, `type` int(11) NOT NULL, `remarks` text NOT NULL, PRIMARY KEY (`path`))")


class folder(daqbroker_settings_local):
    __tablename__ = "folder"
    clock = Column(BigInteger)
    path = Column(String(100), primary_key=True)
    type = Column(Integer)
    remarks = Column(Text)

# localConn.execute(" CREATE TABLE `nodes` ( `node` varchar(50) NOT NULL, `name` varchar(50), `address` varchar(50) NOT NULL, `port` int(11) NOT NULL, `local` varchar(50) NOT NULL, `active` tinyint(1) NOT NULL, `lastActive` bigint(20) NOT NULL, `tsyncauto` tinyint(1) NOT NULL DEFAULT '0', `remarks` text NOT NULL, PRIMARY KEY (`node`))")


class nodes(daqbroker_settings_local):
    __tablename__ = "nodes"
    node = Column(String(50), primary_key=True)
    name = Column(String(50))
    address = Column(String(50))
    port = Column(Integer)
    local = Column(String(50))
    active = Column(Boolean)
    lastActive = Column(BigInteger)
    tsyncauto = Column(Boolean)
    remarks = Column(Text)

#connection.execute("CREATE TABLE `jobs` (`clock` BIGINT(11),`jobid` VARCHAR(50),`type` TEXT,`username` TEXT,`status` INT,`data` TEXT,`error` TEXT,`reqid` TEXT, PRIMARY KEY(jobid))")


class jobs(daqbroker_settings_local):
    __tablename__ = "jobs"
    clock = Column(BigInteger)
    jobid = Column(String(50), primary_key=True)
    type = Column(Text)
    username = Column(Text)
    status = Column(Integer)
    data = Column(Text)
    error = Column(Text)
    reqid = Column(Text)

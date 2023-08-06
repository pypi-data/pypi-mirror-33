from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
#from sqlalchemy_views import CreateView, DropView

# connection.execute("CREATE TABLE `jobs` (`clock` BIGINT(11),`jobid` VARCHAR(50),`type` TEXT,`username` TEXT,`status` INT,`data` TEXT,`error` TEXT,`reqid` TEXT, PRIMARY KEY(jobid))")
# connection.execute("CREATE TABLE `data_raw` (`clock` BIGINT(11), PRIMARY KEY(clock))")
# connection.execute("CREATE TABLE `data_finalized` (`clock` BIGINT(11), PRIMARY KEY(clock))")
# connection.execute("CREATE TABLE `data_processed` (`clock` BIGINT(11), PRIMARY KEY(clock))")
# connection.execute("CREATE TABLE `data_other` (`clock` BIGINT(11), PRIMARY KEY(clock))")
# connection.execute(text("INSERT INTO `daqbroker_settings`.`databases` VALUES(:dbname,'0')"),dbname=newdbname)

daqbroker_database = declarative_base()

#connection.execute("CREATE TABLE `instruments` ( `Name` text NOT NULL, `instid` int(11) NOT NULL, `active` int(11) NOT NULL, `description` text NOT NULL, `username` text NOT NULL, `email` text NOT NULL, `insttype` int(11) NOT NULL,`log` text, PRIMARY KEY (`instid`))")


class instruments(daqbroker_database):
    __tablename__ = "instruments"

    Name = Column(String(50))
    instid = Column(Integer, primary_key=True)
    active = Column(Boolean)
    description = Column(Text)
    username = Column(Text)
    email = Column(Text)
    insttype = Column(Integer)
    log = Column(Text)

    sources = relationship("instmeta", backref="meta", cascade="all, delete, delete-orphan", order_by="instmeta.metaid")

#connection.execute("CREATE TABLE `instmeta` (`clock` bigint(11) NOT NULL DEFAULT '0', `name` varchar(50) NOT NULL, `metaid` int(11) NOT NULL DEFAULT '0', `instid` int(11) NOT NULL DEFAULT '0', `type` int(11) DEFAULT '0', `node` varchar(50) NOT NULL, `remarks` text, `sentRequest` tinyint(1) DEFAULT '0', `lastAction` bigint(11) NOT NULL DEFAULT '0', `lasterrortime` bigint(11) NOT NULL DEFAULT '0', `lasterror` text, `lockSync` tinyint(1) DEFAULT '0', PRIMARY KEY (`instid`,`metaid`,`name`))")


class instmeta(daqbroker_database):
    __tablename__ = "instmeta"

    clock = Column(BigInteger)
    name = Column(String(50))
    metaid = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, ForeignKey('instruments.instid'))
    type = Column(Integer)
    node = Column(String(50))
    remarks = Column(Text)
    sentRequest = Column(Boolean)
    lastAction = Column(BigInteger)
    lasterrortime = Column(BigInteger)
    lasterror = Column(Text)
    lockSync = Column(Boolean)

    channels = relationship("channels", backref="chann", cascade="all, delete, delete-orphan", order_by="channels.channelid")
    parsing = relationship("parsing", backref="metaParse", cascade="all, delete, delete-orphan")

#connection.execute("CREATE TABLE `channels` (`Name` text NOT NULL, `channelid` int(11) NOT NULL, `channeltype` int(11) NOT NULL, `valuetype` int(11) NOT NULL DEFAULT '0', `units` text NOT NULL, `instid` int(11) NOT NULL, `description` text NOT NULL, `active` int(11) NOT NULL, `remarks` text NOT NULL, `metaid` INT, `lastclock` BIGINT(11) NOT NULL DEFAULT 0, `lastValue` text, `fileorder` int(11) DEFAULT 0,`alias` text NOT NULL,`firstClock` BIGINT(11) DEFAULT 10000000000000, PRIMARY KEY (channelid,metaid,instid))")


class channels(daqbroker_database):
    __tablename__ = "channels"

    Name = Column(Text)
    channelid = Column(Integer, primary_key=True)
    channeltype = Column(Integer)
    valuetype = Column(Integer)
    units = Column(Text)
    description = Column(Text)
    active = Column(Boolean)
    remarks = Column(Text)
    metaid = Column(Integer, ForeignKey('instmeta.metaid'))
    lastclock = Column(BigInteger)
    lastValue = Column(Text)
    firstClock = Column(BigInteger)
    fileorder = Column(Text)
    alias = Column(Text)

    #chann = relationship("instmeta", back_populates="channels")

#connection.execute("CREATE TABLE `parsing` (clock BIGINT(11),lastAction BIGINT(11), `metaid` INT(11) , `instid` INT(11), `type` INT(11), `locked` INT(11), `forcelock` BOOLEAN DEFAULT '0', `remarks` MEDIUMTEXT, PRIMARY KEY (metaid,instid))")


class parsing(daqbroker_database):
    __tablename__ = "parsing"

    clock = Column(BigInteger)
    metaid = Column(Integer, ForeignKey('instmeta.metaid'), primary_key=True)
    type = Column(Integer)
    locked = Column(Boolean)
    forcelock = Column(Boolean)
    remarks = Column(Text)

    #metaParse = relationship("instmeta", back_populates="parsing")

#connection.execute("CREATE TABLE `plots` ( `plotname` varchar(200) NOT NULL, `plotid` int(11) NOT NULL, `channelids` text NOT NULL, `plottype` int(11) NOT NULL, `adminPlot` int(11) NOT NULL, `active` int(11) NOT NULL, `remarks` text NOT NULL, PRIMARY KEY (`plotname`,`plotid`))")


class plots(daqbroker_database):
    __tablename__ = "plots"

    plotname = Column(String(200))
    plotid = Column(Integer, primary_key=True)
    channelids = Column(Text)
    plottype = Column(Integer)
    adminPlot = Column(Boolean)
    active = Column(Boolean)
    remarks = Column(Text)

#connection.execute("CREATE TABLE `plotcomments` (`clock` BIGINT(11),`plotid` INT,`channelid` INT,`comment` TEXT,`author` TEXT,`remarks` TEXT, PRIMARY KEY(clock,plotid,channelid))")


class plotcomments(daqbroker_database):
    __tablename__ = "plotcomments"

    clock = Column(BigInteger, primary_key=True)
    plotid = Column(Integer, primary_key=True)
    channelid = Column(Integer, primary_key=True)
    comment = Column(Text)
    author = Column(Text)
    remarks = Column(Text)

#connection.execute("CREATE TABLE `layouts` (`Name` varchar(50) NOT NULL,`layoutid` int(11) NOT NULL,`plots` text NOT NULL,`format` text NOT NULL,PRIMARY KEY (`layoutid`) USING BTREE,UNIQUE KEY `Name` (`Name`))")


class layouts(daqbroker_database):
    __tablename__ = "layouts"

    Name = Column(String(200))
    layoutid = Column(Integer, primary_key=True)
    plots = Column(Text)
    format = Column(Text)
    plottype = Column(Integer)
    adminPlot = Column(Boolean)
    active = Column(Boolean)
    remarks = Column(Text)

#connection.execute("CREATE TABLE `collections` (`Name` VARCHAR(30),`channels` TEXT,`remarks` TEXT, PRIMARY KEY(Name))")


class collections(daqbroker_database):
    __tablename__ = "collections"

    Name = Column(String(200), primary_key=True)
    channels = Column(Text)
    remarks = Column(Text)

#connection.execute("CREATE TABLE `runs` (`clock` BIGINT(11),`lastUpdate` BIGINT(11),`isLinked` INT(11),`linkRemarks` TEXT,`linkType` INT(11),`runlistRemarks` TEXT, PRIMARY KEY (clock))")


class runs(daqbroker_database):
    __tablename__ = "runs"

    clock = Column(BigInteger, primary_key=True)
    lastUpdate = Column(BigInteger)
    isLinked = Column(Boolean)
    linkRemarks = Column(Text)
    linkType = Column(Integer)
    runlistRemarks = Column(Text)

#connection.execute("CREATE TABLE `runlist` (`start` BIGINT(11),`end` BIGINT(11),`run` VARCHAR(50),`summary` LONGTEXT,`comments` TEXT,`active` INT, PRIMARY KEY(run))")


class runlist(daqbroker_database):
    __tablename__ = "runlist"

    start = Column(BigInteger)
    end = Column(BigInteger)
    run = Column(String(20), primary_key=True)
    lastUpdate = Column(BigInteger)
    summary = Column(Text)
    comments = Column(Text)
    active = Column(Boolean)

#connection.execute("CREATE TABLE `subscribers` (`email` VARCHAR(100), PRIMARY KEY(email))")


class subscribers(daqbroker_database):
    __tablename__ = "subscribers"

    email = Column(String(200), primary_key=True)


class instTable(object):
    def __init__(self, cols):
        for key in cols:
            setattr(self, key, cols[key])

    def __repr__(self):
        return "<instTable class>"

def createInstrumentTable(iname, cols, isNew):
    attrDictData = {'__tablename__': iname + '_data', 'clock': Column(BigInteger, primary_key=True)}  # For raw data
    attrDictCustom = {
        '__tablename__': iname + '_custom',
        'clock': Column(
            BigInteger,
            primary_key=True)}  # For custom (processed) data
    for col in cols:
        if col["type"] == 1:
            attrDictData[col["name"]] = Column(Float)
        if col["type"] == 2:
            attrDictData[col["name"]] = Column(Text)
        if col["type"] == 3:
            attrDictCustom[col["name"]] = Column(Float)
    #tableClassData = type (instTable, (attrDictData)
    if not isNew:
        tableClassData = type(iname + '_data', (instTable,), attrDictData)
        tableClassCustom = type(iname + '_custom', (instTable,), attrDictCustom)
    else:
        tableClassData = type(iname + '_data', (daqbroker_database,), attrDictData)
        tableClassCustom = type(iname + '_custom', (daqbroker_database,), attrDictCustom)
    return (tableClassData,tableClassCustom)


def dropTable(tableName, engine, is_view):
    tablesDrop = []
    tablesDropKeys = []
    for table in daqbroker_database.metadata.tables.keys():
        if table == tableName:
            tablesDrop.append(daqbroker_database.metadata.tables[table])
            tablesDropKeys.append(table)
    if is_view:
        for table in tablesDrop:
            engine.execute(DropView(table, if_exists=True))
    else:
        daqbroker_database.metadata.drop_all(engine, tables=tablesDrop)
    for table in tablesDropKeys:
        daqbroker_database.metadata.remove(daqbroker_database.metadata.tables[table])

def newMetaData():
    global daqbroker_database
    daqbroker_database.metadata.clear()
    daqbroker_database = declarative_base()

    instruments = type('instruments', (daqbroker_database,), dict(
        __tablename__="instruments",
        Name=Column(String(50)),
        instid=Column(Integer, primary_key=True),
        active=Column(Boolean),
        description=Column(Text),
        username=Column(Text),
        email=Column(Text),
        insttype=Column(Integer),
        log=Column(Text),
        sources=relationship("instmeta", backref="meta", cascade="all, delete, delete-orphan", order_by="instmeta.metaid"))
    )

    instmeta = type('instmeta', (daqbroker_database,), dict(
        __tablename__="instmeta",
        clock=Column(BigInteger),
        name=Column(String(50)),
        metaid=Column(Integer, primary_key=True),
        instrument_id=Column(Integer, ForeignKey('instruments.instid')),
        type=Column(Integer),
        node=Column(String(50)),
        remarks=Column(Text),
        sentRequest=Column(Boolean),
        lastAction=Column(BigInteger),
        lasterrortime=Column(BigInteger),
        lasterror=Column(Text),
        lockSync=Column(Boolean),
        channels=relationship("channels", backref="chann", cascade="all, delete, delete-orphan", order_by="channels.channelid"),
        parsing=relationship("parsing", backref="metaParse", cascade="all, delete, delete-orphan"))
    )

    channels = type('channels', (daqbroker_database,), dict(
        __tablename__="channels",
        Name = Column(Text),
        channelid = Column(Integer, primary_key=True),
        channeltype = Column(Integer),
        valuetype = Column(Integer),
        units = Column(Text),
        description = Column(Text),
        active = Column(Boolean),
        remarks = Column(Text),
        metaid = Column(Integer, ForeignKey('instmeta.metaid')),
        lastclock = Column(BigInteger),
        lastValue = Column(Text),
        firstClock = Column(BigInteger),
        fileorder = Column(Text),
        alias = Column(Text)
    ))
    parsing = type('parsing', (daqbroker_database,), dict(
        __tablename__="parsing",
        clock = Column(BigInteger),
        metaid = Column(Integer, ForeignKey('instmeta.metaid'), primary_key=True),
        type = Column(Integer),
        locked = Column(Boolean),
        forcelock = Column(Boolean),
        remarks = Column(Text)
    ))
    plots = type('plots', (daqbroker_database,), dict(
        __tablename__="plots",
        plotname = Column(String(200)),
        plotid = Column(Integer, primary_key=True),
        channelids = Column(Text),
        plottype = Column(Integer),
        adminPlot = Column(Boolean),
        active = Column(Boolean),
        remarks = Column(Text)
    ))
    plotcomments = type('plotcomments', (daqbroker_database,), dict(
        __tablename__="plotcomments",
        clock = Column(BigInteger, primary_key=True),
        plotid = Column(Integer, primary_key=True),
        channelid = Column(Integer, primary_key=True),
        comment = Column(Text),
        author = Column(Text),
        remarks = Column(Text),
    ))
    layouts = type('layouts', (daqbroker_database,), dict(
        __tablename__="layouts",
        Name = Column(String(200)),
        layoutid = Column(Integer, primary_key=True),
        plots = Column(Text),
        format = Column(Text),
        plottype = Column(Integer),
        adminPlot = Column(Boolean),
        active = Column(Boolean),
        remarks = Column(Text)
    ))
    runs = type('runs', (daqbroker_database,), dict(
        __tablename__="runs",
        clock = Column(BigInteger, primary_key=True),
        lastUpdate = Column(BigInteger),
        isLinked = Column(Boolean),
        linkRemarks = Column(Text),
        linkType = Column(Integer),
        runlistRemarks = Column(Text)
    ))
    runlist = type('runlist', (daqbroker_database,), dict(
        __tablename__="runlist",
        start = Column(BigInteger),
        end = Column(BigInteger),
        run = Column(String(20), primary_key=True),
        lastUpdate = Column(BigInteger),
        summary = Column(Text),
        comments = Column(Text),
        active = Column(Boolean)
    ))
    collections = type('collections', (daqbroker_database,), dict(
        __tablename__="collections",
        Name = Column(String(200), primary_key=True),
        channels = Column(Text),
        remarks = Column(Text)
    ))

    collections = type('collections', (daqbroker_database,), dict(
        __tablename__="subscribers",
        email=Column(String(200), primary_key=True)
    ))

    return daqbroker_database
import time

from sqlalchemy import Column, Integer, Sequence, String, Boolean, BLOB, ForeignKey, PickleType, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(50), nullable=False)
    password = Column(String, nullable=False)
    api_token = Column(String(50))
    last_logon_time = Column(String(50))  # DateTime # todo vr rename
    enabled = Column(Boolean, nullable=False)
    admin = Column(Boolean, nullable=False)

    def __repr__(self):
        return "<User(username='%s')>" % (
            self.username)


class Listener(Base):
    __tablename__ = 'listeners'
    id = Column(Integer, Sequence("listener_id_seq"), primary_key=True)
    name = Column(String, nullable=False, unique=True)
    module = Column(String, nullable=False)
    listener_type = Column(String, nullable=False)
    listener_category = Column(String, nullable=False)
    enabled = Column(Boolean, nullable=False)
    options = Column(PickleType)

    def __repr__(self):
        return "<Listener(name='%s')>" % (
            self.name)


class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, Sequence("agent_id_seq"), primary_key=True)
    name = Column(String, nullable=False)
    listener = Column(String, nullable=False)  # join?
    session_id = Column(String)
    language = Column(String)
    language_version = Column(String)
    delay = Column(Integer)
    jitter = Column(Float)
    external_ip = Column(String)
    internal_ip = Column(String)
    username = Column(String)
    high_integrity = Column(Integer)
    process_name = Column(String)
    process_id = Column(String)
    hostname = Column(String)
    os_details = Column(String)
    session_key = Column(BLOB)
    nonce = Column(String)
    checkin_time = Column(String)
    lastseen_time = Column(String)
    parent = Column(String)
    children = Column(String)
    servers = Column(String)
    profile = Column(String)
    functions = Column(String)
    kill_date = Column(String)
    working_hours = Column(String)
    lost_limit = Column(Integer)
    taskings = Column(String)  # Queue of tasks. Should refactor to manage queued tasks from the taskings table itself.
    taskings_executed = relationship("Tasking")
    results = relationship("Result")

    @hybrid_property
    def stale(self):
        interval_max = (self.delay + self.delay * self.jitter) + 30
        agent_time = time.mktime(time.strptime(self.lastseen_time, "%Y-%m-%d %H:%M:%S"))
        stale = agent_time < time.mktime(time.localtime()) - interval_max

        return stale

    def __repr__(self):
        return "<Agent(name='%s')>" % (
            self.name)


class Config(Base):
    __tablename__ = 'config'
    staging_key = Column(String, nullable=False, primary_key=True)  # TODO Revisit max length
    install_path = Column(String, nullable=False)
    ip_whitelist = Column(String, nullable=False)
    ip_blacklist = Column(String, nullable=False)
    autorun_command = Column(String, nullable=False)
    autorun_data = Column(String, nullable=False)
    rootuser = Column(Boolean, nullable=False)
    obfuscate = Column(Integer, nullable=False)
    obfuscate_command = Column(String, nullable=False)

    def __repr__(self):
        return "<Config(staging_key='%s')>" % (
            self.staging_key)


class Credential(Base):
    __tablename__ = 'credentials'
    id = Column(Integer, Sequence("credential_id_seq"), primary_key=True)
    credtype = Column(String)
    domain = Column(String)
    username = Column(String)
    password = Column(String)
    host = Column(String)
    os = Column(String)
    sid = Column(String)
    notes = Column(String)

    def __repr__(self):
        return "<Credential(id='%s')>" % (
            self.id)


# TODO vr I'd like to merge taskings and results to a single table
#  and get rid of the json queue array on Agent.
class Tasking(Base):
    __tablename__ = 'taskings'
    id = Column(Integer, primary_key=True)
    agent = Column(String, ForeignKey('agents.id'), primary_key=True)
    data = Column(String)
    user_id = Column(String, ForeignKey('users.id'))
    time_stamp = Column(String)  # TODO Dates?

    def __repr__(self):
        return "<Tasking(id='%s')>" % (
            self.id)


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)  # Current implementation requires this to match Tasking's id
    agent = Column(String, ForeignKey('agents.id'), primary_key=True)
    data = Column(String)
    user_id = Column(String)

    def __repr__(self):
        return "<Result(id='%s')>" % (
            self.id)


class Reporting(Base):
    __tablename__ = 'reporting'
    id = Column(Integer, Sequence("reporting_id_seq"), primary_key=True)
    name = Column(String, nullable=False)
    event_type = Column(String)
    message = Column(String)
    time_stamp = Column(String)
    taskID = Column(Integer, ForeignKey('results.id'))  # Should be task_id. might be result.id

    def __repr__(self):
        return "<Reporting(id='%s')>" % (
            self.id)


# TODO there's probably a better way to lay this one out
class Function(Base):
    __tablename__ = "functions"
    id = Column(Integer, Sequence("functions_id_seq"), primary_key=True)
    invoke_empire = Column(String)
    invoke_mimikatz = Column(String)

    def __repr__(self):
        return "<Function(id='%s')>" % (
            self.id)

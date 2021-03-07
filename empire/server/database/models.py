from datetime import datetime, timezone

from sqlalchemy import Column, Integer, Sequence, String, Boolean, ForeignKey, PickleType, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utc import UtcDateTime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    api_token = Column(String(50))
    last_logon_time = Column(UtcDateTime)
    enabled = Column(Boolean, nullable=False)
    admin = Column(Boolean, nullable=False)
    notes = Column(Text)

    def __repr__(self):
        return "<User(username='%s')>" % (
            self.username)


class Listener(Base):
    __tablename__ = 'listeners'
    id = Column(Integer, Sequence("listener_id_seq"), primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    module = Column(String(255), nullable=False)
    listener_type = Column(String(255), nullable=True)
    listener_category = Column(String(255), nullable=False)
    enabled = Column(Boolean, nullable=False)
    options = Column(PickleType)  # Todo Json?
    created_at = Column(UtcDateTime, nullable=False)

    def __repr__(self):
        return "<Listener(name='%s')>" % (
            self.name)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, Sequence("agent_id_seq"), primary_key=True)
    name = Column(String(255), nullable=False)
    listener = Column(String(255), nullable=False)
    session_id = Column(String(255), nullable=False, unique=True)
    language = Column(String(255))
    language_version = Column(String(255))
    delay = Column(Integer)
    jitter = Column(Float)
    external_ip = Column(String(255))
    internal_ip = Column(String(255))
    username = Column(Text)
    high_integrity = Column(Boolean)
    process_name = Column(Text)
    process_id = Column(Integer)
    hostname = Column(String(255))
    os_details = Column(String(255))
    session_key = Column(String(255))
    nonce = Column(String(255))
    checkin_time = Column(UtcDateTime)
    lastseen_time = Column(UtcDateTime)
    parent = Column(String(255))
    children = Column(String(255))
    servers = Column(String(255))
    profile = Column(String(255))
    functions = Column(String(255))
    kill_date = Column(String(255))
    working_hours = Column(String(255))
    lost_limit = Column(Integer)
    taskings = Column(String(255))  # Queue of tasks. Should refactor to manage queued tasks from the taskings table itself.
    results = Column(String(255))
    notes = Column(Text)
    killed = Column(Boolean, nullable=False)

    @hybrid_property # todo @stale.expression
    def stale(self):
        return is_stale(self.lastseen_time, self.delay, self.jitter)

    def __repr__(self):
        return "<Agent(name='%s')>" % (
            self.name)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value


class AgentFile(Base):
    __tablename__ = 'agent_files'
    id = Column(Integer, primary_key=True)
    session_id = Column(String(50))
    name = Column(Text, nullable=False)
    path = Column(Text, nullable=False)
    is_file = Column(Boolean, nullable=False)
    parent_id = Column(Integer, ForeignKey('agent_files.id', ondelete='CASCADE'), nullable=True)


class Config(Base):
    __tablename__ = 'config'
    staging_key = Column(String(255), primary_key=True)
    install_path = Column(Text, nullable=False)
    ip_whitelist = Column(Text, nullable=False)
    ip_blacklist = Column(Text, nullable=False)
    autorun_command = Column(Text, nullable=False)
    autorun_data = Column(Text, nullable=False)
    rootuser = Column(Boolean, nullable=False)
    obfuscate = Column(Boolean, nullable=False)
    obfuscate_command = Column(Text, nullable=False)

    def __repr__(self):
        return "<Config(staging_key='%s')>" % (
            self.staging_key)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value


class Credential(Base):
    __tablename__ = 'credentials'
    id = Column(Integer, Sequence("credential_id_seq"), primary_key=True)
    credtype = Column(String(255))
    domain = Column(Text)
    username = Column(Text)
    password = Column(Text)
    host = Column(Text)
    os = Column(String(255))
    sid = Column(String(255))
    notes = Column(Text)

    def __repr__(self):
        return "<Credential(id='%s')>" % (
            self.id)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value


# TODO vr I'd like to merge taskings and results to a single table
#  and get rid of the json queue array on Agent.
class Tasking(Base):
    __tablename__ = 'taskings'
    id = Column(Integer, primary_key=True)
    agent = Column(String(255), ForeignKey('agents.session_id'), primary_key=True)
    data = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(UtcDateTime, nullable=False)
    module_name = Column(Text)


    def __repr__(self):
        return "<Tasking(id='%s')>" % (
            self.id)


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)  # Current implementation requires this to match Tasking's id
    agent = Column(String(255), ForeignKey('agents.session_id'), primary_key=True)
    data = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return "<Result(id='%s')>" % (
            self.id)


class Reporting(Base):
    __tablename__ = 'reporting'
    id = Column(Integer, Sequence("reporting_id_seq"), primary_key=True)
    name = Column(String(255), nullable=False)
    event_type = Column(String(255))
    message = Column(Text)
    timestamp = Column(UtcDateTime, nullable=False)
    taskID = Column(Integer, ForeignKey('results.id'))

    def __repr__(self):
        return "<Reporting(id='%s')>" % (
            self.id)


class Function(Base):
    __tablename__ = "functions"
    keyword = Column(String(255), primary_key=True)
    replacement = Column(String(255))

    def __repr__(self):
        return "<Function(id='%s')>" % (
            self.id)


def is_stale(lastseen: datetime, delay: int, jitter: float):
    """
    Convenience function for calculating staleness
    """
    interval_max = (delay + delay * jitter) + 30
    diff = getutcnow() - lastseen
    stale = diff.total_seconds() > interval_max
    return stale


def getutcnow():
    return datetime.now(timezone.utc)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from lib import arguments
from lib.database import models
from lib.database.defaults import get_default_user, get_default_config, get_default_functions
from lib.database.models import Base

engine = create_engine('sqlite:///data/' + arguments.args.db, echo=True)

Session = scoped_session(sessionmaker(bind=engine))

Base.metadata.create_all(engine)

# When Empire starts up for the first time, it will create the database and create
# these default records. If ./setup_database.py is run, this same process will happen,
# and then it will overwrite the default records with what is defined in that file.
if len(Session().query(models.User).all()) == 0:
    Session().add(get_default_user())
    Session().commit()
    Session.remove()

if len(Session().query(models.Config).all()) == 0:
    Session().add(get_default_config())
    Session().commit()
    Session.remove()

if len(Session().query(models.Function).all()) == 0:
    Session().add(get_default_functions())
    Session().commit()
    Session.remove()
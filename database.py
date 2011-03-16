from types import ModuleType
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db = ModuleType('db')

db.engine = create_engine('sqlite:////tmp/pastes.db', convert_unicode=True,
                          echo=True)
db.session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                         bind=db.engine))

db.Base = declarative_base()
db.Base.query = db.session.query_property()

def init():
    import ControlPaste.models
    db.Base.metadata.create_all(bind=db.engine)

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

class Database:
    def __init__(self, db_uri):
        self.__engine = db.create_engine(db_uri, echo=True)
        self.__Session = sessionmaker(bind=self.__engine)

    def getEngine(self):
        return self.__engine
    
    def getConnection(self):
        self.__engine.connect()

    def getSession(self):
        return self.__Session()
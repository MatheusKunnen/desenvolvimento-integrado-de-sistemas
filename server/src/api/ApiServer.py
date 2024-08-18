from flask import Flask
from src.db import Database

from .JobView import JobView

class ApiServer:
    __FlaskApp = None
    
    def __init__(self, db: Database):
        self.__db = db

        if ApiServer.__FlaskApp is None:
            ApiServer.__FlaskApp = Flask('ApiServer')

        self.__app = ApiServer.__FlaskApp
        
        JobView.register(self.__app, route_base='/job', init_argument=(self.__db, ...) )

    def run(self):
        self.__app.run(port=5005, debug=True)
    

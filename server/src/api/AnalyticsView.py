from flask import request
from flask_classful import FlaskView

from src.db import Database

from src.models.AppInfo import AppInfo

class AnalyticsView(FlaskView):

    def __init__(self, args):
        self.__db:Database = args[0]
    
    def index(self):
        session = self.__db.getSession()
        try:
            minimal = request.args.get('minimal') == 'true'

            rows = session.query(AppInfo).order_by(AppInfo.created_at.desc()).limit(600).all()
            
            data=[]
            for row in rows:
                data.append(row.getDict(minimal))

            return {'data':data};            
        finally:
            session.close()

    def last(self):
        session = self.__db.getSession()
        try:
            minimal = request.args.get('minimal') == 'true'

            query = session.query(AppInfo).order_by(AppInfo.created_at.desc())
            
            if query.count() == 0:
                return {'error':f"Register {id} not found"}, 404

            return {'data':query.first().getDict(minimal)};            
        finally:
            session.close()

    def get(self, id):
        session = self.__db.getSession()
        try:
            minimal = request.args.get('minimal') == 'true'
            
            query = session.query(AppInfo).filter_by(id=id)

            if query.count() == 0:
                return {'error':f"Register {id} not found"}, 404

            job = query.first()

            return {'data':job.getDict(minimal)};            
        finally:
            session.close()
    
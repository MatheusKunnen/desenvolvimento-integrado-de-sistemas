from flask import request
from flask_classful import FlaskView

from datetime import datetime, timedelta
import numpy as np

from src.db import Database
from src.config import LocalConfig

from src.models.AppInfo import AppInfo

class AnalyticsView(FlaskView):

    def __init__(self, args):
        self.__db:Database = args[0]
    
    def index(self):
        session = self.__db.getSession()
        try:
            minimal = request.args.get('minimal') == 'true'

            rows = session.query(AppInfo).order_by(AppInfo.created_at.desc()).limit(LocalConfig.GetDefault().getAnalyticsRowsLimit()).all()
            
            data=[]
            for row in rows:
                data.append(row.getDict(minimal))

            return {'data':data};            
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

    def summary(self):
        session = self.__db.getSession()
        try:
            from_date = datetime.fromisoformat(request.args.get('from_date').replace('T', ' ')) if  request.args.get('from_date') is not None else datetime.now()
            delta_min = int(request.args.get('delta_min')) if request.args.get('delta_min') is not None else 5
            to_date = from_date - timedelta(minutes=delta_min) 

            query = session.query(AppInfo).filter(AppInfo.created_at.between(to_date, from_date)).order_by(AppInfo.created_at.desc())
            
            if query.count() == 0:
                return {'error':f"No information between {from_date.isoformat()} and {to_date.isoformat()}"}, 404
            rows = query.all()

            main_cpu = np.array([x.main_cpu_pct for x in rows]).flatten()
            main_mem_rss = np.array([x.main_mem_rss for x in rows]).flatten()
            workers_cpu = np.array([x.workers_cpu_pct for x in rows]).flatten()
            workers_mem_rss = np.array([x.workers_mem_rss for x in rows]).flatten()
            workers_count = np.array([x.workers for x in rows]).flatten().min()

            workers = [{'id': id, 'cpu': [], 'rss': []} for id in range(workers_count)]
            for row in rows:
                workers_r = row.getDict()['workers_info']
                for i in range(workers_count):
                    workers[i]['cpu'].append(workers_r[i]['cpu'])
                    workers[i]['rss'].append(workers_r[i]['rss'])
            
            for w in workers:
                w['cpu'] = np.array(w['cpu']).flatten()
                w['rss'] = np.array(w['rss']).flatten()

            mem_unit_scale = 1/(1024**2)
            mem_unit = 'MiB'

            workers_summary = []
            for worker in workers:
                w_data = {}

                w_data['cpu_max'] = worker["cpu"].max()
                w_data['cpu_mean'] = worker["cpu"].mean()
                w_data['cpu_min'] = worker["cpu"].min()
                w_data['cpu_last'] = worker["cpu"][0]
                w_data['mem_rss_max'] = f'{np.round(worker["rss"].max()*mem_unit_scale)} {mem_unit}'
                w_data['mem_rss_mean'] = f'{np.round(worker["rss"].mean()*mem_unit_scale)} {mem_unit}'
                w_data['mem_rss_min'] = f'{np.round(worker["rss"].min()*mem_unit_scale)} {mem_unit}'
                w_data['mem_rss_min'] = f'{np.round(worker["rss"][0]*mem_unit_scale)} {mem_unit}'
                
                workers_summary.append(w_data)

            data = dict({})
            data['from_date'] = from_date.isoformat() if from_date < to_date else to_date.isoformat()
            data['to_date'] = from_date.isoformat() if from_date > to_date else to_date.isoformat()
            data['data_points'] = len(rows)
            data['main_cpu_max'] = main_cpu.max()
            data['main_cpu_mean'] = main_cpu.mean()
            data['main_cpu_min'] = main_cpu.min()
            data['main_cpu_last'] = main_cpu[0]
            data['main_mem_rss_max'] = f'{np.round(main_mem_rss.max()*mem_unit_scale)} {mem_unit}'
            data['main_mem_rss_mean'] = f'{np.round(main_mem_rss.mean()*mem_unit_scale)} {mem_unit}'
            data['main_mem_rss_min'] = f'{np.round(main_mem_rss.min()*mem_unit_scale)} {mem_unit}'
            data['main_mem_rss_last'] = f'{np.round(main_mem_rss[0]*mem_unit_scale)} {mem_unit}'
            data['workers_cpu_max'] = workers_cpu.max()
            data['workers_cpu_mean'] = workers_cpu.mean()
            data['workers_cpu_min'] = workers_cpu.min()
            data['workers_cpu_last'] = workers_cpu[0]
            data['workers_mem_rss_max'] = f'{np.round(workers_mem_rss.max()*mem_unit_scale)} {mem_unit}'
            data['workers_mem_rss_mean'] = f'{np.round(workers_mem_rss.mean()*mem_unit_scale)} {mem_unit}'
            data['workers_mem_rss_min'] = f'{np.round(workers_mem_rss.min()*mem_unit_scale)} {mem_unit}'
            data['workers_mem_rss_last'] = f'{np.round(workers_mem_rss[0]*mem_unit_scale)} {mem_unit}'
            data['workers_summary'] = workers_summary

            return { 'data': data };
        except Exception as e:
            print(e)
            raise e         
        finally:
            session.close()

    def last(self):
        session = self.__db.getSession()
        try:
            minimal = request.args.get('minimal') == 'true'

            query = session.query(AppInfo).filter_by().order_by(AppInfo.created_at.desc())
            
            if query.count() == 0:
                return {'error':f"Register {id} not found"}, 404

            return {'data':query.first().getDict(minimal)};            
        finally:
            session.close()
    
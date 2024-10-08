from flask import make_response, request, send_file
from flask_classful import FlaskView
import io

from src.db import Database
from src.manager import JobManager

from src.models.Job import Job

class JobView(FlaskView):

    def __init__(self, args):
        self.__db:Database = args[0]
        self.__job_m:JobManager = args[1]
    
    def post(self):
        session = self.__db.getSession()
        job = None
        try:
            job = Job.FromJson(request.json)

            session.add(job)
            session.commit()

            return {'data':{'job_id':job.job_id}}, 201;     
        except Exception as e:
            print(e)
            session.flush() 
            return {'error': f'Unexpected error {e}'},500      
        finally:
            session.close()
            if job is not None:
                self.__job_m.addJob(job.getQueueDict())

    def index(self):
        session = self.__db.getSession()
        try:
            limit = int(request.args.get('limit')) if request.args.get('limit') is not None else 100
            
            query = session.query(Job).order_by(Job.created_at.desc()).limit(limit)

            if query.count() == 0:
                return {'error':f"No jobs not found"}, 404

            jobs = query.all()

            return {'data':[job.getDict() for job in jobs]};            
        finally:
            session.close()

    def get(self, job_id):
        session = self.__db.getSession()
        try:
            minimal = request.args.get('minimal') == 'true'
            
            query = session.query(Job).filter_by(job_id=job_id)

            if minimal:
                query.with_entities(Job.status)
            
            if query.count() == 0:
                return {'error':f"Job {job_id} not found"}, 404

            job = query.first()

            return {'data':job.getDict(minimal)};            
        finally:
            session.close()
    
    def image(self, job_id):
        session = self.__db.getSession()
        try:
            query = session.query(Job).filter_by(job_id=job_id)

            if query.count() == 0:
                return {'error':f"Job {job_id} not found"}, 404
            
            job = query.first()

            if job.image == None:
                return {'error':f"Job {job_id} image not ready"}, 400

            bytes = io.BytesIO()
            bytes.write(job.image)
            bytes.seek(0)
            
            res = make_response(send_file(bytes,mimetype='image/png'))         
            return res
        finally:
            session.close()
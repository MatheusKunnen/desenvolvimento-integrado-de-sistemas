from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, LargeBinary

import json

from src.utils.uuidv7 import uuid7

from datetime import datetime

JobBase = declarative_base()

class Job(JobBase):
    __tablename__ = 'job'

    job_id = Column(String, nullable=False, primary_key=True)
    status = Column(String, nullable=False)
    user = Column(String, nullable=False)
    use_gain = Column(Boolean, nullable=False)
    model = Column(Integer, nullable=False)
    signal = Column(LargeBinary, nullable=False)
    algorithm = Column(String, nullable=False)
    image_size = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    image = Column(LargeBinary, nullable=True)
    iterations_at = Column(Integer, nullable=True)

    def __repr__(self):
        if str(self.status).lower() == 'pending':
            return f"Job: {self.job_id} [{self.status}]"
        else:
            return f"Job: {self.job_id} [{self.status}] at: {self.finished_at}"
        
    def getDict(self, minimal=False):
        if minimal:
            return dict({'status':self.status})
        return dict({
            'job_id':self.job_id,
            'status':self.status,
            'user':self.user,
            'use_gain':self.use_gain,
            'model':self.model,
            'algorithm':self.algorithm,
            'image_size':self.image_size,
            'created_at':self.created_at.isoformat(),
            'started_at':self.started_at.isoformat() if self.started_at is not None else None,
            'finished_at':self.finished_at.isoformat() if self.finished_at is not None else None,
            'iterations_at':self.iterations_at,
        })
    
    def getQueueDict(self):
        return dict({
            'job_id':self.job_id,
            'status':self.status,
            'user':self.user,
            'use_gain':self.use_gain,
            'model':self.model,
            'algorithm':self.algorithm,
            'image_size':self.image_size,
            'signal':self.signal
        })
    
    @staticmethod
    def FromJson(data:dict):
        return Job(
            job_id=data['job_id'] if data.get('job_id') is not None else uuid7(as_type='str'),
            status=data['status'] if data.get('state') is not None else 'pending',
            user=data['user'],
            use_gain=data['use_gain'],
            model=data['model'],
            signal=json.dumps(data['signal']).encode('utf-8'),
            algorithm=data['algorithm'] if data.get('state') is not None else 'cgnr',
            image_size='30x30' if data['model'] == 1 else '60x60',
            created_at=datetime.now()
        )
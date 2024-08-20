import json

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime

from src.utils.uuidv7 import uuid7

AnalyticsBase = declarative_base()

class AppInfo(AnalyticsBase):
    __tablename__ = 'app_info'

    id = Column(String, nullable=False, primary_key=True)
    main_cpu_pct = Column(Float, nullable=False)
    main_mem_rss = Column(Integer, nullable=False)
    workers_cpu_pct = Column(Float, nullable=False)
    workers_mem_rss = Column(Integer, nullable=False)
    jobs_queue = Column(Integer, nullable=False)
    results_queue = Column(Integer, nullable=False)
    workers = Column(Integer, nullable=False)
    workers_info = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
        
    def getDict(self, minimal=False):
        return dict({
                    'id': self.id,
                    'main_cpu_pct': self.main_cpu_pct,
                    'main_mem_rss': self.main_mem_rss,
                    'workers_cpu_pct': self.workers_cpu_pct,
                    'workers_mem_rss': self.workers_mem_rss,
                    'jobs_queue': self.jobs_queue,
                    'results_queue': self.results_queue,
                    'workers': self.workers,
                    'workers_info': AppInfo.__GetJSON(self.workers_info) if not minimal else None,
                    'created_at': self.created_at.isoformat()
                })
    
    @staticmethod
    def FromDict(data:dict):
        return AppInfo(
            id = data['id'] if data.get('id') is not None else uuid7(as_type='str'),
            main_cpu_pct = data['main_cpu_pct'],
            main_mem_rss = data['main_mem_rss'],
            workers_cpu_pct = data['workers_cpu_pct'],
            workers_mem_rss = data['workers_mem_rss'],
            jobs_queue = data['jobs_queue'],
            results_queue = data['results_queue'],
            workers = data['workers'],
            workers_info = data['workers_info'],
            created_at = data['created_at']
        )
    
    @staticmethod
    def __GetJSON(data:str):
        try:
            return json.loads(data)
        except:
            return {}
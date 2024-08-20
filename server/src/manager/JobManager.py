import psutil
import json
from typing import List
from time import sleep
from datetime import datetime

from multiprocessing import Process, Queue
from threading import Thread
from sqlalchemy import update

from .Worker import Worker

from src.db import Database
from src.config import LocalConfig

from src.models.Job import Job
from src.models.AppInfo import AppInfo

def worker_entry(id, input_q, output_q, timeout, max_error):
    try:
        w = Worker(id, input_q, output_q, timeout, max_error)
        w.run()
    except Exception as e:
        print(e)


def r_thread_entry(job_m):
    job_m.resultThreadEntry()

def m_thread_entry(job_m):
    job_m.monitorThreadEntry()

class JobManager:
    
    def __init__(self, jobs_db: Database, analytics_db: Database):
        self.__jobs_db = jobs_db
        self.__analytics_db = analytics_db

        self.__n_workers = LocalConfig.GetDefault().getMaxModelWorkers()
        self.__processes: List[Process] = []
        self.__r_thread = None
        self.__m_thread = None

        self.__jobs_queue = Queue()
        self.__results_queue = Queue()
        
        self.__initResultThread()
        self.__initWorkers()
        self.__initMonitorThread()

    def addJob(self, job):
        self.__jobs_queue.put(job)

    def __initResultThread(self):
        self.__r_thread = Thread(target=r_thread_entry, args=(self, ), daemon=True)
        self.__r_thread.start()

    def __initMonitorThread(self):
        self.__m_thread = Thread(target=m_thread_entry, args=(self, ), daemon=True)
        self.__m_thread.start()

    def __initWorkers(self):
        timeout = LocalConfig.GetDefault().getModelClearTimeout()
        max_error = LocalConfig.GetDefault().getModelMaxError()
        for i in range(self.__n_workers):            
            p = Process(target=worker_entry, args=(i, self.__jobs_queue, self.__results_queue, timeout, max_error), daemon=True)
            self.__processes.append(p)
        
        for p in self.__processes:
            p.start()

    def handleJobResult(self, result):
        session = self.__jobs_db.getSession()
        try:
            # print('RT',f'Saving result of job {result["job_id"]}')
            stmt = update(Job).where(Job.job_id == result["job_id"]).values(
                status="done",
                iterations_at= result["iterations_at"],
                started_at= result["started_at"],
                finished_at= result["finished_at"],
                image= result["image"]
            )
            session.execute(stmt)
            session.commit()
        finally:
            session.close()

    def resultThreadEntry(self):
        while True:
            try:
                result = self.__results_queue.get()
                self.handleJobResult(result)
            except Exception as e:
                print(e)

    def monitorThreadEntry(self):
        print('Monitor Thread started.')
        while True:
            try:
                info = self.getAnalyticsInfo()
                
                self.saveAnalyticsInfo(info)

                # print('[MT]', 'MAIN=','CPU:', info['main_cpu_pct'],'RAM:', round(info['main_mem_rss']/1024), 'KiB', 'WORKERS=','CPU:', info['workers_cpu_pct'],'RAM:', round(info['workers_mem_rss']/1024), 'KiB', 'Jobs:', info['jobs_queue'])

                sleep(1)
            except Exception as e:
                print(e)

    def saveAnalyticsInfo(self, info: dict):
        session = self.__analytics_db.getSession()
        try:
            app_info = AppInfo.FromDict(info)
            session.add(app_info)
            session.commit()
        except Exception as e:
            print(e)
        finally:
            session.close()

    def getAnalyticsInfo(self):
        main_p = psutil.Process()
        main_cpu_pct = main_p.cpu_percent(interval=0.0001)
        main_mem_rss = main_p.memory_info().rss

        workers_cpu_pct = 0
        workers_mem_rss = 0
        workers_info = []
        for i, p in enumerate(self.__processes):
            proc = psutil.Process(p.pid)
            if not proc.is_running:
                return
            
            info = dict({'id': i, 'cpu':proc.cpu_percent(interval=0.001), 'rss': proc.memory_info().rss})
            
            workers_cpu_pct += info['cpu']
            workers_mem_rss += info['rss']
            
            workers_info.append(info)

        return dict({
            'main_cpu_pct': main_cpu_pct,
            'main_mem_rss': main_mem_rss,
            'workers_cpu_pct': workers_cpu_pct,
            'workers_mem_rss': workers_mem_rss,
            'jobs_queue': self.getJobsCount(),
            'results_queue': self.getResultsCount(),
            'workers': len(workers_info),
            'workers_info': json.dumps(workers_info),
            'created_at': datetime.now()
        })

    def getJobsCount(self):
        try:
            return self.__jobs_queue.qsize()
        except:
            return -1
        
    def getResultsCount(self):
        try:
            return self.__results_queue.qsize()
        except:
            return -1
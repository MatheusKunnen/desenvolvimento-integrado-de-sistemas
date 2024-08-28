import traceback
import psutil
import json
import os 

from math import ceil
import numpy as np

from typing import List
from time import sleep
from datetime import datetime

from multiprocessing import Process, Queue, Event, synchronize
from threading import Thread
from sqlalchemy import update

from .Worker import Worker

from src.db import Database
from src.config import LocalConfig

from src.models.Job import Job
from src.models.AppInfo import AppInfo

def worker_entry(id, input_q, output_q, timeout, max_error, event):
    try:
        w = Worker(id, input_q, output_q, event, timeout, max_error)
        w.run()
    except Exception as e:
        print(e)

class WorkerDescriptor:
    def __init__(self, id:int, process:Process, event: synchronize.Event):
        self.id = id
        self.process = process
        self.event = event

def r_thread_entry(job_m):
    job_m.resultThreadEntry()

def m_thread_entry(job_m):
    job_m.monitorThreadEntry()

def a_thread_entry(job_m):
    job_m.analyticsThreadEntry()

class JobManager:
    __W_ID = 0
    MODEL_COUNT = 2
    MODEL_COSTS = [6, 1]
    MODEL_MEM_COST_MB = [1500, 250]
    
    def __init__(self, jobs_db: Database, analytics_db: Database):
        self.__pid = os.getpid()
        self.__verbose = False

        self.__jobs_db = jobs_db
        self.__analytics_db = analytics_db

        self.__max_workers = LocalConfig.GetDefault().getMaxModelWorkers()
        self.__processes: List[Process] = []
        self.__workers: List[List[WorkerDescriptor]] = [[],[]]

        self.__r_thread = None
        self.__m_thread = None

        self.__jobs_queues = [Queue(), Queue()]
        self.__results_queue = Queue()
        
        self.__initResultThread()
        self.__initWorkers()
        self.__initMonitorThread()
        self.__initAnalyticsThread()

    def addJob(self, job):
        model = job["model"] -1
        self.__jobs_queues[model].put(job)

    def __initResultThread(self):
        self.__r_thread = Thread(target=r_thread_entry, args=(self, ), daemon=True)
        self.__r_thread.start()

    def __initAnalyticsThread(self):
        self.__a_thread = Thread(target=a_thread_entry, args=(self, ), daemon=True)
        self.__a_thread.start()

    def __initMonitorThread(self):
        self.__m_thread = Thread(target=m_thread_entry, args=(self, ), daemon=True)
        self.__m_thread.start()

    def __initWorkers(self):
        worker_t = self.getWorkersTarget()
        self.print(f"Workers target {worker_t}")
        for model in range(2):
            for i in range(int(worker_t[model])):
                worker = self.genWorker(self.__jobs_queues[model])
                self.__workers[model].append(worker)
                worker.process.start()

    def genWorker(self, job_queue: Queue, id:int = None):
        timeout = LocalConfig.GetDefault().getModelClearTimeout()
        max_error = LocalConfig.GetDefault().getModelMaxError()
        id = id if id is not None else self.__getWorkerId()

        event = Event()
        event.set()
        p = Process(target=worker_entry, args=(id, job_queue, self.__results_queue, timeout, max_error, event), daemon=True)

        return WorkerDescriptor(id, p, event)

    def handleJobResult(self, result):
        session = self.__jobs_db.getSession()
        try:
            if self.__verbose:
                print('RT',f'Saving result of job {result["job_id"]}')

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

    def analyticsThreadEntry(self):
        timeout = LocalConfig.GetDefault().getAnalyticsPollingTime()
        verbose = LocalConfig.GetDefault().getAnalyticsVerbose()

        print('Analytics Thread started.')
        while True:
            try:
                info = self.getAnalyticsInfo()
                
                self.saveAnalyticsInfo(info)
                if verbose:
                    print('[AN]', 'MAIN=','CPU:', info['main_cpu_pct'],'RAM:', round(info['main_mem_rss']/1024), 'KiB', 'WORKERS=','CPU:', info['workers_cpu_pct'],'RAM:', round(info['workers_mem_rss']/1024), 'KiB', 'Jobs:', info['jobs_queue'])

                sleep(timeout)
            except Exception as e:
                # print(e)
                print(traceback.format_exc())

    def monitorThreadEntry(self):
        timeout = LocalConfig.GetDefault().getAnalyticsPollingTime()
        verbose = LocalConfig.GetDefault().getAnalyticsVerbose()

        print('Monitor Thread started.')
        while True:
            try:
                self.checkWorkersBalance()
                sleep(timeout)
            except Exception as e:
                print(traceback.format_exc())

    def checkWorkersBalance(self):
        w_target = self.getWorkersTarget()
        w_current = self.getCurrentWorkersTarget()

        if w_current[0] == w_target[0] and w_current[1] == w_target[1]:
            if self.__verbose:
                self.print(f'Same worker target {w_target}')
            return
        
        w_delta = w_target - w_current

        if self.__verbose:
            self.print(f'Target changed {w_current} -> {w_target} ({w_delta})')

        w_2_stop:List[List[WorkerDescriptor]] = [[],[]]
        for model in range(JobManager.MODEL_COUNT):
            if w_delta[model] < 0:
                for i in range(-w_delta[model]):
                    worker = self.__workers[model][i]
                    worker.event.clear() # Flag worker to stop
                    w_2_stop[model].append(worker)

        for model in range(JobManager.MODEL_COUNT):
            for w in w_2_stop[model]:
                if w.event.wait(80): # Waits to worker to stop
                    self.__workers[model] = [w2 for w2 in self.__workers[model] if w2.id != w.id]
                else: 
                    self.print(f'ERROR: Timeout waiting for {w.id}')
                    return

        for model in range(JobManager.MODEL_COUNT):
            if w_delta[model] > 0:
                worker = self.genWorker(self.__jobs_queues[model])
                self.__workers[model].append(worker)
                worker.process.start()

        if True or self.__verbose:
            self.print(f'Worker target change completed {w_target} {self.getCurrentWorkersTarget()}')


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
        main_cpu_pct = main_p.cpu_percent(interval=0.005)
        main_mem_rss = main_p.memory_info().rss

        workers_cpu_pct = 0
        workers_mem_rss = 0
        workers_info = []
        for model in range(JobManager.MODEL_COUNT):
            for w in self.__workers[model]:
                pid = w.process.pid

                proc = psutil.Process(pid)
                if not proc.is_running:
                    return
                
                info = dict({'pid':pid, 'id': w.id, 'cpu':proc.cpu_percent(interval=0.005), 'rss': proc.memory_info().rss})
                
                workers_cpu_pct += info['cpu']
                workers_mem_rss += info['rss']
                
                workers_info.append(info)
        
        data = dict({})

        jobs_count = self.getJobsCount()
        w_count = self.getCurrentWorkersTarget()
        for model in range(JobManager.MODEL_COUNT):
            data[f'jobs_queue_{model+1}'] = int(jobs_count[model])
            data[f'workers_model_{model+1}'] = int(w_count[model]) 

        data['main_cpu_pct'] =  main_cpu_pct
        data['main_mem_rss'] =  main_mem_rss
        data['workers_cpu_pct'] =  workers_cpu_pct
        data['workers_mem_rss'] =  workers_mem_rss
        data['jobs_queue'] =  data[f'jobs_queue_1'] + data[f'jobs_queue_2']
        data['results_queue'] =  self.getResultsCount()
        data['workers'] =  len(workers_info)
        data['workers_info'] =  json.dumps(workers_info)
        data['created_at'] =  datetime.now()

        return data

    def getJobsCount(self):
        try:
            return [queue.qsize() for queue in self.__jobs_queues]
        except Exception as e:
            print(e)
            return [1 for _ in self.__jobs_queues]
        
    def getResultsCount(self):
        try:
            return self.__results_queue.qsize()
        except:
            return 1
        
    def getCurrentWorkersTarget(self):
        return np.array([len(self.__workers[0]), len(self.__workers[1])]).astype(np.int32)
        
    def getMemoryBudget(self):
        allowed = round(psutil.virtual_memory().total*0.6)
        return round(allowed/(1024**2))
    
    def getQueuesCosts(self):
        jobs = np.array(self.getJobsCount())
        
        jobs[0] *= JobManager.MODEL_COSTS[0]
        jobs[1] *= JobManager.MODEL_COSTS[1]

        if jobs.sum() == 0:
            jobs += 1

        return jobs/jobs.sum()
    
    def getWorkersTarget(self):
        models_count = 2
        mem_budget = self.getMemoryBudget()

        q_costs = self.getQueuesCosts()
        
        w_count = np.round(q_costs*self.__max_workers).astype(np.int32)

        # At least 1 workers per model
        for i in range(models_count):
            if w_count[i] == 0:
                w_count[i] += 1

        # Check max workers
        if w_count.sum() > self.__max_workers:
            delta = w_count.sum() - self.__max_workers
            if w_count[0] > w_count[1]:
                w_count[0] -= delta
                w_count[1] += delta
            else:
                w_count[0] += delta
                w_count[1] -= delta

        mem_cost = self.getWorkerPlanMemUsage(w_count)
        if mem_cost.sum() > mem_budget:
            mem_delta = mem_cost.sum() - mem_budget
            
            if mem_delta < JobManager.MODEL_MEM_COST_MB[1] and w_count[1] > 1:
                w_count[1] -= 1
            elif mem_delta < JobManager.MODEL_MEM_COST_MB[0] and w_count[0] > 1:
                w_count[0] -= 1

            mem_cost = self.getWorkerPlanMemUsage(w_count)
            if mem_cost.sum() > mem_budget:

                w_delta = np.array([ceil(mem_delta/JobManager.MODEL_MEM_COST_MB[0]), ceil(mem_delta/JobManager.MODEL_MEM_COST_MB[1])])
                if w_count[0] - w_delta[0] > 0:
                    w_count[0] -= w_delta[0]
                else:
                    w_count[1] -= w_delta[1]
            
        mem_cost = self.getWorkerPlanMemUsage(w_count)
        total_mem = mem_cost.sum()
        if w_count.sum() < self.__max_workers and total_mem + JobManager.MODEL_MEM_COST_MB[1] < mem_budget:
            delta_workers = self.__max_workers - w_count.sum()

            while delta_workers > 0 and total_mem + JobManager.MODEL_MEM_COST_MB[0] < mem_budget:
                w_count[0] += 1
                delta_workers -= 1
                total_mem += JobManager.MODEL_MEM_COST_MB[0]

            while delta_workers > 0 and total_mem + JobManager.MODEL_MEM_COST_MB[1] < mem_budget:
                w_count[1] += 1
                delta_workers -= 1
                total_mem += JobManager.MODEL_MEM_COST_MB[1]
        
        if self.__verbose:
            self.print(f"Worker plan {self.__max_workers}->{w_count} with cost of {mem_cost.sum()}/{mem_budget} MiB")
        
        return w_count
        
    def getWorkerPlanMemUsage(self, w_count):
        return np.array([w_count[i]*JobManager.MODEL_MEM_COST_MB[i] for i in range(2)])
    
    def __getWorkerId(self):
        JobManager.__W_ID += 1
        return JobManager.__W_ID -1
        
    def print(self, msg:str):
        print(f'[{self.__pid}] MA:', msg) 
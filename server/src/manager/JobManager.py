from multiprocessing import Process, Queue
from threading import Thread
from sqlalchemy import update

from .Worker import Worker
from src.models.Job import Job

def worker_entry(id, input_q, output_q):
    w = Worker(id, input_q, output_q)
    w.run()

def thread_entry(job_m):
    job_m.thread_entry()

class JobManager:
    
    def __init__(self, jobs_db):
        self.__jobs_db = jobs_db

        self.__n_workers = 4
        self.__processes = []
        self.__thread = None

        self.__jobs_queue = Queue()
        self.__results_queue = Queue()
        
        self.__initThread()
        self.__initWorkers()

    def addJob(self, job):
        self.__jobs_queue.put(job)

    def __initThread(self):
        self.__thread = Thread(target=thread_entry, args=(self, ), daemon=True)
        self.__thread.start()

    def __initWorkers(self):
        for i in range(self.__n_workers):
            p = Process(target=worker_entry, args=(i, self.__jobs_queue, self.__results_queue), daemon=True)
            self.__processes.append(p)
        
        for p in self.__processes:
            p.start()

    def handleJobResult(self, result):
        session = self.__jobs_db.getSession()
        try:
            print(f'Saving result of job {result["job_id"]}')
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

    def thread_entry(self):
        while True:
            try:
                result = self.__results_queue.get()
                self.handleJobResult(result)
            except Exception as e:
                print(e)
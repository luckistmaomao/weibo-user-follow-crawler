"""
@author yuzt
created on 2014.8.10
"""

import time
from Queue import Queue
from time import ctime,sleep
import threading
import os
import traceback
import random
import socket
try:
    from task import crawl_one
    from logger import Logger
    from requests.exceptions import ConnectionError,ProxyError,Timeout
    from my_exceptions import CountException
except ImportError:
    s = traceback.format_exc()
    print s


if not os.path.exists('logs'):
    os.mkdir('logs')
error_logger = Logger("logs/errors.log","ErrorLogger").getlog()

class Threadpool(object):
    def __init__(self,max_workers,func,user_list = []):
        self.max_workers = max_workers
        self.user_queue = Queue()
        for user in user_list:
            self.user_queue.put(user)
        self.workers = []
        self.func = func
        self.createWorkers(max_workers)

    def createWorkers(self,num_workers):
        for i in range(num_workers):
            self.workers.append(WorkerThread(self.func,self.user_queue))
        for thread in self.workers:
            thread.start()
            

class WorkerThread(threading.Thread):
    '''
    A sub class of Thread
    '''
    def __init__(self, func,user_queue, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self._user_queue = user_queue

    def run(self):
        while True:
            try:
                uid = self._user_queue.get()
            except:
                pass
                continue

            args = []
            args.append(uid)
            print '-starting at:', ctime()
            try:
                apply(self.func,args )
            except:
                s = traceback.format_exc()
                error_logger.error("error uid %s" % (uid,))
                error_logger.error(s)
                print s
            print '-finished at:', ctime()

class ProxyThreadpool(object):
    def __init__(self,max_workers,func,proxy_ip_manager,user_list = []):
        self.max_workers = max_workers
        self.user_queue = Queue()
        for user in user_list:
            self.user_queue.put(user)
        self.workers = []
        self.func = func
        self.proxy_ip_manager = proxy_ip_manager
        self.createWorkers(max_workers)

    def createWorkers(self,num_workers):
        for i in range(num_workers):
            self.workers.append(ProxyWorkerThread(self.func,self.user_queue,self.proxy_ip_manager,'thread'+str(i+1)))
        for thread in self.workers:
            thread.start()
            

class ProxyWorkerThread(threading.Thread):
    '''
    A sub class of Thread
    '''
    def __init__(self, func,user_queue, proxy_ip_manager,name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self._user_queue = user_queue
        self._proxy_ip_manager = proxy_ip_manager

    def run(self):
        while True:
            if self._user_queue.empty() is False:
                uid = self._user_queue.get()
            else:
                continue
            
            try:
                proxy_ip = self._proxy_ip_manager.get_ip()
                while proxy_ip in self._proxy_ip_manager.bad_ip_set:
                    proxy_ip = self._proxy_ip_manager.get_ip()
                if proxy_ip != '':
                    print 'get proxy_ip',proxy_ip
            except:
                self._user_queue.put(uid)
                continue

            if proxy_ip == '':
                self._user_queue.put(uid)
                time.sleep(5)
                continue

            args = []
            args.append(uid)
            args.append(proxy_ip)
            try:
                print self.name,'-starting at:', ctime()
                apply(self.func, args)
                print self.name,'-finished at:', ctime()
            except ConnectionError:
                print self.name,'connection error'
                self._user_queue.put(uid)
            except ProxyError:
                print self.name,'proxy_ip',proxy_ip,'  proxy error'
                self._user_queue.put(uid)
                self._proxy_ip_manager.bad_ip_set.add(proxy_ip)
            except Timeout:
                print self.name,'timeout'
                self._user_queue.put(uid)
            except socket.timeout:
                print self.name,'socket timeout'
                self._user_queue.put(uid)
            except CountException:
                print self.name,'count exception'
                error_logger.error('%s:count exception' % (self.name,))
                self._user_queue.put(uid)
                self._proxy_ip_manager.bad_ip_set.add(proxy_ip)
            except:
                s = traceback.format_exc()
                error_logger.error("error uid %s" % (uid,))
                error_logger.error(s)
                self._user_queue.put(uid)


def do_something(num):
    sleep(1)
    print num

def test():
    pool = Threadpool(5,do_something,range(10))

if __name__ == "__main__":
    error_logger.error("eb")

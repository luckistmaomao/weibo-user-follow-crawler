#coding:utf-8
"""
@author yuzt
created on 2014.8.8
"""

import Queue
import time
import threading
import random
import traceback
try:
    import storage
    from storage import WeiboUser,WaitCrawlUser,MicroBlog
    from task import crawl_one,add_crawl
    from multithreads import Threadpool,ProxyThreadpool
    from crawl_follows import get_follows
    from get_proxy_ips import ProxyIpManager
except ImportError:
    s = traceback.format_exc()
    print s

class WaitCrawlUserListManager(threading.Thread):
    """
    维护等待完整爬取的用户队列
    """
    def __init__(self,wait_user_queue):
        threading.Thread.__init__(self)
        self.weibo_user_set = self.get_weibo_user_set()
        self.wait_user_queue = wait_user_queue

    def run(self):
        while True:
            for wait_crawl_user in WaitCrawlUser.objects:
                uid = wait_crawl_user.uid
                if uid in self.weibo_user_set:
                    continue
                self.weibo_user_set.add(uid)
                self.wait_user_queue.put(uid)
            time.sleep(60)

    def get_weibo_user_set(self):
        user_set = set()
        for weibo_user in WeiboUser.objects:
            user_set.add(weibo_user.uid)
        return user_set


class WeiboUserListManager(threading.Thread):
    """
    维护增量爬取的用户队列
    """
    def __init__(self,weibo_user_queue):
        threading.Thread.__init__(self)
        self.weibo_user_queue = weibo_user_queue

    def run(self):
        while True:
            for weibo_user in WeiboUser.objects:
                uid = weibo_user.uid
                self.weibo_user_queue.put(uid)
                sleep_time = random.randint(10,20) 
                time.sleep(sleep_time)


def main():
    pool = Threadpool(4,get_follows)
    ori_uid_list = []
    db_uid_list = []
    uid_list = []
    with open('uid.txt') as f:
        for line in f:
            line = line.strip()
            ori_uid_list.append(line)

    for weibo_user in WeiboUser.objects:
        db_uid_list.append(weibo_user.uid)

    uid_list = list(set(ori_uid_list)-set(db_uid_list))

    for uid in uid_list[:900]:
        pool.user_queue.put(uid)

    proxy_ip_manager = ProxyIpManager()
    proxy_ip_manager.start()
    
    proxy_pool = ProxyThreadpool(30,get_follows,proxy_ip_manager)
    for uid in uid_list[900:]:
        proxy_pool.user_queue.put(uid)

if __name__ == "__main__":
    main()

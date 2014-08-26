#coding:utf-8

import traceback
import time
import urllib
import urllib2
import json
import os
from random import randint
import random
import datetime

try:
    from weibo_login import login
    from conf import USERNAME, PASSWORD, COOKIE_FILE
    from page_parser import parse_user_profile, parse_follow, parse_mblog,\
             parse_json
    from opener import urlfetch
    from errors import UnsuspectedPageStructError, JsonDataParsingError
    from logger import Logger
    from errors import UnsuspectedPageStructError, JsonDataParsingError, URLError
    import storage
    from getcookie import get_cookie,get_cookies
    import requests
    from my_exceptions import CountException
except ImportError:
    s = traceback.format_exc()
    print s

MAXTIMES2TRY = 3
MAXSLEEPINGTIME = 15
http_headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}

#log support
if not os.path.exists('logs'):
    os.mkdir('logs')
log = Logger("logs/routine.log", "RoutineLogger").getlog()
event_logger = Logger("logs/events.log", "EventLogger").getlog()
error_logger = Logger("logs/errors.log","ErrorLogger").getlog()

    
def get_info(uid,proxy_ip=''):
    '''
    get a weibo-user's information
    `uid`: uid of this user
    `weibo_user_type`: 1001 stands for normal users while 1002 stands for media users
    return: UserInfo
    '''
    if login(USERNAME, PASSWORD, COOKIE_FILE):
        for o_o in range(MAXTIMES2TRY):
            try:
                url = 'http://weibo.com/' + uid + '/info'
                if proxy_ip =='':
                    html = urlfetch(url)
                else:
                    proxies = {"http":"http://" + proxy_ip}
                    cookies = get_cookie(COOKIE_FILE)
                    r = requests.get(url, cookies=cookies, headers=http_headers, proxies=proxies,timeout=7)
                    html = r.content
                    with open('data/'+str(random.randint(1,100))+'.html','a') as f:
                        f.write(html)
            except URLError:
                log.error("URLError! - url: %s" % url)
                time.sleep(randint(1, MAXSLEEPINGTIME))
                continue
            else:
                try:
                    info,user_type = parse_user_profile(html)
                except UnsuspectedPageStructError:
                    error_logger.error("Unsuspected page structure! - url: %s" % url)
                else:
                    return info,user_type
    else:
        log.error("Login fail!")
        try:
            os.remove(COOKIE_FILE)
        except:
            pass

def get_follows(uid,proxy_ip=''):
    event_logger.info("get follows start uid: %s" % uid)
    info,user_type = get_info(uid,proxy_ip)

    if info:
        event_logger.info("Information fetching succeed - uid: %s" % uid)
    else:
        event_logger.critical("Infromation fetching fail - uid: %s" % uid)

    n_follows = info.n_followees
    if login(USERNAME, PASSWORD, COOKIE_FILE):
        follows = []
        n_follows = 200 if n_follows > 200 or n_follows is None else n_follows #at most 200   
        if n_follows%10 == 0:
            n_pages = n_follows/20
        else:
            n_pages = n_follows/20

        for page in range(n_pages):
            for o_o in range(MAXTIMES2TRY):
                try:
                    url = 'http://weibo.com/' + uid + '/follow?page=' + str(page+1)
                    if proxy_ip =='':
                        html = urlfetch(url)
                    else:
                        proxies = {"http":"http://" + proxy_ip}
                        cookies = get_cookie(COOKIE_FILE)
                        r = requests.get(url, cookies=cookies, headers=http_headers, proxies=proxies,timeout=7)
                        html = r.content
                except URLError:
                    log.error("URLError! - url: %s" % url)
                    time.sleep(randint(1, MAXSLEEPINGTIME))
                    continue
                else:
                    try:
                        follows_on_current_page = parse_follow(html)
                    except UnsuspectedPageStructError:
                        error_logger.error("Unsuspected page structure! - url: %s" % url)
                        try:
                            os.remove(COOKIE_FILE)
                        except:
                            pass
                        if login(USERNAME, PASSWORD, COOKIE_FILE) == 0:
                            log.error("Login fail!")
                    else:
                        follows += follows_on_current_page
                        log.info("Followees fetched. - uid: %s - count: %d - page:%d" % (uid, len(follows_on_current_page), page+1))
                    break
            time.sleep(randint(1, MAXSLEEPINGTIME))
            if page == 2:
                if len(follows) == 0:
                    raise CountException

        if len(follows) == 0:
            return 
        user, create = storage.WeiboUser.objects.get_or_create(uid=uid)
        user.followees = follows

        user.save()
    

    else:
        log.error("Login fail!")
        try:
            os.remove(COOKIE_FILE)
        except:
            pass


def test():
    uid = '1401527553'
    follows = get_follows(uid)
    print len(follows)

if __name__ == "__main__":
    test()

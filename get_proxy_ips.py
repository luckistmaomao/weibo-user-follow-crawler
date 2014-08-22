#coding:utf-8
"""
author @yuzt
created on 2014.8.20
"""
import traceback
import urllib2
from StringIO import StringIO
import gzip
import threading
import re
import datetime
import time
try:
#    import PyV8
    from lxml import etree
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    print "Import Error"

#class v8Doc(PyV8.JSClass):
#    def write(self, s):
#        return s
#
#class Global(PyV8.JSClass):
#    def __init__(self):
#        self.document = v8Doc()

def getIPs_xici_nn():
    IPs = []
    proxy_url = "http://www.xici.net.co/nn"
    r = requests.get(proxy_url)
    soup = BeautifulSoup(r.content)
    table = soup.find('table',attrs={'id':'ip_list'})
    trs = table.findAll('tr')
    for tr in trs[1:50]:
        tds = tr.findAll('td')
        ip = tds[1].text.strip()
        port = tds[2].text.strip()
        IPs.append(ip+':'+port) 
    return IPs

def getIPs_xici_wn():
    IPs = []
    proxy_url = "http://www.xici.net.co/wn"
    r = requests.get(proxy_url)
    soup = BeautifulSoup(r.content)
    table = soup.find('table',attrs={'id':'ip_list'})
    trs = table.findAll('tr')
    for tr in trs[1:50]:
        tds = tr.findAll('td')
        ip = tds[1].text.strip()
        port = tds[2].text.strip()
        IPs.append(ip+':'+port) 
    return IPs

def getIPs_zdaye():
    IPs = []
    proxy_url = "http://ip.zdaye.com/?ip=&port=&dengji=%B8%DF%C4%E4&adr=&checktime=&sleep=&cunhuo=&px="
    r = requests.get(proxy_url)
    soup = BeautifulSoup(r.content)
    html = str(soup)
    pattern = re.compile('共(\d+)个')
    total_proxy_ip_num = int(pattern.findall(html)[0])
    if total_proxy_ip_num % 80 == 0:
        total_page_num = total_proxy_ip_num / 80
    else:
        total_page_num = total_proxy_ip_num / 80 + 1
    for i in range(total_page_num):
        url = "http://ip.zdaye.com/?ip=&port=&dengji=%B8%DF%C4%E4&adr=&checktime=&sleep=&cunhuo=&px=i&pageid=" + str(i+1)
        r = requests.get(url)
        soup = BeautifulSoup(r.content)
        table = soup.find('table')
        trs = table.findAll('tr')
        for tr in trs:
            tds = tr.findAll('td')
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            IPs.append(ip+':'+port) 
    return IPs

def getIPs_proxy_ru():
    IPs = []
    proxy_url = 'http://proxy.com.ru/gaoni'
    r = requests.get(proxy_url)
    soup = BeautifulSoup(r.content)
    html = str(soup)
    pattern = re.compile('共(\d+)页')
    total_page_num = int(pattern.findall(html)[0])
    for i in range(min(8,total_page_num)):
        url = 'http://proxy.com.ru/gaoni/list_%s.html' % (i+1,)
        r = requests.get(url)
        soup = BeautifulSoup(r.content)
        table = soup.findAll('table')[7]
        trs = table.findAll('tr')
        for tr in trs[1:]:
            tds = tr.findAll('td')
            ip = tds[1].text.strip()
            port = tds[2].text.strip()
            IPs.append(ip+':'+port) 
    return IPs

def getIPs_proxy_digger():
    socket_list = []
    url = 'http://www.site-digger.com/html/articles/20110516/proxieslist.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    tbody = soup.find('tbody')
    trs = tbody.findAll('tr')
    for tr in trs:
        tds = tr.findAll('td')
        socket_address = tds[0].text
        proxy_type = tds[1].text
        location = tds[2].text
        if proxy_type == 'Anonymous' :#and location == 'China':
            ip,port = socket_address.split(':')
            socket_list.append(ip+':'+port)
            
    return socket_list

#- -use v8 engine to eval javascript code to get port
#def getIPs_org_pachong():
#    glob = Global()
#    socket_list = []
#    url = 'http://pachong.org/area/short/name/cn/type/high.html'
#    r = requests.get(url)
#    soup = BeautifulSoup(r.content)
#    script = soup.findAll('script',attrs={'type':'text/javascript'})[2] 
#    js_code_part1 = script.text
#    tbody = soup.find('tbody')
#    trs = tbody.findAll('tr')
#    for tr in trs:
#        tds = tr.findAll('td')
#        ip = tds[1].text
#        js_code_part2 = tds[2].text
#        with PyV8.JSIsolate():
#            with PyV8.JSContext() as ctxt:
#                ctxt.eval(js_code_part1)
#                port = ctxt.eval(js_code_part2[15:-2])
#        socket_address = '%s:%s' % (ip,port)
#        proxy_type = tds[4].a.text
#        if proxy_type == 'high':
#            socket_list.append(socket_address)
#    return socket_list

def getIPs():
    IPPool = []
    
    try:
        IPPool.extend(getIPs_proxy_ru())
    except:
        print traceback.format_exc()
        pass
    try:
        IPPool.extend(getIPs_xici_wn())
    except:
        pass
    try:
        IPPool.extend(getIPs_xici_nn())
    except:
        print traceback.format_exc()
        pass
    try:
        IPPool.extend(getIPs_proxy_digger())
    except:
        pass
    try:
        IPPool.extend(getIPs_zdaye())
    except:
        pass
#    try:
#        IPPool.extend(getIPs_org_pachong())
#    except:
#        print traceback.format_exc()
#        pass

    IPPool = list(set(IPPool))
    print "total IPs: " + str(len(IPPool))
    return IPPool


threadLock = threading.Lock()

class ProxyVerifier(threading.Thread):
    def __init__(self,thread_name,ip_list,proxy_manager):
        threading.Thread.__init__(self)
        self.name = thread_name
        self.ip_list = ip_list
        self.proxy_manager = proxy_manager

    def run(self):
        for ip in self.ip_list:
            validity = False
            try:
                validity = self.verify_ip(ip)
            except:
                pass

            if validity is True:
                self.proxy_manager.add_ip(ip)

    def verify_ip(self, socket_address):
        proxies = {"http":"http://" + socket_address}
        try:
            ip = socket_address.split(':')[0] 
            verify_url1 = 'http://luckist.sinaapp.com/test_ip'
            verify_url2 = 'http://members.3322.org/dyndns/getip'

            r1 = requests.get(verify_url1,proxies=proxies,timeout=3)
            r2 = requests.get(verify_url2,proxies=proxies,timeout=3)
            return_ip1 = r1.content.strip() 
            return_ip2 = r2.content.strip()

            if ip == return_ip1 and ip == return_ip2:
    #        if ip == return_ip1:
                return True
            else:
                return False
        except:
            return False

class ProxyIpManager(threading.Thread):
    def __init__(self,thread_name="ProxyIpManager"):
        threading.Thread.__init__(self)
        self.name= thread_name
        self.ip_list = []
        self.tmp_ip_list = []
        self.cur_index = 0
        self.stop_me = False 
        self.bad_ip_set = set()

    def run(self):
        while not self.stop_me:
            verify_threads = []
            try:
                self.bad_ip_set.clear()
                IPPool = getIPs()
                for thread_id in range(60):   #40个线程验证ip有效性
                    ips = []
                    for index in range(thread_id,len(IPPool),60):
                        ips.append(IPPool[index])
                    #print 'ips',ips
                    verify_threads.append(ProxyVerifier("verify " + str(thread_id), ips, self))
                    print "verify thread %d, ip_list'size is %d" % (thread_id, len(ips))

                self.tmp_ip_list = []
               
                for verify_thread in verify_threads:
                    verify_thread.start()
                for verify_thread in verify_threads:
                    verify_thread.join()

                self.ip_list = self.tmp_ip_list
            except:
                traceback.print_exc()
                pass
            time.sleep(1800)

    def get_ip(self):
        if not self.has_enough_ips():
            return ""
        list_size = len(self.ip_list)
        ip = ""
        try:
            global threadLock
            threadLock.acquire()
            ip = self.ip_list[self.cur_index % list_size]
            self.cur_index = (self.cur_index + 1) % list_size
        except:
            self.cur_index = 0
            pass
        finally:
            threadLock.release()
        
        return ip


    def has_enough_ips(self):
        if len(self.ip_list) > 10:
            return True
        else:
            return False
    
    def get_ip_number(self):
        return len(self.ip_list)
    
    def add_ip(self, new_ip):
        global threadLock
        threadLock.acquire()
        try:
            self.tmp_ip_list.append(new_ip)
        except:
            pass
        finally:
            threadLock.release()
    
    def stop_me(self):
        self.stop_me = True


if __name__ == "__main__":
    proxy_ip_manager = ProxyIpManager()
    proxy_ip_manager.start()
    while True:
        print proxy_ip_manager.get_ip_number()
        time.sleep(3)
#    ips = getIPs()
#    print ips
#    print len(ips)

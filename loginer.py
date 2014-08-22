#!/usr/bin/env python
#coding=utf8

'''
Created on 2014��4��3��

@author: cc
'''
import traceback
try:
    import os, errno
    from login import login
    import cookielib
    import urllib2
    
    from login import do_login
except:
    s = traceback.format_exc()
    print s
    
class Loginer:
    
    def __init__(self):
        
        pass
    
    def login(self, username, password, cookie_file):
        
        return bool( login(username, password, cookie_file) )
    
    
    def proxy_login(self, username, pwd, cookie_file):
        """"
            Login with use name, password and cookies.
            (1) If cookie file exists then try to load cookies;
            (2) If no cookies found then do login
        """
        #If cookie file exists then try to load cookies
        if os.path.exists(cookie_file):
            try:
                cookie_jar  = cookielib.LWPCookieJar(cookie_file)
                cookie_jar.load(ignore_discard=True, ignore_expires=True)
                loaded = 1
            except cookielib.LoadError:
                loaded = 0
                print 'Loading cookies failed!'
        
            #install loaded cookies for urllib2
            if loaded:
                #print 'Loading cookies success'
                return 1
            else:
                return do_login(username, pwd, cookie_file)
    
        else:   #If no cookies found
            return do_login(username, pwd, cookie_file)
        
    def relogin(self,username="",password="",cookie_file=""):
        
        self.remove_cookie(cookie_file)
        
        return login(username,password,cookie_file)

    def remove_cookie(self,cookie_file=""):
        
        try:
            os.remove(cookie_file)
        except OSError as e:
            if e.errno != errno.ENOENT:
                pass
            
loginer = Loginer()

def get_loginer():
    return loginer
    
if __name__ == "__main__":
    loginer = Loginer()
    
    print bool( loginer.login('chengchuan90@126.com','900119','./weibo_login_cookies.dat') )
        
#coding:utf-8
import requests
import sqlite3

def get_cookie(cookiefile):
    cookie = {}
    with open(cookiefile) as f:
        lines = f.readlines()
    for line in lines[1:]:
        line = line.strip()
        space_index = line.find(' ')
        pair = line.split(';')[0][space_index:]
        pair = pair.replace('\"','')
        equal_index = pair.find('=')
        key = pair[:equal_index]
        value = pair[equal_index+1:]
        cookie[key] = value
    
    return cookie

def get_cookies():
    cookies = {}
    path = '/home/yu/.mozilla/firefox/zitwijha.default/cookies.sqlite'
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute('select * from moz_cookies')
    rows = cur.fetchall()
    keys = []
    with open('data/info.txt') as f:
        for line in f:
            keys.append(line.strip())
    for row in rows:
        if row[4] in keys:
            print row
    cur.close()
    return cookies
    

def test():
#    cookies = get_cookie('weibo_login_cookies.dat')
    get_cookies()
    url = 'http://weibo.com/1779257210'
    http_headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
#    r = requests.get(url, cookies=cookies, headers=http_headers) 
#    print r.headers
#    content = r.content
#
#    with open('user.html','a') as f:
#        f.write(content)

if __name__ == "__main__":
    test()


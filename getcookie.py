#coding:utf-8
import requests

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

def test():
    cookies = get_cookie()
    url = 'http://weibo.com/u/1779257210'
    http_headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
    r = requests.get(url, cookies=cookies, headers=http_headers) 
    content = r.content

    with open('user.html','a') as f:
        f.write(content)

if __name__ == "__main__":
    test()


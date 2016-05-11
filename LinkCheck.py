# coding=utf-8

import requests
import pyquery
from datetime import datetime
import lxml.etree
import hashlib

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class LinkCheck(object):

    URL = 'http://m.sohu.com'
    Forward_URL = [
        'http://m.sohu.com/f',
        'http://m.sohu.com/towww',
        '/f',
    ]

    q = []
    h = []

    def __init__(self, url=URL):
        self.URL = url

    def fetch_url(self):
        url = self.q.pop(0)
        t = hashlib.md5(url).hexdigest()
        if t in self.h:
            return
        else:
            self.h.append(t)

        f, r = self.check_avaliable(url)
        if f:
            try:
                pq = pyquery.PyQuery(r.content)
                # src_list = pq('[src]')
                href_list = pq('[href]')
                for i in range(len(href_list)):
                    u = href_list.eq(i).attr('href')
                    # print 'item', u
                    self.q.append(u)

            except lxml.etree.ParserError, e:
                print e
                self.log_error(time=str(datetime.now()), url=url, error=str(e))

            except lxml.etree.XMLSyntaxError, e:
                print e
                self.log_error(time=str(datetime.now()), url=url, error=str(e))

    def check_avaliable(self, url):
        print url

        if 'mailto:' == url[:7]:
            return False, None
        if not 'http://' == url[:7] and not 'https://' == url[:8]:
            if url[0] != '/':
                url = '/'+url
            url = self.URL+url
        try:
            r = requests.get(url, timeout=2)
        except requests.exceptions.MissingSchema, e:
            print e
            self.log_error(time=str(datetime.now()), url=url, error=str(e))
            return False, None
        except requests.exceptions.InvalidSchema, e:
            print e
            self.log_error(time=str(datetime.now()), url=url, error=str(e))
            return False, None
        except requests.exceptions.ConnectionError, e:
            print e
            self.log_error(time=str(datetime.now()), url=url, error=str(e))
            return False, None
        except requests.exceptions.ReadTimeout, e:
            print e
            self.log_error(time=str(datetime.now()), url=url, error=str(e))
            return False, None

        if self.URL in url and not self.check_redirect(url):
                if r.status_code == 200:
                    return True, r
                else:
                    self.log_error(time=str(datetime.now()), url=url, error=str(r.status_code))
                    return False, None
        else:
            return False, None

    def check_repetition(self):
        pass

    def check_redirect(self, url):
        if '.css' in url or '.js' in url or '.jpg' in url or '.png' in url or '.gif' in url:
            return True
        for i in self.Forward_URL:
            if i in url:
                return True
        return False

    def log_error(self, time, url, error):
        with open('log.txt', 'a+') as f:
            res = '\t'.join([time, url, error])
            f.write(res)
            f.write('\n')

    def scan(self):
        self.q.append(self.URL)
        while self.q:
            # print self.q[:5]
            # print self.h[-3:]
            self.fetch_url()
        print u'结果信息'
        with open('log.txt', 'r') as f:
            print f.read()
            print '共计', len(self.h)


if __name__ == '__main__':
    website = LinkCheck('http://tech.gladuo.com')
    website.scan()

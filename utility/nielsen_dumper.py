#! /usr/bin/env python
#coding=utf-8

import re, os, urllib2
from HTMLParser import HTMLParser

from BeautifulSoup import BeautifulSoup

ckpr = urllib2.HTTPCookieProcessor()
opnr = urllib2.build_opener(ckpr)
#Install an OpenerDirector instance as the default global opener.
urllib2.install_opener(opnr)

filepath = os.path.abspath(os.path.split(__file__)[0])

Headers = {
        'Host': 'services.cr-nielsen.com', 
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6', 
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
        'Accept-Language': 'zh-cn,zh;q=0.5', 
        'Accept-Encoding': 'gzip,deflate', 
        'Accept-Charset': 'gb2312,utf-8;q=0.7,*;q=0.7', 
        'Keep-Alive': '300', 
        'Connection': 'keep-alive',
        'Referer': 'http://services.cr-nielsen.com/CR-NetRatings/login.jsp',
    }

def _open(URL, POSTDATA=''):
    if POSTDATA:
        req = urllib2.Request(url=URL, headers=Headers, data=POSTDATA)
    else:
        req = urllib2.Request(url=URL, headers=Headers)
    return urllib2.urlopen(req)

def login(user='hudandan', pswd='Bigworld65'):
    URL_login = '''http://services.cr-nielsen.com/CR-NetRatings/login/pub.UserM.do'''
    POSTDATA='''user=%s&pwd=%s&userlang=0&imageField.x=30&imageField.y=15'''%(user, pswd)
    return _open(URL_login, POSTDATA)

def test_login():
    return login().read().decode('utf-8')

def get_download_idx(idx_url='http://services.cr-nielsen.com/CR-NetRatings/lastPubWeek/pub.ExcelIndex.do'):
    class Parser(HTMLParser):
        result = ''
        def handle_data(self, data):
            self.result = re.search('\d{8,}', _open(idx_url).read()).group()
        def close(self):
            return self.result
    psr = Parser()
    psr.feed(_open(idx_url).read())
    return psr.close()

def get_xls_by_idx(idx):
    src_html = _open(
            URL='http://services.cr-nielsen.com/CR-NetRatings/excelList/pub.ExcelIndex.do', 
            POSTDATA='week=%s'%idx
        ).read()
    
    class Parser(HTMLParser):
        xls_urls = []
        titles = []
        host = 'http://services.cr-nielsen.com'
        
        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                for name,value in attrs:
                    if name == 'href':
                        self.xls_urls.append(self.host+value)
                    if name == 'title':
                        self.titles.append(value)
                            
        def close(self):
            return self.xls_urls

        def get_titles(self):
            return self.titles
    
    psr = Parser()
    psr.feed(src_html)
    xlses = psr.close()
    titles = psr.get_titles()
    
    if not os.path.exists(r'xls'):
        os.mkdir(r'xls')
        
    for index, value in enumerate(xlses):
        
        xls_path = os.path.join(filepath,'xls')
        filename = os.path.join(xls_path, '%s.xls' % titles[index])
        #filename = unicode("xls\%s.xls" % titles[index], "utf8")
        try:
            postdata ='''user=hudandan&pwd=Bigworld65&userlang=0&imageField.x=30&imageField.y=15'''
            data = _open(value, postdata).read()
            xls = file(filename, 'wb')
            xls.write(data)
            print "%s dumped" % filename
            xls.close()
        except:
            pass
        

def dump_overlap(xls_idx):
    
    overlap_xls_url = "http://services.cr-nielsen.com/CR-NetRatings/excel/pub.OverLap.do"
    sid, titles = get_overlap_files(xls_idx)
    
    # overlap files end with '_overlap'
    if not os.path.exists(r'xls'):
        os.mkdir(r'xls')
        
    for index, value in enumerate(sid):
        title = titles[index]
        
        #filename = u"xls\%s.xls" % (title+'_overlap')
        xls_path = os.path.join(filepath,'xls')
        filename = os.path.join(xls_path, '%s.xls' % (title+'_overlap'))
        
        post = '''form_in=true&frequency_id=2&imageField10.x=56&imageField10.y=6&seachstr=&start_date=%s&step3=1&step3_selids=%s&step4_selids=''' % (xls_idx, value)
        data = _open(overlap_xls_url, post).read()
        xls = file(filename, 'wb')
        xls.write(data)
        xls.close()
        print "%s dumped" % filename

def get_overlap_files(xls_idx):
    """ overlap analysis
    download overlap xls files , including sites and classfication xls
    """
    get_site_index_url = "http://services.cr-nielsen.com/CR-NetRatings/sfsel/pub.SWOverlap.do?wdate=%s&hn=3&ids=2" % xls_idx
    get_type_index_url = "http://services.cr-nielsen.com/CR-NetRatings/selsinglec/pub.SWOverlap.do?wdate=%s&hn=3&ids=C0" % xls_idx

    sid = []
    titles = []

    site_data = _open(get_site_index_url).read()
    site_soup = BeautifulSoup(site_data)
    site_items = site_soup.findAll('a', id= re.compile('^a1,'))

    for si in site_items:
        sid.append(si['sid'])
        titles.append(si['title'])

    #type_data = _open(get_type_index_url).read()
    #type_soup = BeautifulSoup(type_data)
    #type_items = type_soup.findAll('a', id= re.compile('^a1,'))

    #for ti in type_items:
    #    sid.append(ti['sid'])
    #    titles.append(ti['title'])
        
    return sid, titles

if '__main__' == __name__:
    test_login()
    xls_idx = get_download_idx()
    print 'xls idx:', get_download_idx()
    data = get_xls_by_idx(xls_idx)
    dump_overlap(xls_idx)
    

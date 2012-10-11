#!/usr/bin/env python
# -*- coding: utf8 -*-
import time
import urllib
import urllib2
import re
import cookielib
import cStringIO
import gzip
import sys

class Pinterest(object):

    def __init__(self):
        self.cookieJar           = None
        self.csrfmiddlewaretoken = None
        self._ch                 = None
        self.http_timeout        = 15
        self.boards              = {}
        
    def login(self,login,password):
        url = 'https://pinterest.com/login/'
        try:
            res = self.request(url)
        except Exception as e:
            print e
            return False
        
        csrfmiddlewaretoken = re.findall(r"<input type='hidden' name='csrfmiddlewaretoken' value='([^']+)'",res)[0]
        _ch                 = re.findall(r"<input type='hidden' name='_ch' value='([^']+)'",res)[0]
        self.csrfmiddlewaretoken = csrfmiddlewaretoken
        self._ch                 = _ch
        post_data = urllib.urlencode({
            'email':login,
            'password':password,
            '_ch':_ch,
            'csrfmiddlewaretoken':csrfmiddlewaretoken,
            'next':'/'
        }) 
        res = self.request(url,post_data,referrer='https://pinterest.com/login/')
        if 'window.userIsAuthenticated = true' in res:
            return True
        else:
            return False
        
    
    def getBoards(self):
        url       = 'http://pinterest.com/pin/create/bookmarklet/'
        res       = self.request(url,referrer='https://pinterest.com/')
        
        res = re.findall(r'<li data="([^"]+)">[\s]*<span>([^<]+)</span>',res)
        boards = {}
        for idb,name in res:
            boards[name.lower()] = idb
        self.boards = boards
        return boards
    
    def createPin(self,board='',title='',desc='',media='',posturl='',tags=[]):
        url       = 'http://pinterest.com/pin/create/bookmarklet/'
        post_data = urllib.urlencode({
            'caption': title,
            'desc': title,
            'board': board,
            'media_url': media,
            'url': posturl,
            'buyable':'',
            'tags':'',
            'replies':'',
            'via':'',
            'csrfmiddlewaretoken':self.csrfmiddlewaretoken
        }) 
        try:
            ref = "%s?%s" % (url,post_data)
            post_data = "%s&form_url=/pin/create/bookmarklet/?%s" % (post_data,post_data)
            res = self.request(url, post_data,referrer=ref)
        except:
            return False
        else:
            if 'Your pin was pinned' in res:
                return True
            return False
            
    def request(self,url,post_data=None,referrer='http://google.com/'):
        """Donwload url with urllib2.
        
           Return downloaded data
        """
        handlers = []
        
        urllib2.HTTPRedirectHandler.max_redirections = 10
        
        if not self.cookieJar:
            self.cookieJar = cookielib.CookieJar()
        
        cookie_handler = urllib2.HTTPCookieProcessor(self.cookieJar)
        handlers.append(cookie_handler)
            
        opener = urllib2.build_opener(*handlers)

        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.1 \
                      (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1'),
            ('Accept', 'image/png,image/*;q=0.8,*/*;q=0.5'),
            ('Accept-Language', 'en-us,en;q=0.5'),
            ('Accept-Encoding', 'gzip,deflate'),
            ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
            ('Keep-Alive', '3600'),
            ('Connection', 'keep-alive'),
            ('Referer', referrer)
        ]
        
        error_happen = False
        html = ''
        try:
            req = urllib2.Request(url, post_data)
            r = opener.open(req,timeout=self.http_timeout)
            html = r.read() 
        except DownloadTimeoutException,e:
            sys.exc_clear()
            error_happen = e
        except Exception,e:
            sys.exc_clear()
            error_happen = e
            
        if error_happen:
            return error_happen

        headers = r.info()
        # If we get gzipped data the unzip it
        if ('Content-Encoding' in headers.keys() and headers['Content-Encoding']=='gzip') or \
           ('content-encoding' in headers.keys() and headers['content-encoding']=='gzip'):
            data = cStringIO.StringIO(html)
            gzipper = gzip.GzipFile(fileobj=data)
            # Some servers may return gzip header, but not zip data.
            try:
                html_unzipped = gzipper.read()
            except:
                sys.exc_clear()    
            else:
                html = html_unzipped

        return html
            
class DownloadTimeoutException(Exception):
    pass
    
    
if __name__ == "__main__":
    p = Pinterest()
    logged = p.login('someeamil@gmail.com','password')
    if logged:
        print 'logged in.'
        boards = p.getBoards()
        print boards
        res = p.createPin(board=boards['art'],title='Anton Semenov | 30 Art Works',
            desc='Anton Semenov | 30 Art Works',
            media='http://1.bp.blogspot.com/-SfG0Ad5_UVo/UGxBfrBGugI/AAAAAAAAA54/o-glBuiX_3Q/s640/Black_dream_by_Gloom82.jpg',
            posturl='http://30artworks.blogspot.com/2012/10/anton-semenov.html')
        print 'pin created: %s' % res
    
    
    
    
    
    
    
    
        

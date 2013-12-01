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
import json

class Pinterest(object):

    def __init__(self,cookie=None):
        self.cookieJar           = cookie
        self.csrfmiddlewaretoken = None
        self.http_timeout        = 15
        self.boards              = {}
        
    def getCookies(self):
        return self.cookieJar
        
    def login(self,login,password):
        url = 'https://pinterest.com/login/'
        try:
            res,headers,cookies = self.request(url)
        except Exception as e:
            raise NotLogged(e)
        
        post_data = urllib.urlencode({
            'source_url':'/login/',
            'data':json.dumps({"options":{"username_or_email":login,"password":password},"context":{"app_version":"62fcc23","https_exp":False}}),
            'module_path':'App()>LoginPage()>Login()>Button(class_name=primary, text=Log in, type=submit, size=large)'
        }) 
        res,headers,cookies = self.request('http://www.pinterest.com/resource/UserSessionResource/create/',post_data,referrer='https://pinterest.com/login/',ajax=True)
        if login in res:
            return True
        else:
            raise NotLogged('Not authorized. Cant find "window.userIsAuthenticated = true" in response')
        
    
    def getBoards(self):
        url       = 'http://pinterest.com/pin/create/bookmarklet/'
        res,headers,cookies = self.request(url,referrer='https://pinterest.com/')
        
        res = re.findall(r'<li(?:.*?)data-id="([^"]+)"(?:.*?)</div>([^<]+)</li>',res, re.I | re.M | re.U | re.S)
        boards = {}
        for idb,name in res:
            boards[unicode(name,'utf-8').lower().strip()] = idb
        self.boards = boards
        return boards
    
    def createPin(self,board='',title='',media='',posturl='',tags=[]):
        url       = 'http://pinterest.com/pin/create/bookmarklet/?media=%s&url=%s&description=%s' % (media,posturl,title)
        post_data = urllib.urlencode({
            'source_url':'/pin/create/bookmarklet/?media=%s&url=%s&description=%s' % (media,posturl,title),
            'data':'{"options":{"board_id":"%s","description":"%s","link":"%s","share_facebook":false,"image_url":"%s","method":"bookmarklet","is_video":null},"context":{"app_version":"62fcc23","https_exp":false}}' % (board,title,posturl,media),
            'module_path':'App()>PinBookmarklet()>PinCreate()>PinForm()>Button(class_name=repinSmall pinIt, text=Pin it, disabled=false, has_icon=true, show_text=false, type=submit, color=primary)'
        }) 
        try:
            res,header,query = self.request('http://www.pinterest.com/resource/PinResource/create/', post_data,referrer=url,ajax=True)
        except Exception as e:
            raise CantCreatePin(e)
        else:
            if 'PinResource' in res:
                return True
            raise CantCreatePin('Cant create pin. Cant find PinResource in response')
            
    def request(self,url,post_data=None,referrer='http://google.com/',ajax=False):
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
            ('Host','www.pinterest.com'),
            ('Origin','http://www.pinterest.com'),
            ('Connection', 'keep-alive'),
            ('Referer', referrer),
            ('X-NEW-APP','1')
        ]
        if ajax:
            opener.addheaders.append(('X-Requested-With','XMLHttpRequest'))
        if self.csrfmiddlewaretoken:
            opener.addheaders.append(('X-CSRFToken',self.csrfmiddlewaretoken))
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
            return error_happen,{},{}

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

        cookies = {cookie.name:cookie.value for cookie in self.cookieJar}
        self.csrfmiddlewaretoken = cookies['csrftoken']
           
        return html,headers,cookies
         
            
class DownloadTimeoutException(Exception):
    pass
    
class NotLogged(Exception):
    pass
    
class CantCreatePin(Exception):
    pass
    
    
if __name__ == "__main__":
    p = Pinterest()
    p.login('test@test.com','123456')
    boards = p.getBoards()
    print boards
    bid = boards['test']
    res = p.createPin(board=bid,title='Anton Semenov | 30 Art Works',
        media='http://1.bp.blogspot.com/-SfG0Ad5_UVo/UGxBfrBGugI/AAAAAAAAA54/o-glBuiX_3Q/s640/Black_dream_by_Gloom82.jpg',
        posturl='http://30artworks.blogspot.com/2012/10/anton-semenov.html')

    print 'pin created: %s' % res
    
    
    
    
    
    
    
    
        

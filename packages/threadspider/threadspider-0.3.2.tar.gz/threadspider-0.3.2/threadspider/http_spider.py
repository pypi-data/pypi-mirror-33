# coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/8/25.
# ---------------------------------
from utils.queue import PriorityQueue as Queue
from threading import Thread
import urllib2
import time
import datetime
from utils.encrypt import md5
import  urlparse
from pybloom import  BloomFilter,ScalableBloomFilter
import  traceback


_queue = Queue()
_size = 0
_handle = None


def spider_init(pool_size,handle = lambda url,content:None):
    '''初始化爬虫
    pool_size 线程池的大小
    handle    爬虫结果回调函数, 函数必须包含两个参数, 第一个参数是url,第二个参数是爬取到的结果
    '''
    print datetime.datetime.now(), "[Spider]:init...."
    global _size, _queue, _url_max_num, _proxy_list,_handle
    if _size == 0 and _handle ==None:
        _size = pool_size
        _handle = handle
        def run():
            def work():
                while 1:
                    kwargs = _queue.get().obj
                    if kwargs:
                        Spider(**kwargs).go()
                    _queue.task_done()
            for i in range(0, _size):
                thread = Thread(target=work)
                thread.setDaemon(True)
                thread.start()

        run()


def spider_join():
    '''
    等待爬虫执行完成
    '''
    global _queue
    _queue.join()







class Spider(object):
    _url_buff = None

    def __init__(self, url, charset=None, data=None, headers=None,  timeout=3, retry_times=30,
                 retry_delta=3, http_proxy=None, force=False):
        '''
            url   目标url
            charset   编码
            data   post的数据,字符串
            headers  自定义请求头,dict
            timeout  超时时间,int,  比如:3
            retry_times 重试次数,int,比如3
            retry_delta   重试间隔,int
            http_proxy         代理ip, 192.168.1.1
            force         强制爬取,而不管有没有爬取过.
        '''
        self.url = url
        self.data = data
        self.timeout = timeout
        self.retry_times = retry_times
        self.retry_delta = retry_delta
        self.charset = charset
        self.headers = headers
        self.http_proxy = http_proxy
        if not Spider._url_buff:
            Spider._url_buff = [BloomFilter(1000000)]
        global _queue
        if data:
            _hash = md5(url) + md5(data)
        else:
            _hash = md5(url)
        if not force:
            try:
                for bloomfilter in Spider._url_buff:
                    assert  _hash not in bloomfilter
            except:
                pass
            else:
                try:
                    Spider._url_buff[-1].add(_hash)
                except:
                    Spider._url_buff.append(BloomFilter(Spider._url_buff[-1].capacity+1000000))
                    Spider._url_buff[-1].add(_hash)
                _queue.put_priority(self.__dict__,0)
        else:
            _queue.put_priority(self.__dict__,0)

    def go(self):
        global  _handle
        def urllib2_get_httpproxy(ip, port):
            proxy = urllib2.ProxyHandler({'http': 'http://%s:%s' % (ip, port)})
            opener = urllib2.build_opener(proxy)
            return opener, "http", ip, port
        retry_times = self.retry_times
        url = self.url
        postdata = self.data
        timeout = self.timeout
        retry_delta = self.retry_delta
        for i in range(0, retry_times):
            try:
                if self.http_proxy:
                    proxy = urllib2_get_httpproxy(self.http_proxy,80)
                    urllib2.install_opener(proxy)
                request = urllib2.Request(url)
                if self.headers:
                    pass
                else:
                    self.headers = {"User-Agent": 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36\
                        (KHTML, like Gecko) Chrome/63.0.3239.132 Mobile Safari/537.36'}
                for k,l in self.headers.items():
                    request.add_header(k,l)
                if self.charset:
                    response = urllib2.urlopen(request, data=postdata, timeout=timeout)
                    data = response.read().decode(self.charset, errors="ignore")
                else:
                    response = urllib2.urlopen(request, data=postdata, timeout=timeout)
                    data = response.read()
                _handle(self.url,data)
            except Exception as e:
                traceback.print_exc()
                print datetime.datetime.now(), "[Spider]:%s Exception:%s" % (url, e)
                time.sleep(retry_delta)
            else:
                print datetime.datetime.now(), "[Spider]:%s Success!" % url
                break

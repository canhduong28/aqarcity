# encoding=utf-8
from scrapy import log
import re
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.http import Request
from aqarcity.items import CityPhone

class AqarcitySpider(BaseSpider):
    name = 'aqarcity'
    allowed_domains = ['www.aqarcity.com']
    cities = {}

    def __init__(self):
        f = open('Saudicities.txt', 'r')
        line = f.readline()
        while line:
            city = line.split(',')
            identifier = re.search(r'(\d+)', city[1]).group(1)
            self.cities[identifier] = city[0]
            line = f.readline()
        f.close()

    def start_requests(self):
        f_index = [9, 10, 11, 12, 13, 15, 17, 18, 110, 19, 2, 103, 3, 4, 5, 6, 109, 7, 21, 22, 39, 26, 27, 28, 29]
        for i in f_index:
            url = 'http://www.aqarcity.com/f' + str(i) + '.html'
            yield Request(url, dont_filter=False, callback=self._parser)

    def _parser(self, response):
        log.msg('Extract city from %s' % response.url, level=log.INFO)

        hxs = HtmlXPathSelector(response)

        base_url = re.sub(r'\.html', '', response.url)
        base_url = re.sub(r'-.+', '', base_url).strip()

        subpages_list = set(re.findall(r'(' + base_url + r'-\d+\.html)', response.body))
        for href in subpages_list:
            yield Request(href, dont_filter=False, callback=self._parser)

        identifier = re.search(r'(\d+)', response.url).group(1)
        try:
            city = self.cities[str(identifier)]
        except:
            city = 'UNKNOWN'
        
        threads_list = set(re.findall(r'href="(http://www\.aqarcity\.com/t\d+\.html)"', response.body))
        for href in threads_list:
            req = Request(href, dont_filter=False, callback=self._extracter)
            req.meta['city'] = city
            yield req
        
        base_url = re.sub(r'\.html', '', response.url)
        base_url = re.sub(r'-.+', '', base_url).strip()
        subpages_list = set(re.findall(r'(' + base_url + r'-\d+\.html)', response.body))
        for href in subpages_list:
            yield Request(href, dont_filter=False, callback=self._parser)            
    
    def _extracter(self, response):
        log.msg('Extract phones from %s' % response.url, level=log.INFO)

        base_url = re.sub(r'\.html', '', response.url)
        base_url = re.sub(r'-.+', '', base_url).strip()
        subpages_list = set(re.findall(r'(' + base_url + r'-\d+\.html)', response.body))
        for href in subpages_list:
            req = Request(href, dont_filter=False, callback=self._extracter)
            req.meta['city'] = response.request.meta['city']
            yield req

        phones = set(re.findall(r'05[0-9]{8}', response.body))

        for phone in phones:
            item = CityPhone()
            item['city'] = response.request.meta['city']
            item['phone'] = phone
            yield item




    



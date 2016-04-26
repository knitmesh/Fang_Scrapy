#!/usr/bin/env python
# coding=utf-8

import scrapy
import demjson
from SpiderGanji.items import SpiderganjiItem
from SpiderGanji.spiders.startURL import startURL

class xinfangGanji(scrapy.Spider):
    name = 'xinfangGanji'
    allowed_domains = ['ganji.com']
    start_urls = startURL.xinfangURL

    def parse(self, response):
        house_page_query = '//body/div/div/div/dl/dd/div/a'
        house_page_root = response.request.url.split('/')[2]
        for info in response.xpath(house_page_query):
            house_page_href = info.xpath('attribute::href').extract()[0]
            house_page_url = 'http://'+ house_page_root + house_page_href
            house_page_log = info.xpath('attribute::gjalog_fang').extract()[0]
            temp_time = house_page_log.split('@')[2]
            housePublishedTiem = temp_time.split('=')[1]
            yield scrapy.Request(house_page_url,callback=self.parse_house_page,meta={"time":housePublishedTiem})

    def parse_house_page(self,response):
        item = SpiderganjiItem()
        item['housePublishedTime'] = response.request.meta['time']
        item['houseTitle'] = response.xpath('//html/head/title/text()').extract()[0]
        item['houseCity'] = item['houseCity'] = response.xpath('//head/meta[@name="location"]/attribute::content').extract()[0].split(';')[1].split('=')[1]

        #此XPath节点可以获得房屋的所有基本信息
        house_info_query = '//body/div/div/div/div/div/div/ul[@class="basic-info-ul"]'

        price_query = 'li/b[@class="basic-info-price"]/text()'
        item['housePrice'] = response.xpath(house_info_query).xpath(price_query).extract()[0]

        area_query = 'li[2]/text()'
        temp_area = response.xpath(house_info_query).xpath(area_query).extract()[0]
        item['houseArea'] = temp_area.split('-')[1]

        name_query = 'li[5]/a/text()'
        name_query_2 = 'li[5]/span[2]/text()'
        if response.xpath(house_info_query).xpath(name_query).extract_first() is None:
            item['houseName'] = response.xpath(house_info_query).xpath(name_query_2).extract()[0]
        else:
            item['houseName'] = response.xpath(house_info_query).xpath(name_query).extract()[0]

        district_query = 'li[6]/a/text()'
        temp_district = response.xpath(house_info_query).xpath(district_query).extract()
        houseDistrict = ''
        for dist in temp_district:
            houseDistrict = houseDistrict + '-' + dist
        item['houseDistrict'] = houseDistrict

        address_query = 'li[7]/span[@title]/text()'
        item['houseAddress'] = response.xpath(house_info_query).xpath(address_query).extract()[0]

        #此节点匹配经纬度信息
        data = response.xpath('//body/div/div/div/div/div/div[@class="js-map-tab js-so-map-tab"]/attribute::data-ref').extract()[0]
        data_json = demjson.decode(data)
        lnglat = data_json['lnglat']
        item['houseBaiduLongitude'] = lnglat.split(',')[0][1:]
        item['houseBaiduLatitude'] = lnglat.split(',')[1]

        yield item
        

"""
Usage: scrapy runspider linkhkSpider.py -a target=xxxx -o %'(time)s'_xxxx.csv
xxxx can only be shop or dine
"""

# -*- coding: utf-8 -*-
#encoding=utf-8
import json
import scrapy
from urllib.parse import urljoin


class LinkhkScrollSpider(scrapy.Spider):
	name = "LINKHK"
	Type = {'shop': 1, 'dine': 2}
	api_url = 'http://www.linkhk.com/linkweb/api/shop/?categoryId=&districtId=&shopCentreId=&pageType={}&pageSize=10&pageNo={}'

	def start_requests(self):
		self.api_url = self.api_url.format(self.Type.get(self.target, 1), {})
		start_urls = [self.api_url.format(0)]
		yield scrapy.Request(start_urls[0], self.parse)

	def parse(self, response):
		data = json.loads(response.text)

		for shop in data['data']['shopList']:
			item = {}
			item['shop_name_tc'] = shop['shopNameTc']
			item['shop_name_en'] = shop['shopNameEn']
			item['centre_name_tc'] =  shop['shopCentreNameTc']
			item['centre_name_en'] =  shop['shopCentreNameEn']
			item['shop_number'] = shop['shopNo']
			item['shop_id'] = shop['shopId']
			shop_url = urljoin('http://www.linkhk.com/linkweb/api/shop/', str(shop['shopId']))

			request = scrapy.Request(url=shop_url, callback=self.parse_details, meta={'item': item})
			yield request

		if data['data']['pageInfo']['curPage'] < data['data']['pageInfo']['pageCount']:
			next_page = data['data']['pageInfo']['curPage'] + 1
			yield scrapy.Request(url=self.api_url.format(next_page), callback=self.parse)

	def parse_details(self, response):
		data_details = json.loads(response.text)
		item = response.meta['item']
		item['address_tc'] = data_details['data']['shopInfo']['locationTc']
		item['address_en'] = data_details['data']['shopInfo']['locationEn']
		item['shop_type_tc'] = data_details['data']['shopInfo']['shopTypeTextTc']
		item['opening_hours'] = data_details['data']['shopInfo']['openingHoursEn']
		item['shop_type_en'] = data_details['data']['shopInfo']['shopTypeTextEn']
		item['telephone'] = data_details['data']['shopInfo']['telephone']
		yield item

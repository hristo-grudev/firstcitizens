import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import FirstcitizensItem
from itemloaders.processors import TakeFirst


class FirstcitizensSpider(scrapy.Spider):
	name = 'firstcitizens'
	start_urls = ['https://www.firstcitizens.com/about-us/newsroom/news-releases']

	def parse(self, response):
		next_page = response.xpath('//div[@class="fcb-resources fcb-resources--news"]/@data-component-path').getall()
		yield from response.follow_all(next_page, self.parse_year)

	def parse_year(self, response):
		data = json.loads(response.text)
		for post in data['resourceCards']:
			url = post['link']
			date = post['date']
			title = post['title']
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})


	def parse_post(self, response, title, date):
		description = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "fcb-grid--resources-article", " " ))]//div[@class="fcb-rte"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=FirstcitizensItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()

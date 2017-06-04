# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TuItem(scrapy.Item):
	name = scrapy.Field()
	zone = scrapy.Field()
	star = scrapy.Field()
	rating = scrapy.Field()
	rates = scrapy.Field()
	room = scrapy.Field()
	size = scrapy.Field()
	bed = scrapy.Field()
	guests = scrapy.Field()
	price = scrapy.Field()
	#lowestPrice = scrapy.Field()	
	address = scrapy.Field()	
	link = scrapy.Field()
	checkin = scrapy.Field()
	checkout = scrapy.Field()
	zipcode = scrapy.Field()

    # define the fields for your item here like:
    # name = scrapy.Field()
    #pass
	# name = scrapy.Fild()
 #    price = scrapy.Fild()

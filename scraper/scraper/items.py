# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class BroxbourneItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    appNo=scrapy.Field()
    address=scrapy.Field()
    proposal=scrapy.Field()
    applicant=scrapy.Field()
    agent=scrapy.Field()
    planOff=scrapy.Field()
    ward=scrapy.Field()
    co_ords=scrapy.Field()
    validated=scrapy.Field()
    consultation=scrapy.Field()
    neighNotifd=scrapy.Field()
    consultNotifd=scrapy.Field()
    decided=scrapy.Field()
    appealSub=scrapy.Field()

class SearchDocItem(scrapy.Item):
    appNo=scrapy.Field()
    date=scrapy.Field()
    doclink=scrapy.Field()
    doctype=scrapy.Field()
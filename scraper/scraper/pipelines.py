# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv
from itemadapter import ItemAdapter
from scraper.items import BroxbourneItem
from scraper.items import SearchDocItem

class ScraperPipeline:
    
    def process_item(self, item, spider):
        return item
    

class MainPagePipeline:
    def open_spider(self,spider):
        self.file=open('mainpageitems.csv','w',newline='',encoding='utf-8')
        self.writer=csv.writer(self.file)
        self.writer.writerow(['AppNo','Address','proposal','applicant','agent','planningOfficer','ward','co-ordinate','validated','consultation','neigboursNotifd','consulteesNotifd','decided','appealSub'])

    

    def process_item(self,item,spider):
        if isinstance(item,BroxbourneItem):
            self.writer.writerow([
            item.get('appNo',''),
            item.get('address',''),
            item.get('proposal',''),
            item.get('applicant',''),
            item.get('agent',''),
            item.get('planOff',''),
            item.get('ward',''),
            item.get('co_ords',''),
            item.get('validated',''),
            item.get('consultation',''),
            item.get('neighNotifd',''),
            item.get('consultNotifd',''),
            item.get('decided',''),
            item.get('appealSub','')
            ])

        return item
    
    def close_spider(self,spider):
        self.file.close()


class DocumentPagePipeline:
    def open_spider(self,spider):

        self.file2=open('douments.csv','w',newline='',encoding='utf-8')
        self.writer2=csv.writer(self.file2)
        self.writer2.writerow(['date','doclink','doctype','AppNo'])

    def process_item(self,item,spider):
        if isinstance(item,SearchDocItem):
            self.writer2.writerow([
                item.get('date',''),
                item.get('doclink',''),
                item.get('doctype',''),
                item.get('appNo','')
            ])
        return item
    

    def close_spider(self,spider):
        self.file2.close()

        
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
from scrapy.exceptions import DropItem

class DuplicatePhoneNumbersPipeline(object):
    def __init__(self):
        self.phones_seen = set()

    def process_item(self, item, spider):
        if item['phone'] in self.phones_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.phones_seen.add(item['phone'])
            return item
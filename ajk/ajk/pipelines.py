# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymysql
from itemadapter import ItemAdapter


class AjkPipeline:
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cur  = conn.cursor()

    def process_item(self, item, spider):

        if spider.name  == 'ershoufang':


            try:
                print('pipline', item)

                sql = "insert into house_copy values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                    f'{item["xiaoqu"]} {item["huxing"]}',
                    item["area"],
                    item["size"].replace("㎡", ''),
                    item["chaoxiang"],
                    item["louceng"],
                    item["price"],
                    item["city"],
                    item["image"],
                    item["address1"],
                    item["address2"],
                    item["tags"],
                    item["average_price"],
                    item["house_id"]
                )

                self.cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                print(f"excute error:{e}")

        return item

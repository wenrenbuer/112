import copyheaders
import scrapy


class ErshoufangSpider(scrapy.Spider):
    name = "ershoufang"
    allowed_domains = ["anjuke.com"]
    start_urls = ["http://anjuke.com/"]
    headers = copyheaders.headers_raw_to_dict(b"""
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
    cookie: id58=CrIcnGPsY1Grp4siEAv7Ag==; aQQ_ajkguid=3E3343E0-1A8E-5593-7D38-88FD7E4ACF75; 58tj_uuid=5f072458-2697-4040-bb70-250199c88b7d; ajk-appVersion=; als=0; sessid=AC7CF012-A540-4BE3-846D-A69DD034308C; cmctid=613; fzq_h=37ad05e535ce0ddc0bd9912701aa4001_1678374019566_f0d888d551ac41feb5c161bbaa5d560b_614294783; twe=2; _ga=GA1.2.1676633921.1678380677; _gid=GA1.2.1834426893.1678380677; ctid=13; _gat=1; init_refer=; new_uv=4; new_session=0; xxzl_cid=26e39a7a576d4bcb85342e8e4b102983; xxzl_deviceid=67u7D1O9um1/1zN+6d20XH6qxZlnDhcovOoFKRNc2Q//8HdwKnZl9HXvl6jSF3U6; fzq_js_anjuke_ershoufang_pc=e5d2211d266fec85e862687a74d3b86f_1678382824755_23; obtain_by=1
    user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63
    """)

    def start_requests(self):
        citys0 = ["beijing","shanghai","shenzhen"]
        citys1 = ('hangzhou','nanjing','wuhan','xa','chengdu','chongqing')
        citys2 = ('lanzhou','dalian','gy','sjz','ty','xuzhou')
        for icity in citys0[:]:
            yield  scrapy.Request(
                f'https://{icity}.anjuke.com/sale/v3/',
                headers=self.headers,
                dont_filter=True,
            )


    def parse(self, response):
        allarea = response.xpath(".//ul[@class='region region-line2']/li/a/@href")
        print(f'area_list :{len(allarea)}')
        for iar in allarea[1:]:
            print(iar.extract())

            for page in range(1,5):

                true_url = iar.extract() + f'p{page}/'
                print(f"download_next_url {true_url}")

                yield  scrapy.Request(
                    true_url,
                    headers=self.headers,
                    dont_filter=True,
                    callback=self.parse_list
                )





    def parse_list(self,response):

        houses = response.xpath(".//div[@tongji_tag='fcpc_ersflist_gzcount']")
        print(f'house length:{len(houses)}')
        for ihouse in houses:
            saveinfo = {}
            saveinfo["title"] = ''.join(ihouse.xpath(".//h3[@class='property-content-title-name']/text()").extract()).strip()
            saveinfo["huxing"] = ''.join(ihouse.xpath(".//div[@class='property-content-info']/p[1]//text()").extract()).strip().replace(' ','')
            saveinfo["xiaoqu"] = ''.join(ihouse.xpath(".//p[@class='property-content-info-comm-name']//text()").extract()).strip()
            saveinfo["chaoxiang"] = ''.join(ihouse.xpath(".//div[@class='property-content-info']/p[3]//text()").extract()).strip()
            saveinfo["size"] = ''.join(ihouse.xpath(".//div[@class='property-content-info']/p[2]//text()").extract()).strip()
            saveinfo["city"] = ''.join(response.xpath(".//span[@class='city-name']/text()").extract()).strip()
            saveinfo["area"] = ''.join(response.xpath(".//ul[@class='region region-line2']/li[@class='region-item region-item-area region-item-active']/a/text()").extract()).strip()
            saveinfo["price"] = ''.join(ihouse.xpath(".//span[@class='property-price-total-num']/text()").extract()).strip()
            saveinfo["louceng"] = ''.join(ihouse.xpath(".//div[@class='property-content-info']/p[4]//text()").extract()).strip().split("(")[0]
            if '共' in saveinfo["louceng"]:
                saveinfo["louceng"] = "低层"
            if '室' not in saveinfo["huxing"] and  '厅' not in saveinfo["huxing"] and '卫' not in saveinfo["huxing"]:
                saveinfo["huxing"] = ""

            if '㎡' not in saveinfo["size"]:
                saveinfo["size"] = ""

            saveinfo["image"] = ''.join(ihouse.xpath(".//div[@class='property-image']/img/@src").extract()).strip()
            saveinfo["address1"] = ''.join(ihouse.xpath(".//p[@class='property-content-info-comm-name']//text()").extract()).strip()
            saveinfo["address2"] = ''.join(ihouse.xpath(".//p[@class='property-content-info-comm-address']//text()").extract()).strip()
            saveinfo["tags"] = "|".join(ihouse.xpath(".//span[@class='property-content-info-tag']//text()").extract()).strip()
            saveinfo["average_price"] = ''.join(ihouse.xpath(".//p[@class='property-price-average']/text()").extract()).strip()
            saveinfo["house_id"] = ''.join(ihouse.xpath("./a/@href").extract()).strip().split("?")[0]
            yield  saveinfo

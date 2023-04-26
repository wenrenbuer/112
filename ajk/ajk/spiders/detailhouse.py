import copyheaders
import pymysql
import scrapy


class ErshoufangSpider(scrapy.Spider):
    name = "detail"
    allowed_domains = ["anjuke.com"]
    start_urls = ["http://anjuke.com/"]
    headers = copyheaders.headers_raw_to_dict(b"""
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
    cookie: id58=CrIcnGPsY1Grp4siEAv7Ag==; aQQ_ajkguid=3E3343E0-1A8E-5593-7D38-88FD7E4ACF75; 58tj_uuid=5f072458-2697-4040-bb70-250199c88b7d; ajk-appVersion=; als=0; sessid=AC7CF012-A540-4BE3-846D-A69DD034308C; cmctid=613; fzq_h=37ad05e535ce0ddc0bd9912701aa4001_1678374019566_f0d888d551ac41feb5c161bbaa5d560b_614294783; twe=2; _ga=GA1.2.1676633921.1678380677; _gid=GA1.2.1834426893.1678380677; ctid=13; _gat=1; init_refer=; new_uv=4; new_session=0; xxzl_cid=26e39a7a576d4bcb85342e8e4b102983; xxzl_deviceid=67u7D1O9um1/1zN+6d20XH6qxZlnDhcovOoFKRNc2Q//8HdwKnZl9HXvl6jSF3U6; fzq_js_anjuke_ershoufang_pc=e5d2211d266fec85e862687a74d3b86f_1678382824755_23; obtain_by=1
    user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63
    """)

    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cur = conn.cursor()
#定义了所爬取的url段
    def start_requests(self):
        urlssql = "select house_id from house_copy"
        self.cur.execute(urlssql)
        urls = self.cur.fetchall()
        for iurl in urls:
            yield scrapy.Request(
                iurl[0],
                headers=self.headers,
                dont_filter=True,
                callback=self.parse_list
            )

    def parse_list(self, ihouse):
        saveinfo = {}
        saveinfo["house_id"] = ihouse.url
        yield saveinfo

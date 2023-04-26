import pandas
import pymysql
from sklearn.preprocessing import LabelEncoder as LE
from sklearn.linear_model import LinearRegression as LR




##构建预测函数
def wage_pred(size, hx, city):
    # 将各字符分类变量重编码为数值分类变量
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    sql = "select area,title,city,price from house_copy"
    cursor.execute(sql)
    result = cursor.fetchall()
    filter_item = []
    for ire in result:
        filter_item.append({
            "面积":int(ire[0]),
            "户型":ire[1].split(" ")[-1],
            "城市": ire[2],
            "价格":float(ire[3])
        })

    le = LE()
    huxings = [i.get('户型') for i in filter_item]
    cityss = [i.get('城市') for i in filter_item]
    newcitys = []
    for i in cityss:
        if i in newcitys:
            continue
        else:
            newcitys.append(i)

    newhuxing = []
    for i in huxings:
        if i in newhuxing:
            continue
        else:
            newhuxing.append(i)
    huxing_hot = dict([(i[1],i[0]) for i in enumerate(newhuxing)])

    city_hot = dict([(i[1],i[0]) for i in enumerate(newcitys)])

    print(huxing_hot)
    print(city_hot)


    jobs = pandas.DataFrame(filter_item)
    jobs['户型'] = jobs['户型'].apply(lambda x:huxing_hot[x])
    jobs['城市'] = jobs['城市'].apply(lambda x: city_hot[x])
    ## 特征选择
    X = jobs[['面积', '户型', '城市']]
    ## 结果集
    y = jobs['价格']
    print(jobs)
    ## 模型学习
    model = LR()
    model.fit(X, y)
    hx_index = huxing_hot.get(hx)
    city_index = city_hot.get(city)
    wage_pred = model.predict([[size, hx_index, city_index]])
    print('%.2f' % wage_pred)


## 测试代码
if __name__ == '__main__':
    wage_pred(100, '3室1厅1卫', '兰州')

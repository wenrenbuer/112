import jieba
import jieba.analyse
import numpy as np
from flask import Flask, request, jsonify
import pymysql
from flask_cors import *
import pickle
import pandas
import pymysql
from sklearn.preprocessing import LabelEncoder as LE
from sklearn.linear_model import LinearRegression as LR
from textRank import LocalTextRank

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app, supports_credentials=True)

from flask.json import JSONEncoder as _JSONEncoder
from flask import render_template

class JSONEncoder(_JSONEncoder):
    def default(self, o):
        import decimal
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(JSONEncoder, self).default(o)
app.json_encoder = JSONEncoder






@app.route('/zufang_data',methods=['GET'])
def zufang_data():
    limit = int(request.args['limit'])
    page = int(request.args['page'])
    page = (page-1)*limit
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')

    cursor = conn.cursor()
    if (len(request.args) == 2):
        cursor.execute("select count(*) from house_copy;")
        count = cursor.fetchall()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute("select * from house_copy limit "+str(page)+","+str(limit))
        data_dict = []
        result = cursor.fetchall()
        for field in result:
            data_dict.append(field)
    else:
        city = str(request.args['city'])
        cursor.execute("select count(*) from house_copy where city = '"+city+"';")
        count = cursor.fetchall()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute("select * from house_copy where city = '"+city+"' limit " + str(page) + "," + str(limit))
        data_dict = []
        result = cursor.fetchall()
        for field in result:
            data_dict.append(field)
    table_result = {"code": 0, "msg": None, "count": count[0], "data": data_dict}
    cursor.close()
    conn.close()
    return jsonify(table_result)


#注册用户
@app.route('/addUser',methods=['POST'])
def addUser():
    #服务器端获取json
    get_json = request.get_json()
    name = get_json['name']
    password = get_json['password']
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("select count(*) from `user` where `username` = '" + name + "'")
    count = cursor.fetchall()
    #该昵称已存在
    if (count[0][0]!= 0):
        table_result = {"code": 500, "msg": "该昵称已存在！"}
        cursor.close()
    else:
        add = conn.cursor()
        sql = "insert into `user`(username,password) values('"+name+"','"+password+"');"
        add.execute(sql)
        conn.commit()
        table_result = {"code": 200, "msg": "注册成功"}
        add.close()
    conn.close()
    return jsonify(table_result)
#用户登录
@app.route('/loginByPassword',methods=['POST'])
def loginByPassword():
    get_json = request.get_json()
    name = get_json['name']
    password = get_json['password']
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("select count(*) from `user` where `username` = '" + name +"' and password = '" + password+"';")
    count = cursor.fetchall()
    if(count[0][0] != 0):
        table_result = {"code": 200, "msg": name}
        cursor.close()
    else:
        name_cursor = conn.cursor()
        name_cursor.execute("select count(*) from `user` where `username` = '" + name +"';")
        name_count = name_cursor.fetchall()
        #print(name_count)
        if(name_count[0][0] != 0):
            table_result = {"code":500, "msg": "密码错误！"}
        else:
            table_result = {"code":500, "msg":"该用户不存在，请先注册！"}
        name_cursor.close()
    conn.close()
    print(name)
    return jsonify(table_result)
#密码修改
@app.route('/updatePass',methods=['POST'])
def updatePass():
    get_json = request.get_json()
    name = get_json['name']
    oldPsw = get_json['oldPsw']
    newPsw = get_json['newPsw']
    rePsw = get_json['rePsw']
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("select count(*) from `user` where `username` = '" + name + "' and password = '" + oldPsw+"';")
    count = cursor.fetchall()
    print(count[0][0])
    #确定昵称密码对应
    if (count[0][0] == 0):
        table_result = {"code": 500, "msg": "原始密码错误！"}
        cursor.close()
    else:
        updatepass = conn.cursor()
        sql = "update `user` set password = '"+newPsw+"' where username = '"+ name +"';"
        updatepass.execute(sql)
        conn.commit()
        table_result = {"code": 200, "msg": "密码修改成功！", "username": name, "new_password": newPsw}
        updatepass.close()
    conn.close()
    return jsonify(table_result)
#个人信息修改
@app.route('/updateUserInfo',methods=['POST'])
def updateUserInfo():
    get_json = request.get_json()
    name = get_json['name']
    print(name)
    email = get_json['email']
    content = get_json['content']
    address = get_json['address']
    phone = get_json['phone']
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("update `user` set email = '"+email+"',content = '"+content+"',address = '"+address+"',phone = '"+phone+"' where username = '"+ name +"';")
    conn.commit()
    table_result = {"code": 200, "msg": "更新成功！","youxiang": email, "tel": phone}
    cursor.close()
    conn.close()
    print(table_result)
    return jsonify(table_result)
#密保手机修改
@app.route('/updateUserPhone',methods=['POST'])
def updateUserPhone():
    get_json = request.get_json()
    name = get_json['name']
    tel = get_json['tel']
    youxiang = get_json['youxiang']
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("update `user` set email = '"+youxiang+"',phone = '"+tel+"' where username = '"+ name +"';")
    conn.commit()
    table_result = {"code": 200, "msg": "修改成功！","youxiang": youxiang, "tel": tel}
    cursor.close()
    conn.close()
    print(table_result)
    return jsonify(table_result)
#密保邮箱修改
@app.route('/updateUserEmail',methods=['POST'])
def updateUserEmail():
    get_json = request.get_json()
    name = get_json['name']
    print(name)
    email = get_json['email']
    content = get_json['content']
    address = get_json['address']
    phone = get_json['phone']
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("update `user` set email = '"+email+"',content = '"+content+"',address = '"+address+"',phone = '"+phone+"' where username = '"+ name +"';")
    conn.commit()
    table_result = {"code": 200, "msg": "更新成功！","youxiang": email, "tel": phone}
    cursor.close()
    conn.close()
    print(table_result)
    return jsonify(table_result)
#个人信息查询
@app.route('/selectUserInfo',methods=['GET'])
def selectUserInfo():
    name = str(request.args['name'])
    print(name)
    email = []
    content = []
    address = []
    phone = []
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    #邮箱
    cursor.execute("select email from user where username = '"+ name +"';")
    result = cursor.fetchall()
    for field in result:
        email.append(field[0])
    #个人简介
    cursor.execute("select content from user where username = '" + name + "';")
    result = cursor.fetchall()
    for field in result:
        content.append(field[0])
    #地址
    cursor.execute("select address from user where username = '" + name + "';")
    result = cursor.fetchall()
    for field in result:
        address.append(field[0])
    #联系方式
    cursor.execute("select phone from user where username = '" + name + "';")
    result = cursor.fetchall()
    for field in result:
        phone.append(field[0])
    table_result = {"code": 200, "msg": "查询成功！","name": name, "email": email, "content": content, "address": address, "phone": phone, "tel": phone, "youxiang": email}
    cursor.close()
    conn.close()
    print(table_result)
    return jsonify(table_result)
@app.route('/predict',methods=['GET'])
def predict():
    size = float(request.args["size"])
    hx = request.args["huxing"]
    city = request.args["city"]
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
    return jsonify('%.2f' % wage_pred)



@app.route('/area',methods=['GET'])
def area():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡', '181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    #<=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20;")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    #21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40;")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60;")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80;")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100;")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120;")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140;")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160;")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180;")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200;")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    cursor.close()
    print(area_data)
    return jsonify({"area_kind": area_kind, "area_data": area_data})

@app.route('/area_first',methods=['GET'])
def area_first():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡', '181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    #<=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    #21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    cursor.close()
    print(area_data)
    return jsonify({"area_kind": area_kind, "area_data": area_data})

@app.route('/area_nfirst',methods=['GET'])
def area_nfirst():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡', '181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    #<=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    #21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    cursor.close()
    print(area_data)
    return jsonify({"area_kind": area_kind, "area_data": area_data})

@app.route('/area_second',methods=['GET'])
def area_second():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡', '181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    #<=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    #21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    area_data.append(count[0][0])
    cursor.close()
    print(area_data)
    return jsonify({"area_kind": area_kind, "area_data": area_data})

@app.route('/floor',methods=['GET'])
def floor():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(floor) from house_copy;")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "'")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    cursor.close()
    return jsonify({"floor_kind": floor_kind, "floor_data": floor_data})

@app.route('/floor_first',methods=['GET'])
def floor_first():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city in ('北京','上海','深圳');")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city in ('北京','上海','深圳');")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    cursor.close()
    return jsonify({"floor_kind": floor_kind, "floor_data": floor_data})

@app.route('/floor_nfirst',methods=['GET'])
def floor_nfirst():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city in ('杭州','南京','武汉','西安','成都','重庆');")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city in ('杭州','南京','武汉','西安','成都','重庆');")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    cursor.close()
    return jsonify({"floor_kind": floor_kind, "floor_data": floor_data})

@app.route('/floor_second',methods=['GET'])
def floor_second():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    cursor.close()
    return jsonify({"floor_kind": floor_kind, "floor_data": floor_data})

@app.route('/orient',methods=['GET'])
def orient():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(orient) from house_copy;")
    result = cursor.fetchall()
    orient_kind = []
    orient_data = []
    # 获取到朝向的几种情况
    for field in result:
        orient_kind.append(field[0])
    # 获取到每种朝向类型对应的个数
    for i in range(len(orient_kind)):
        cursor.execute("SELECT count(*) from house_copy where orient = '" + orient_kind[i] + "'")
        count = cursor.fetchall()
        orient_data.append({'value': count[0][0], 'name': orient_kind[i]})
    cursor.close()
    print(orient_data)
    return jsonify({"orient_kind": orient_kind, "orient_data": orient_data})

@app.route('/orient_first',methods=['GET'])
def orient_first():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(orient) from house_copy where city in ('北京','上海','深圳');")
    result = cursor.fetchall()
    orient_kind = []
    orient_data = []
    # 获取到朝向的几种情况
    for field in result:
        orient_kind.append(field[0])
    # 获取到每种朝向类型对应的个数
    for i in range(len(orient_kind)):
        cursor.execute("SELECT count(*) from house_copy where orient = '" + orient_kind[i] + "' and city in ('北京','上海','深圳');")
        count = cursor.fetchall()
        orient_data.append({'value': count[0][0], 'name': orient_kind[i]})
    cursor.close()
    print(orient_data)
    return jsonify({"orient_kind": orient_kind, "orient_data": orient_data})

@app.route('/orient_nfirst',methods=['GET'])
def orient_nfirst():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(orient) from house_copy where city in ('杭州','南京','武汉','西安','成都','重庆');")
    result = cursor.fetchall()
    orient_kind = []
    orient_data = []
    # 获取到朝向的几种情况
    for field in result:
        orient_kind.append(field[0])
    # 获取到每种朝向类型对应的个数
    for i in range(len(orient_kind)):
        cursor.execute("SELECT count(*) from house_copy where orient = '" + orient_kind[i] + "' and city in ('杭州','南京','武汉','西安','成都','重庆');")
        count = cursor.fetchall()
        orient_data.append({'value': count[0][0], 'name': orient_kind[i]})
    cursor.close()
    print(orient_data)
    return jsonify({"orient_kind": orient_kind, "orient_data": orient_data})

@app.route('/orient_second',methods=['GET'])
def orient_second():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(orient) from house_copy where city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    result = cursor.fetchall()
    orient_kind = []
    orient_data = []
    # 获取到朝向的几种情况
    for field in result:
        orient_kind.append(field[0])
    # 获取到每种朝向类型对应的个数
    for i in range(len(orient_kind)):
        cursor.execute("SELECT count(*) from house_copy where orient = '" + orient_kind[i] + "' and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
        count = cursor.fetchall()
        orient_data.append({'value': count[0][0], 'name': orient_kind[i]})
    cursor.close()
    print(orient_data)
    return jsonify({"orient_kind": orient_kind, "orient_data": orient_data})

@app.route('/price',methods=['GET'])
def price():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000', '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000;")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000;")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000;")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000;")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000;")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000;")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000;")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000;")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000;")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000;")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000;")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    cursor.close()
    print(price_data)
    return jsonify({"price_kind": price_kind, "price_data": price_data})

@app.route('/price_first',methods=['GET'])
def price_first():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000', '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种类别类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    cursor.close()
    print(price_data)
    return jsonify({"price_kind": price_kind, "price_data": price_data})

@app.route('/price_nfirst',methods=['GET'])
def price_nfirst():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000', '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种类别类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    cursor.close()
    print(price_data)
    return jsonify({"price_kind": price_kind, "price_data": price_data})

@app.route('/price_second',methods=['GET'])
def price_second():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000', '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种类别类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    cursor.close()
    print(price_data)
    return jsonify({"price_kind": price_kind, "price_data": price_data})

@app.route('/relation',methods=['GET'])
def relation():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    relation_data = []
    cursor.execute("select count(*) from house_copy;")
    count = cursor.fetchall()
    #print(count[0][0])
    cursor.execute("SELECT area,price from house_copy;")
    result = cursor.fetchall()
    for i in range(count[0][0]):
        relation_data.append(list(result[i]))
    #print(relation_data)
    cursor.close()
    return jsonify({"relation_data": relation_data})

@app.route('/relation_first',methods=['GET'])
def relation_first():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    relation_data = []
    cursor.execute("select count(*) from house_copy where city in ('北京','上海','深圳');")
    count = cursor.fetchall()
    #print(count[0][0])

    cursor.execute("SELECT area,price from house_copy where city in ('北京','上海','深圳');")
    result = cursor.fetchall()
    for i in range(count[0][0]):
        relation_data.append(list(result[i]))
    #print(relation_data)
    cursor.close()
    return jsonify({"relation_data": relation_data})

@app.route('/relation_nfirst',methods=['GET'])
def relation_nfirst():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    relation_data = []
    cursor.execute("select count(*) from house_copy where city in ('杭州','南京','武汉','西安','成都','重庆');")
    count = cursor.fetchall()
    #print(count[0][0])

    cursor.execute("SELECT area,price from house_copy where city in ('杭州','南京','武汉','西安','成都','重庆');")
    result = cursor.fetchall()
    for i in range(count[0][0]):
        relation_data.append(list(result[i]))
    #print(relation_data)
    cursor.close()
    return jsonify({"relation_data": relation_data})

@app.route('/relation_second',methods=['GET'])
def relation_second():
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    cursor = conn.cursor()
    relation_data = []
    cursor.execute("select count(*) from house_copy where city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    count = cursor.fetchall()
    #print(count[0][0])

    cursor.execute("SELECT area,price from house_copy where city in ('兰州','大连','贵阳','石家庄','太原','徐州');")
    result = cursor.fetchall()
    for i in range(count[0][0]):
        relation_data.append(list(result[i]))
    #print(relation_data)
    cursor.close()
    return jsonify({"relation_data": relation_data})

@app.route('/bj',methods=['GET'])
def bj():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '北京';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '北京';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '北京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '北京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '北京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '北京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '北京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '北京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '北京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '北京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '北京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '北京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '北京';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '北京';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '北京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max': 500})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '北京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max': 500})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '北京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max': 500})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '北京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 500})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '北京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 500})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '北京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 500})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '北京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 500})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '北京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 500})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '北京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 500})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '北京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 500})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '北京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 500})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/sh',methods=['GET'])
def sh():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '上海';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '上海';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '上海';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '上海';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '上海';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '上海';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '上海';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '上海';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '上海';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '上海';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '上海';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '上海';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '上海';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '上海';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '上海';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max': 700})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '上海';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max': 700})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '上海';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max': 700})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '上海';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 700})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '上海';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 700})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '上海';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 700})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '上海';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 700})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '上海';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 700})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '上海';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 700})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '上海';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 700})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '上海';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 700})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/sz',methods=['GET'])
def sz():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '深圳';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '深圳';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '深圳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '深圳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '深圳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '深圳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '深圳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '深圳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '深圳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '深圳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '深圳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '深圳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '深圳';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '深圳';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '深圳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max': 400})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '深圳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max': 400})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '深圳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max': 400})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '深圳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 400})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '深圳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 400})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '深圳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 400})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '深圳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 400})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '深圳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 400})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '深圳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 400})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '深圳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 400})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '深圳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 400})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/hz',methods=['GET'])
def hz():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '杭州';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '杭州';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '杭州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '杭州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '杭州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '杭州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '杭州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '杭州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '杭州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '杭州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '杭州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '杭州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '杭州';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '杭州';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '杭州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max': 600})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '杭州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max': 600})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '杭州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max': 600})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '杭州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 600})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '杭州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 600})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '杭州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 600})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '杭州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 600})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '杭州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 600})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '杭州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 600})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '杭州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 600})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '杭州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 600})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/wh',methods=['GET'])
def wh():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '武汉';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '武汉';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '武汉';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '武汉';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '武汉';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '武汉';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '武汉';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '武汉';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '武汉';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '武汉';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '武汉';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '武汉';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '武汉';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '武汉';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '武汉';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max': 1000})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '武汉';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max': 1000})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '武汉';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max': 1000})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '武汉';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 1000})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '武汉';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 1000})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '武汉';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 1000})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '武汉';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 1000})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '武汉';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 1000})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '武汉';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 1000})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '武汉';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 1000})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '武汉';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 1000})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/nj',methods=['GET'])
def nj():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '南京';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '南京';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '南京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '南京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '南京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '南京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '南京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '南京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '南京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '南京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '南京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '南京';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '南京';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '南京';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '南京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max': 1000})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '南京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max': 1000})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '南京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max': 1000})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '南京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 1000})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '南京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 1000})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '南京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 1000})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '南京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 1000})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '南京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 1000})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '南京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 1000})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '南京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 1000})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '南京';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 1000})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/xa',methods=['GET'])
def xa():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '西安';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '西安';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '西安';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '西安';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '西安';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '西安';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '西安';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '西安';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '西安';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '西安';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '西安';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '西安';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '西安';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '西安';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '西安';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max': 900})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '西安';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max': 900})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '西安';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max': 900})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '西安';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 900})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '西安';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 900})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '西安';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 900})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '西安';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 900})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '西安';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 900})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '西安';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 900})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '西安';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 900})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '西安';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 900})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/cq',methods=['GET'])
def cq():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '重庆';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '重庆';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '重庆';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '重庆';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '重庆';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '重庆';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '重庆';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '重庆';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '重庆';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '重庆';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '重庆';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '重庆';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '重庆';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '重庆';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '重庆';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max': 1200})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '重庆';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max': 1200})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '重庆';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max': 1200})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '重庆';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 1200})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '重庆';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 1200})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '重庆';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 1200})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '重庆';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 1200})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '重庆';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 1200})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '重庆';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 1200})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '重庆';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 1200})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '重庆';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 1200})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/cd',methods=['GET'])
def cd():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '成都';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '成都';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '成都';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '成都';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '成都';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '成都';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '成都';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '成都';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '成都';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '成都';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '成都';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '成都';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '成都';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '成都';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '成都';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max':1100})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '成都';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max':1100})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '成都';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max':1100})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '成都';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 1100})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '成都';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 1100})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '成都';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 1100})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '成都';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 1100})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '成都';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 1100})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '成都';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 1100})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '成都';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 1100})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '成都';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 1100})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/lz',methods=['GET'])
def lz():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '兰州';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '兰州';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '兰州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '兰州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '兰州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '兰州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '兰州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '兰州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '兰州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '兰州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '兰州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '兰州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '兰州';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '兰州';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '兰州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max':1200})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '兰州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max':1200})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '兰州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max':1200})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '兰州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 1200})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '兰州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 1200})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '兰州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 1200})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '兰州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 1200})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '兰州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 1200})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '兰州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 1200})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '兰州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 1200})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '兰州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 1200})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/dl',methods=['GET'])
def dl():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '大连';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '大连';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '大连';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '大连';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '大连';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '大连';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '大连';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '大连';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '大连';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '大连';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '大连';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '大连';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '大连';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '大连';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '大连';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max':1000})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '大连';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max':1000})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '大连';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max':1000})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '大连';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 1000})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '大连';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 1000})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '大连';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 1000})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '大连';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 1000})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '大连';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 1000})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '大连';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 1000})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '大连';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 1000})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '大连';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 1000})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/gy',methods=['GET'])
def gy():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '贵阳';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '贵阳';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '贵阳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '贵阳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '贵阳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '贵阳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '贵阳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '贵阳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '贵阳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '贵阳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '贵阳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '贵阳';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '贵阳';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '贵阳';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '贵阳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max':1300})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '贵阳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max':1300})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '贵阳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max':1300})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '贵阳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 1300})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '贵阳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 1300})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '贵阳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 1300})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '贵阳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 1300})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '贵阳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 1300})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '贵阳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 1300})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '贵阳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 1300})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '贵阳';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 1300})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/sjz',methods=['GET'])
def sjz():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '石家庄';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '石家庄';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '石家庄';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '石家庄';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '石家庄';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '石家庄';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '石家庄';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '石家庄';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '石家庄';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '石家庄';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '石家庄';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '石家庄';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '石家庄';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '石家庄';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '石家庄';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max': 1700})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '石家庄';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max': 1700})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '石家庄';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max': 1700})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '石家庄';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 1700})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '石家庄';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 1700})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '石家庄';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 1700})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '石家庄';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 1700})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '石家庄';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 1700})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '石家庄';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 1700})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '石家庄';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 1700})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '石家庄';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 1700})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/ty',methods=['GET'])
def ty():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '太原';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '太原';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '太原';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '太原';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '太原';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '太原';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '太原';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '太原';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '太原';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '太原';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '太原';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '太原';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '太原';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '太原';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '太原';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max':1600})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '太原';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max':1600})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '太原';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max':1600})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '太原';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 1600})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '太原';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 1600})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '太原';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 1600})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '太原';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 1600})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '太原';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 1600})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '太原';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 1600})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '太原';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 1600})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '太原';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 1600})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})

@app.route('/xz',methods=['GET'])
def xz():
    # 打开数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    # 行政区
    cursor.execute("SELECT DISTINCT(district) from house_copy where city = '徐州';")
    result = cursor.fetchall()
    district = []
    district_data = []
    for field in result:
        district.append(field[0])
    for i in range(len(district)):
        cursor.execute("SELECT count(*) from house_copy where district = '" + district[i] + "' and city = '徐州';")
        count = cursor.fetchall()
        district_data.append({'value': count[0][0], 'name': district[i]})
    #面积
    area_kind = ['<=20㎡', '21~40㎡', '41~60㎡', '61~80㎡', '81~100㎡', '101~120㎡', '121~140㎡', '141~160㎡', '161~180㎡','181~200㎡']
    area_data = []
    # 获取到每种面积类别对应的个数
    # <=20㎡
    cursor.execute("SELECT count(*) from house_copy where area between 0 and 20 and city = '徐州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[0]})
    # 21~40㎡
    cursor.execute("SELECT count(*) from house_copy where area between 21 and 40 and city = '徐州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[1]})
    # 41~60㎡
    cursor.execute("SELECT count(*) from house_copy where area between 41 and 60 and city = '徐州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[2]})
    # 61~80㎡
    cursor.execute("SELECT count(*) from house_copy where area between 61 and 80 and city = '徐州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[3]})
    # 81~100㎡
    cursor.execute("SELECT count(*) from house_copy where area between 81 and 100 and city = '徐州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[4]})
    # 101~120㎡
    cursor.execute("SELECT count(*) from house_copy where area between 101 and 120 and city = '徐州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[5]})
    # 121~140㎡
    cursor.execute("SELECT count(*) from house_copy where area between 121 and 140 and city = '徐州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[6]})
    # 141~160㎡
    cursor.execute("SELECT count(*) from house_copy where area between 141 and 160 and city = '徐州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[7]})
    # 161~180㎡
    cursor.execute("SELECT count(*) from house_copy where area between 161 and 180 and city = '徐州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[8]})
    # 181~200㎡
    cursor.execute("SELECT count(*) from house_copy where area between 181 and 200 and city = '徐州';")
    count = cursor.fetchall()
    area_data.append({'value': count[0][0], 'name':area_kind[9]})
    #楼层
    cursor.execute("SELECT DISTINCT(floor) from house_copy where city = '徐州';")
    result = cursor.fetchall()
    floor_kind = []
    floor_data = []
    # 获取到楼层的几种情况
    for field in result:
        floor_kind.append(field[0])
    # 获取到每种楼层类型对应的个数
    for i in range(len(floor_kind)):
        cursor.execute("SELECT count(*) from house_copy where floor = '" + floor_kind[i] + "' and city = '徐州';")
        count = cursor.fetchall()
        floor_data.append({'value': count[0][0], 'name': floor_kind[i]})
    #价格
    max_dict = []
    price_kind = ['<=1000', '1001~2000', '2001~3000', '3001~4000', '4001~5000', '5001~6000', '6001~7000', '7001~8000',
                  '8001~9000', '9001~10000', '>10000']
    price_data = []
    # 获取到每种价格类别对应的个数
    # <=1000
    cursor.execute("SELECT count(*) from house_copy where price between 0 and 1000 and city = '徐州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[0], 'max':1600})
    # 1001~2000
    cursor.execute("SELECT count(*) from house_copy where price between 1001 and 2000 and city = '徐州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[1], 'max':1600})
    # 2001~3000
    cursor.execute("SELECT count(*) from house_copy where price between 2001 and 3000 and city = '徐州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[2], 'max':1600})
    # 3001~4000
    cursor.execute("SELECT count(*) from house_copy where price between 3001 and 4000 and city = '徐州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[3], 'max': 1600})
    # 4001~5000
    cursor.execute("SELECT count(*) from house_copy where price between 4001 and 5000 and city = '徐州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[4], 'max': 1600})
    # 5001~6000
    cursor.execute("SELECT count(*) from house_copy where price between 5001 and 6000 and city = '徐州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[5], 'max': 1600})
    # 6001~7000
    cursor.execute("SELECT count(*) from house_copy where price between 6001 and 7000 and city = '徐州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[6], 'max': 1600})
    # 7001~8000
    cursor.execute("SELECT count(*) from house_copy where price between 7001 and 8000 and city = '徐州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[7], 'max': 1600})
    # 8001~9000
    cursor.execute("SELECT count(*) from house_copy where price between 8001 and 9000 and city = '徐州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[8], 'max': 1600})
    # 9001~10000
    cursor.execute("SELECT count(*) from house_copy where price between 9001 and 10000 and city = '徐州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[9], 'max': 1600})
    # >10000
    cursor.execute("SELECT count(*) from house_copy where price >10000 and city = '徐州';")
    count = cursor.fetchall()
    price_data.append(count[0][0])
    max_dict.append({'name': price_kind[10], 'max': 1600})

    cursor.close()
    return jsonify({"district":district, "district_data":district_data, "area_data":area_data, "floor_kind":floor_kind, "floor_data":floor_data,
                    "price_data":price_data, "max_dict":max_dict})


# @app.route('/xz',methods=['GET'])
# def xz():
#     
#     return render_template("/UI_Pages/page/")


@app.route("/del_item",methods=['GET'])
def del_item():
    print(request.args)
    sql = "delete from house_copy where house_id = '%s'" % (request.args["house_id"])
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    cursor.execute(sql)
    print(sql)
    conn.commit()
    return jsonify({})

@app.route("/update_item",methods=['GET'])
def update_item():
    print(request.args)
    sql = "delete from house_copy where house_id = '%s'" % (request.args["house_id"])
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    item = request.args
    sql = "insert into house_copy values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
        f'{item["title"]}',
        item["district"],
        item["area"].replace("㎡", ''),
        item["orient"],
        item["floor"],
        item["price"],
        item["city"],
        item["image"],
        item["xiaoqu"],
        item["address"],
        item["tags"],
        item["average_price"],
        item["house_id"]
    )

    cursor.execute(sql)
    conn.commit()

    return jsonify({})

@app.route("/shoucang")
def shoucang():

    print(request.args)
    sql = "insert into choucang(houseid,userid) values('%s','%s')" % (request.args["house_id"],request.args["user"])
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

    return jsonify({})
@app.route("/shoucangssss")
def shoucangssss():
    print(request.args)
    sql = "select * from choucang where userid = '%s'" % (request.args["user"])
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql)
    urls = [i.get("houseid") for i in cursor.fetchall()]
    results = []
    for iurl in urls:
        sql = "select * from house_copy where house_id = '%s'" % (iurl)
        cursor.execute(sql)
        result= cursor.fetchone()
        result['user'] = request.args["user"]
        results.append(result)
    table_result = {"code": 0, "msg": None, "count": len(results), "data": results}
    return jsonify(table_result)


@app.route("/cruuent")
def cruuent():
    print(request.args)
    search = str(request.args['search'])
    print(f'args:{search}')
    conn = pymysql.connect(host='localhost', user='root', password='961948438', port=3306, db='anjuke_db',
                           charset='utf8mb4')
    # 创建一个游标对象cursor
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    sql = "select * from  house_copy where city like '%" + search + "%' "
    print(sql)
    cursor.execute(sql)
    records = cursor.fetchall()

    content = " ".join([i.get("title") for i in records])

    print(content)
    tr = LocalTextRank(content, 3, 0.85, 700)
    tr.cutSentence()
    tr.createNodes()
    tr.createMatrix()
    tr.calPR()
    rs = tr.printResult()
    return jsonify({
        "data":rs
    })


if __name__ == "__main__":
   app.run(port=5000)
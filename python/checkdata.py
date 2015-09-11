#!/usr/bin/python
# coding: utf-8
__author__ = 'tangjia'

import requests
import json
import mysql.connector
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
from pymongo import MongoClient
from urllib import urlencode
import datetime
import time
import pymongo

JSON_HEADER = {'content-type': 'applocation/json'}

REST_HOST = "https://a1.easemob.com"
APP_KEY = "fahaicom#baymax"
APP_CLIENT_ID = "YXA6qzxTcAmWEeWG_fVPP2mf6g"
APP_CLIENT_SECRET = "YXA6FVCmT-5D0SHkLgXBtXlPsdjxMwk"
REQU_URL = REST_HOST + '/' + APP_KEY.split("#")[0] + "/" + APP_KEY.split("#")[1];

conn = mysql.connector.connect(host='123.56.102.50', user='checkdata', password='123456', db='common',
                               port='9527')
client = MongoClient('10.10.1.8', 27017)
db = client["message"]
collection = db["message"]


def post(url, param_data):
    return requests.post(url, data=json.dumps(param_data), headers=JSON_HEADER).json();


def get(url):
    response = requests.get(url, headers=JSON_HEADER)
    response.encoding = 'utf-8'
    return response.json()


def get_token():
    param_data = {
        "grant_type": "client_credentials",
        "client_id": APP_CLIENT_ID,
        "client_secret": APP_CLIENT_SECRET
    }
    return post(REQU_URL + '/token', param_data);


def get_all_hx_users():
    url = REQU_URL + "/users?limit=1000"
    return get(url)["entities"]


def get_hx_user_frdlist(user_id):
    url = REQU_URL + "/users/" + user_id + "/contacts/users"
    return get(url)["data"]


def get_all_hx_group_id():
    url = REQU_URL + "/chatgroups"
    return get(url)["data"]


# owner+menber  set
def get_hx_group_member(group_id):
    url = REQU_URL + "/chatgroups/" + group_id + "/users"
    return get(url)["data"]


def get_group_info(group_id):
    url = REQU_URL + "/chatgroups/" + group_id
    return get(url)


def get_all_db_users_id():
    cursor = conn.cursor()
    cursor.execute('select huanxinuser from commonUserInfo')
    return cursor.fetchall()


def get_all_db_hxgroup_id():
    cursor = conn.cursor()
    cursor.execute('select hxgroupid from commonGroup')
    return cursor.fetchall()


def get_db_group_member_set(groupid):
    cursor = conn.cursor();
    sql = ("select members  from commonGroupMember where id = %d" % int(groupid))
    cursor.execute(sql)
    return list_turple_list_to_set(cursor.fetchall())


def get_db_frdlist_set(hx_user_id):
    db_user_id = get_db_userid_by_hx_id(hx_user_id)
    cursor = conn.cursor();
    sql = ("select friends from commonFriends where userid = %d " % int(db_user_id))
    cursor.execute(sql)
    frdlist = cursor.fetchall()
    if len(frdlist) == 0:
        return set('')
    return list_turple_list_to_set(frdlist)


def get_db_usr_frdlist():
    cursor = conn.cursor('select id from commonFriends ')
    pass;


def get_db_groupid_by_hx_id(hx_group_id):
    cursor = conn.cursor();
    sql = ("select id  from commonGroup where hxgroupid = \'%s\'" % hx_group_id)
    cursor.execute(sql)
    return cursor.fetchone()[0]


def get_db_userid_by_hx_id(hx_user_id):
    cursor = conn.cursor();
    sql = ("select userid  from commonUserInfo where huanxinuser = \'%s\'" % hx_user_id)
    cursor.execute(sql)
    return cursor.fetchone()[0]


def difference_in_group(set_in_all):
    print("检查群组列表")
    for hx_group_id in set_in_all:
        db_group_id = get_db_groupid_by_hx_id(hx_group_id)
        set_db_group_member = db_user_id_set_to_hx(get_db_group_member_set(db_group_id))
        # 转环信GROUP_ID
        set_hx_group_member = get_hx_group_member_set(get_hx_group_member(hx_group_id))
        if len(compare_set(set_db_group_member, set_hx_group_member)[0]) > 0:
            print("以下用户在数据库群组环信ID为 "+hx_group_id+" 存在而在环信群组不存在:")
            print(hx_group_id)
            print(compare_set(set_db_group_member, set_hx_group_member)[0])
        if len(compare_set(set_db_group_member, set_hx_group_member)[1]) > 0:
            print("以下用户在环信群组ID为 "+hx_group_id+" 存在而在数据库群组不存在:")
            print(hx_group_id)
            print(compare_set(set_db_group_member, set_hx_group_member)[1])


def difference_in_frdlist(set_in_all):
    print("检查好友列表")
    for hx_user_id in set_in_all:
        set_hx_frdlist = (set(get_hx_user_frdlist(hx_user_id)))
        set_db_frdlist = db_user_id_set_to_hx(get_db_frdlist_set(hx_user_id))
        if len(compare_set(set_db_frdlist, set_hx_frdlist)[0]) > 0:
            print("以下用户在数据库好友环信ID为: "+hx_user_id+" 列表存在而在环信列表不存在:")
            print(compare_set(set_db_frdlist, set_hx_frdlist)[0])
        if len(compare_set(set_db_frdlist, set_hx_frdlist)[1]) > 0:
            print("以下用户在环信用户ID为: "+hx_user_id+" 存在而在数据库好友列表不存在:")
            print(compare_set(set_db_frdlist, set_hx_frdlist)[1])


def db_user_id_to_hx(db_user_id):
    cursor = conn.cursor();
    sql = ("select huanxinuser from commonUserInfo where userid = \'%s\' " % db_user_id)
    cursor.execute(sql)
    return cursor.fetchone()


def db_user_id_set_to_hx(db_user_set):
    hx_userid_list = [];
    for db_user_id in db_user_set:
        if db_user_id_to_hx(db_user_id) is None:
            continue
        else:
            hx_userid_list.append("".join(db_user_id_to_hx(db_user_id)))
    return set(hx_userid_list)


def compareUser():
    pass


def compare_set(set_a, set_b):
    set_a_not_in_b = set_a - set_b
    set_b_not_in_a = set_b - set_a
    set_in_a_and_b = set_a & set_b
    return set_a_not_in_b, set_b_not_in_a, set_in_a_and_b


# 针对环信数据
def dirc_list_to_set(list, property):
    return set(map(lambda x: x[property], list))


# 针对群组成员
def get_hx_group_member_set(list):
    list1 = []
    if len(list) == 1:
        return set(map(lambda x: x['owner'], list))
    else:
        for x in list:
            for value in x.itervalues():
                list1.append(value)
    return set(list1)


def get_hx_member(x):
    if x["owner"] is None:
        return x["member"]
    else:
        return x["owner"]


# 针对数据库数据
def truple_list_to_set(list1):
    return set(map(lambda x: "".join(x if isinstance(x[0], str) else str(x[0])), list1))


def list_turple_list_to_set(list1):
    return set(list((list1[0][0][1:-1]).split(",")))


# -------------db
def get_db_id_set(table_name):
    cursor = conn.cursor()
    sql = ("select id from %s" % table_name)
    if table_name == "commonFriends":
        sql = ("select userid from %s" % table_name)
    cursor.execute(sql)
    return truple_list_to_set(cursor.fetchall())


def check_extra_users_in_db():
    print("检查本地数据库")
    print('检查本地数据库的群组列表中用户是否已被删除')
    set_user_id = get_db_id_set("commonUser")
    set_group_info_id = get_db_id_set("commonGroup");
    set_group_member_id = get_db_id_set("commonGroupMember")
    if len(compare_set(set_group_info_id, set_group_member_id)[1]) > 0:
        print("以下群组成员数据（commonGroupMember）可以删除")
        print(compare_set(set_group_info_id, set_group_member_id)[1])
    for group_id in compare_set(set_group_info_id, set_group_member_id)[2]:
        db_group_member_set = get_db_group_member_set(group_id)
        for user_id in db_group_member_set:
            # cursor = conn.cursor()
            # sql = ("select * from commonUser where id =\'%d\'" %int(user_id))
            # cursor.execute(sql)
            # if len(cursor.fetchall()) == 0:
            #     print("群组id为 ：" + group_id + "的" + user_id + "在用户表中已被删除")
            if (str(user_id)).strip() not in set_user_id:
                print("群组id为:" + group_id + "的" + user_id + "在用户表中已被删除")
    print('检查本地数据库的好友列表中用户是否已被删除')
    set_frdlist_user_id = get_db_id_set("commonFriends")
    if len(compare_set(set_user_id, set_frdlist_user_id)[1]) > 0:
        print("以下好友列表中的数据（commonFriends）可以删除")
        print(compare_set(set_user_id, set_frdlist_user_id)[1])
    for frd_id in compare_set(set_user_id, set_frdlist_user_id)[2]:
        db_frdlist_set = get_db_frdlist_set(db_user_id_to_hx(frd_id))
        for user_id in db_frdlist_set:
            # cursor = conn.cursor()
            # if user_id == "":
            #     continue
            # sql = ("select * from commonUser where id = %d"%int(round(float(user_id))))
            # cursor.execute(sql)
            # if len(cursor.fetchall()) == 0:
            #     print("好友列表id为 ：" + frd_id + "的" + user_id + "在用户表中已被删除")
            if (str(user_id)).strip() not in set_user_id:
                print("群组id为:" + group_id + "的" + user_id + "在用户表中已被删除")


def get_chatmessages(begin_timestamp):
    time_query = urlencode({'ql': 'select * where timestamp>' + str(begin_timestamp)})
    url = REQU_URL + "/chatmessages?" + time_query
    get_limit_messages_by_cursor(sink_msg_mongo(get(url)))
    # return get(url)


def get_limit_messages_by_cursor(cursor, limit=10):
    if cursor != "null":
        encode_param = urlencode({'limit': limit, 'cursor': cursor})
        url = REQU_URL + "/chatmessages?" + encode_param
        get_limit_messages_by_cursor(sink_msg_mongo(get(url)))
    else:
        print("聊天记录读取完毕")


def get_db_name_group_id(hxgroup_id):
    cursor = conn.cursor()
    sql = ("select groupname from commonGroup where hxgroupid = \'%s\'" % hxgroup_id)
    cursor.execute(sql)
    result = cursor.fetchone()
    if result is None:
        return hxgroup_id;
    return result[0]


def sink_msg_mongo(msg_response):
    if msg_response.has_key('cursor'):
        cursor = msg_response['cursor']
        entities = msg_response['entities']
        for entity in entities:
            msg_document = {}
            msg_document['send_name'] = get_db_name_by_hxid(entity['from'])
            msg_document['date'] = convent_timestamp_to_data_str(entity['created'])
            msg_document['chat_type'] = entity['chat_type']
            if msg_document['chat_type'] == 'chat':
                msg_document['to_name'] = entity['to'] if entity['to'] == 'fahaiservice' else get_db_name_by_hxid(
                    entity['to'])
            else:
                msg_document['to_name'] = entity['to'] if entity['to'] == 'fahaiservice' else get_db_name_group_id(
                    entity['to'])
            msg_document['type'] = entity['type']
            msg = entity['payload']['bodies'][0]
            msg_document['msg_type'] = msg['type']
            if msg_document['msg_type'] == 'txt':
                msg_document['msg'] = msg['msg']
            elif msg_document['msg_type'] == 'img':
                msg_document['url'] = msg['url']
                msg_document['filename'] = msg['filename']
                msg_document['secret'] = msg['secret']
            elif msg_document['msg_type'] == 'audio':
                msg_document['url'] = msg['url']
                msg_document['filename'] = msg['filename']
                msg_document['length'] = msg['length']
                msg_document['secret'] = msg['secret']
            elif msg_document['msg_type'] == 'loc':
                msg_document['addr'] = msg['addr']
                msg_document['lat'] = msg['lat']
                msg_document['lng'] = msg['lng']
            elif msg_document['msg_type'] == 'video':
                msg_document['url'] = msg['url']
                msg_document['filename'] = msg['filename']
                msg_document['length'] = msg['length']
                msg_document['file_length'] = msg['file_length']
                msg_document['secret'] = msg['secret']
            else:
                pass
            collection.insert_one(msg_document)
        return cursor
    else:
        return "null"


def convent_timestamp_to_data_str(timestamp):
    return datetime.datetime.utcfromtimestamp(int((str(timestamp))[:10])).strftime("%Y-%m-%d %H:%M:%S")


def convent_data_str_to_timestamp(data_str):
    return int(time.mktime(time.strptime("2015-07-27 07:43:43","%Y-%m-%d %H:%M:%S"))*1000)


def get_db_name_by_hxid(hx_id):
    cursor = conn.cursor()
    sql = ("select name from commonUserInfo where huanxinuser = \'%s\'" % hx_id)
    cursor.execute(sql)
    result = cursor.fetchone()
    if result is None:
        return hx_id;
    return result[0]


#获取上次读取最后一条记录的timestamp 误差一秒以内
def get_last_timestamp():
    if collection.count() == 0:
        return 0
    else:
        return convent_data_str_to_timestamp(collection.find({}).sort("date",pymongo.DESCENDING).limit(1)[0]["date"])+1000


if __name__ == '__main__':
    get_last_timestamp();

    output = sys.stdout
    output_file = open("check.log", "a+")
    sys.stdout = output_file
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    print(get_token()["access_token"])
    print("\n\n进行检查，日期为：" + time.strftime(ISOTIMEFORMAT, time.localtime()))
    JSON_HEADER['Authorization'] = 'Bearer ' + get_token()["access_token"]
    # 检查数据库群组和好友列表中已经删除的用户
    # JSON_HEADER = {'content-type': 'applocation/json',
#     #                 'Authorization': 'Bearer YWMtbvjegkMSEeWxeR3E2PPo2gAAAVBk7D5GNa48EgHQkVSwER6VFaHDvwK2qzQ'}
    timestamp = 1433301357123
    print(convent_timestamp_to_data_str(timestamp))
#     [8]['payload']['bodies'][0]['msg']
    all_hx_users = get_all_hx_users();
    all_hx_users_id = dirc_list_to_set(get_all_hx_users(), "username")
    all_hx_group_id = dirc_list_to_set(get_all_hx_group_id(), "groupid")
    print(all_hx_group_id)
    #      print(get_all_hx_group_id())
    #      print(all_hx_group_id)
    #      group_id = "93594992789946880";
    #      print(get_group_info(group_id))
    #      print(set(get_hx_user_frdlist("94f6a5fb90db360aa4f7bc83e86fa386")))
    all_db_users_id = truple_list_to_set(get_all_db_users_id())
    all_db_group_id = truple_list_to_set(get_all_db_hxgroup_id())
    print("检查用户以下在用户在数据库存在而在环信不存在 :")
    print(compare_set(all_db_users_id, all_hx_users_id)[0])
    print("以下用户在数环信存在而在数据库不存在  :")
    print(compare_set(all_db_users_id, all_hx_users_id)[1])
    print("\检查群组以下在群组在数据库存在而在环信不存在 :")
    print(compare_set(all_db_group_id, all_hx_group_id)[0])
    print("以下在群组在环信存在而在数据库不存在 :")
    print(compare_set(all_db_group_id, all_hx_group_id)[1])
    difference_in_group(compare_set(all_db_group_id, all_hx_group_id)[2])
    difference_in_frdlist(compare_set(all_db_users_id, all_hx_users_id)[2])
    check_extra_users_in_db()
    print("检查完毕，开始获取聊天纪录并存入数据库")
    get_chatmessages(get_last_timestamp())

    output_file.close()
    sys.stdout = output
# curl -X POST "https://a1.easemob.com/beijingfahaifuneng/baymax/token" -d '{"grant_type":"client_credentials","client_id":"YXA6kynz0MrhEeSS2Q2e11-3BA","client_secret":"YXA63Xe21wigqK4mgDB1Z0T70KGKNZ4"}'

# curl -X GET -H "Authorization: Bearer YWMtbvjegkMSEeWxeR3E2PPo2gAAAVBk7D5GNa48EgHQkVSwER6VFaHDvwK2qzQ" -i  "https://a1.easemob.com/beijingfahaifuneng/baymax/users?limit=20"

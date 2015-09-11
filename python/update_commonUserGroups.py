# coding: utf-8
import mysql.connector

conn = mysql.connector.connect(host='123.56.102.50', user='checkdata', password='123456', db='common',
                              port='9527')

# conn = mysql.connector.connect(host='wusong.xproj.net', user='common', password='0vCMeQIF4OpHzd6ld0', db='common',
#                                port='9527')

# 把用户对应的数组数据看成list集合  读取群组成员依次往里面加
def fetchall(sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def get_groupmembers_by_id(groupid):
    sql = ("select members from commonGroupMember where id = %d" % int(groupid))
    return fetchall(sql)


def get_all_groupids():
    return fetchall("select id from commonGroupMember")


def get_all_usersid():
    return fetchall("SELECT id FROM common.commonUser;")


def truple_list_to_set(list1):
    return set(map(lambda x: "".join(x if isinstance(x[0], str) else str(x[0])), list1))


def list_turple_list_to_set(list1):
    return list((list1[0][0][1:-1]).split(","))


def insert_into_commonUserGroups(userid,groupids):
    sql = ("insert into commonUserGroups set userid = %d , groupids = \'%s\' ON DUPLICATE KEY UPDATE userid= %s"%(int(userid),str(groupids),int(userid)))
    print(sql)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()


if __name__ == '__main__':
    dict_user = {}
    #1 遍历用户 分别创建容器（字典＋list）  2.遍历数组 分别插入对应容器
    for user_id in get_all_usersid():
        dict_user[user_id[0]] = []
    print(dict_user)
    for group_id in get_all_groupids():
        user_list = list_turple_list_to_set(get_groupmembers_by_id(group_id[0]))
        for user in user_list:
            if dict_user.has_key(int(user)):
                dict_user[int(user)].append(group_id[0])
    for (k,v)in dict_user.items():
        print k,":",v
        insert_into_commonUserGroups(k,v)

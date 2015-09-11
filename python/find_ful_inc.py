# coding=utf-8
__author__ = 'tangjia'

import os;

# date = datetime.datetime.strptime(date_str,'%Y%m%d')

INNOBACKUPEX = '/usr/bin/innobackupex'
MYSQL_START = '/etc/init.d/mysqld start'
MYSQL_STOP = '/etc/init.d/mysqld stop'
ful_dir_base = '/home/backup/ful'
inc_dir_base = '/home/backup/inc'
# mysql数据存储目录
mysql_data_dir = '/var/lib/mysql'
# mysql数据备份目录
mysql_data_dir_cp = '/var/lib/mysql_temp'

back_date = raw_input('enter a date like:2015-07-09_18-54-24-------:')

try:
    need_ful_date = filter(lambda x: x <= back_date, sorted(os.listdir(ful_dir_base)))[-1:][0]
    need_inc_dirs = filter(lambda x: need_ful_date <= x <= back_date, sorted((os.listdir(inc_dir_base))))
except  IndexError, e:
    print("你输入的日期前面没有全备份，无法还原")

print(need_ful_date)
print(need_inc_dirs)
os.environ['ful_dir_base'] = str(ful_dir_base);
os.environ['inc_dir_base'] = str(inc_dir_base);
os.environ['INNOBACKUPEX'] = str(INNOBACKUPEX);
# 备份全库备份  防止LSN更改
os.system('cp -R  ${ful_dir_base}/' + need_ful_date + '   ' + '${ful_dir_base}/' + need_ful_date + '_temp');
os.system(MYSQL_START);
os.system('${INNOBACKUPEX}  --apply-log  --redo-only  ${ful_dir_base}/' + need_ful_date);
for x in need_inc_dirs:
    inc_dir = inc_dir_base + '/' + x;
    #备份当前增量 防止LSN发生修改影响下次备份
    os.system('cp -R  '+inc_dir+'  '+inc_dir+'_temp');
    os.system(
        '${INNOBACKUPEX}  -apply-log  --redo-only  ${ful_dir_base}/' + need_ful_date + '   --incremental-dir=' + inc_dir);
    os.system('rm -rf  '+inc_dir);
    os.system('mv  '+inc_dir+'_temp    '+inc_dir);
# 备份数据库存储目录,防止恢复失败破坏数据文件
os.system('cp -R  ' + mysql_data_dir + '  ' + mysql_data_dir_cp);
# 删除数据库存储目录
os.system('rm  -rf  ' + mysql_data_dir);
os.system(MYSQL_STOP);
os.system('${INNOBACKUPEX}   --copy-back    ${ful_dir_base}/' + need_ful_date);
os.system('chown  -R  mysql:mysql   ' + mysql_data_dir);
os.system('rm  -rf  ${ful_dir_base}/' + need_ful_date);
os.system('mv  ${ful_dir_base}/' + need_ful_date + '_temp    ' + '${ful_dir_base}/' + need_ful_date);
os.system(MYSQL_START);

#! /bin/sh
#数据库还原脚本  
INNOBACKPEX=/usr/bin/innobackupex
MYSQL_START=/etc/init.d/mysqld start
MYSQL_STOP=/etc/init.d/mysqld stop
#数据库文件地址
data_dir=/data/mysql
weekday=`date '+%w'`
user='root'
password='root'
ful_backdir=/root/backup/ful
inc_backdir=/root/backup/inc
# 接受日期字符串参数如 "20150511"

read -p 'enter the recovery-date like 20150614 :' back_date
#将字符串转换为日期并计算是星期几,方便找出当周的主备份以及所有增量备份,并存入数组
echo $back_date
weekday=`date -d "${back_date}" "+%w"`
echo "${weekday}"
format_date=`date -d "${back_date}" "+%Y-%m-%d_%H-%M-%S"`
#找出本周的主备份以及本周当天之前的增量备份
#找出当周星期一的完整备份日期
if [[ ${weekday} = 0 ]]; then
	weekday=7 
fi
	count_temp=`expr ${weekday} - 1`
	echo $count_temp
 	#本次全库备份时间
 	ful_back_time=`date -d "${back_date} -${count_temp} days" "+%Y-%m-%d_%H-%M-%S"`
 	echo "${ful_back_time}"
	#全库备份目录
	ful_backdir_1=${ful_backdir}/${ful_back_time}
	echo "$ful_backdir_1"
	#备份全库副本
	cp -R ${ful_backdir_1} ${ful_backdir}/temp
	#准备
	${MYSQL_START}
	${INNOBACKPEX} --apply-log  --redo-only ${ful_backdir_1}
	echo "全备份目录是  ${ful_backdir_1}"
#如果是星期一 用全库备份去恢复 因为周一增量备份文件夹名字不确定
if [ ${weekday} != 1 ]; then
	while [ ${weekday}  -gt 1 ]; do 
		weekday=$[${weekday}-1]
		#增量文件名
		incremental_date_dir=`date -d "${back_date} -${weekday} days" "+%Y-%m-%d_%H-%M-%S"`
		echo "星期 ${weekday}+1 的目录是 $incremental_date_dir"
		#依次准备合并增量备份
		${INNOBACKPEX} --apply-log --redo-only ${ful_backdir_1} --incremental-dir=${inc_backdir}/${incremental_date_dir}
	done
fi
rm -rf ${data_dir}
${MYSQL_STOP}
#恢复数据
${INNOBACKPEX} --copy-back ${ful_backdir_1}
#改变数据库文件归属
chown -R  mysql:mysql ${data_dir}
#删除已经合并的主备份，将原来主备份的副本名字改回来方便下次备份
rm  -rf  ${ful_backdir_1}
mv  ${ful_backdir}/temp ${ful_backdir_1}

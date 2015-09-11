#!/bin/bash
INNOBACKPEX=/usr/bin/innobackupex
user='common'
password='13morTRhx4eUkdfBza'
ful_backdir=/home/backup/ful
inc_backdir=/home/backup/inc
#logfiledate=backup.`date +%Y%m%d%H%M`.txt  #备份日志

#检查最后一次全备份以及增量备份时间
last_fullback=`find /home/backup/ful  -mindepth 1 -maxdepth 1 -type d -printf "%P\n" | sort -nr | head -1`
last_incback=`find /home/backup/inc -mindepth 1 -maxdepth 1 -type d -printf "%P\n" | sort -nr | head -1`
echo 上一次全量备份:${last_fullback}


case "${1}" in
	ful)
		${INNOBACKPEX} --user=${user} --password=${password}  ${ful_backdir}
		#检查最后一次全备份时间
		last_fullback=`find /root/backup/ful  -mindepth 1 -maxdepth 1 -type d -printf "%P\n" | sort -nr | head -1`
		#新的一周在当周新的全库备份上增量备份
		${INNOBACKPEX} --incremental  ${inc_backdir}  --user=${user} --password=${password}  --incremental-basedir=/root/backup/ful/${last_fullback}
		;;
	inc)
		${INNOBACKPEX} --incremental  ${inc_backdir}  --user=${user} --password=${password}  --incremental-basedir=/root/backup/inc/${last_incback}
		;;
	*)
		echo "basename ${0}:usage: [ful]  or [inc]"
		;;
esac
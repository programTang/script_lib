#coding=utf-8
import  random
import os
__author__ = 'tangjia'

import  os

baseDir = "/Users/tangjia/Desktop/test/"

def createRandomDir( x ,type ):
    for x in range(1,x):
        # full backup
        year = 2015
        month = random.randint(6,7)
        day = random.randint(1,30)
        if day < 10:
            day = "0"+str(day)
        hour = random.randint(0,23)
        if hour < 10:
            hour = "0"+str(hour)
        minute = random.randint(1,60)
        if minute < 10:
            minute = "0"+str(minute)
        second = random.randint(1,60)
        if second < 10:
            second = "0"+str(second)
        dir_name = str(year)+"-0"+str(month)+"-"+str(day)+"_"+str(hour)+"-"+str(minute)+"-"+str(second)
        global baseDir
        os.mkdir(baseDir+type+"/"+dir_name)

#createRandomDir(6,"ful");
createRandomDir(90,"inc");
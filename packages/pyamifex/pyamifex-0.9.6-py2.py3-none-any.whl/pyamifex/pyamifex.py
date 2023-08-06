#-*- encoding=utf-8 -*-
#!/usr/bin/env python
#Author:QiQi
import sys
import glob
import os
from  datetime import  datetime
from logging.handlers import RotatingFileHandler
import logging
if sys.version_info>=(3,0):
   import configparser
else:
   import ConfigParser
from shutil import copyfile
if sys.version_info>=(3,3):
    from .configkey import configKey
    from  .pyamifexlite import  Pyamifexlite
else:
    from configkey import configKey
    from pyamifexlite import  Pyamifexlite

class  Pyamifex:
     def __init__(self,configFileName):
         modulePath = os.path.dirname(os.path.abspath(__file__))
         self.errMsg=""
         self.ifJobId=None
         self.pjId=None
         self.storeId=None
         self.configFileName=configFileName
         if not os.path.exists(self.configFileName):
              raise Exception("config file:{0} not found! ".format(self.configFileName))

     #==  read  all  config
     def readConfig(self):
         logging.info("read config")
         if sys.version_info>=(3,0):
             cf = configparser.RawConfigParser()
         else:
             cf = ConfigParser.RawConfigParser()
         self.cf=cf
         cf.optionxform = str
         cf.read(self.configFileName)
         for section in  cf.sections():
             config = {}
             if  cf.has_option(section,configKey.active ) and  cf.get(section,configKey.active).lower()!="true":
                 logging.info("section={0} not active ,pass".format(section))
                 continue
             config[configKey.section]=section
             if(self.checkKeyExist(section)==False):
                 continue
             #==
             #==== set key  to  config
             keyProps = configKey.getProps()
             for  key in  keyProps:
                 if key.lower()=="pjid":
                     isDebug=True
                 if  key.lower()=="pjid" and self.pjId!=None:
                       config[key]=str(self.pjId)
                 elif key.lower()=="storeid" and self.storeId!=None:
                       config[key] = str(self.storeId)
                 else:
                     if  cf.has_option(section,key):
                         config[key]=cf.get(section,key)
                     else:
                         not_find=key
             self.configList.append(config)   # add  config to  config list

     # reset self.ifJobId
     def  run(self):
         self.configList=[]
         self.readConfig()
         self.processLine=0
         for  config  in  self.configList:
             pyamifexlite = Pyamifexlite(config)
             pyamifexlite.run()
             if  pyamifexlite.errMsg!="":
                 self.errMsg=self.errMsg+""
             else:
                 self.processLine+=pyamifexlite.processLine
             self.ifJobId=pyamifexlite.ifJobId

     # 似乎是这样,检查这个配置是否是重复的,如果这个配置重复就不做了,Add remark by QiQi on 2018/06/04
     def checkKeyExist(self,section):
          noCheckKeys={}
          #==
          noCheckKeys[configKey.section]=1    # this
          noCheckKeys[configKey.active]=1
          noCheckKeys[configKey.callSp] = 1
          # ==
          checkProps=configKey.getProps()
          for  key in  checkProps:
             if  key in noCheckKeys:   # no check
                 continue
             if self.cf.has_option(section, key== False):
                 logging.warning("section={0}, key={1} not exist, pass this section!".format(section,key))
                 return  False
          return  True

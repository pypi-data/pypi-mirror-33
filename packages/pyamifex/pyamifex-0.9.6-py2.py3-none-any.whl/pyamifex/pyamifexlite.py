#-*- encoding=utf-8 -*-
#!/usr/bin/env python
#Author:QiQi
import sys
import glob
import zipfile
import traceback
import os
import uuid
from  datetime import  datetime
import logging
import xlrd
import amiconn
from shutil import copyfile
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
import shutil
import csv
from pydoc import locate
# == this self
if sys.version_info>=(3,3):
    from .ifheadmod import  IfHeadMod
    from .iflinemod import  IfLineMod
    from .ifjobmod  import  IfJobMod
    from .configkey import  configKey
    from .reconfilemod import ReconFileMod
else:
    from ifheadmod import  IfHeadMod
    from iflinemod import  IfLineMod
    from ifjobmod  import  IfJobMod
    from configkey import  configKey
    from reconfilemod import ReconFileMod


class Pyamifexlite():
     def __init__(self,config,reconfilemod=None):
         self.errMsg=""
         self.config=config
         self.fileZipOrign={}
         self.zipDir={}
         self.reconfilemod=reconfilemod
         self.processLine=0

     def _preCheck(self):
         if os.path.exists(self.config[configKey.dir]) == False:
             logging.error("dir not exist"+self.config[configKey.dir])
             logging.error("section={0} dir={1} not exist".format(self.config[configKey.section], self.config[configKey.dir]))
             return False
         if os.path.exists(self.config[configKey.bakDir]) == False:
             logging.error("section={0} bakdir={1} not exist".format(self.config[configKey.section], self.config[configKey.bakDir]))
             return False
         return  True

     def getFiles(self):
         localPath=self.config[configKey.dir]
         pattern=self.config[configKey.filePattern]
         list = glob.glob(os.path.join(localPath, pattern))
         list.sort(key=os.path.getmtime)
         return  list

     def initConn(self):
         odbcClientVer=self.config[configKey.connOdbcVer]
         connString=amiconn.GetMsSqlConnStringByConnName(self.config[configKey.connName],odbcClientVer)
         engine = create_engine(connString)
         dbSession = sessionmaker(bind=engine)
         self.session = dbSession()

     def writeIfJob(self):
         ifJobMod=IfJobMod()
         ifJobMod.IfJobId=str(uuid.uuid4())
         self.ifJobId=ifJobMod.IfJobId
         ifJobMod.pjId=self.config[configKey.pjId]
         ifJobMod.storeId=self.config[configKey.storeId]
         ifJobMod.status=0
         if self.reconfilemod!=None:    #
             ifJobMod.refIfId=self.reconfilemod.reconFileId
         self.session.add(ifJobMod)

     # ========================================
     # ==  writeIfHead
     # ========================================
     def writeIfHead(self,origFrom,fileName,dir):
         ifHeadMod=IfHeadMod()
         ifHeadMod.IfHeadId=str(uuid.uuid4())
         ifHeadMod.pjId=self.config[configKey.pjId]
         ifHeadMod.storeId=self.config[configKey.storeId]
         ifHeadMod.origFrom=origFrom
         ifHeadMod.ifJobId=self.ifJobId
         # dont' write fileType
         #ifHeadMod.fileType=self.config[configKey.fileType]
         if  self.reconfilemod!=None:
             ifHeadMod.fileType=self.reconfilemod.fileType
             ifHeadMod.dateBegin=self.reconfilemod.dateBegin
             ifHeadMod.dateEnd=self.reconfilemod.dateEnd
         ifHeadMod.fileName=fileName
         ifHeadMod.dir=dir
         ifHeadMod.operateUserId=0
         ifHeadMod.status=0
         self.session.add(ifHeadMod)
         return  ifHeadMod

     #=================================================
     def  writeIfLine(self,ifHeadId,lineNo,cols):
         #==  line no check
         if lineNo<int(self.config[configKey.startRow]):
              return
         ifLineMod=IfLineMod()
         ifLineMod.ifLineId=str(uuid.uuid1())   # 以前没有设置这个,但是为何以前没有错? is  chage to  uuid1
         ifLineMod.ifHeadId=ifHeadId
         ifLineMod.lineNo=lineNo
         i=1
         for  col  in  cols:
             fieldName="col"+str(i).zfill(3)
             setattr(ifLineMod,fieldName,col)
             i=i+1
         self.processLine+=1
         self.session.add(ifLineMod)

      #==================================
      #  getOrigFrom ,Modi by QiQi on 2017/10/10, 2017/10/16
      # ==================================
     def getOrigFrom(self,fullFileName):
         if  fullFileName in self.fileZipOrign:
             origFrom=self.fileZipOrign[fullFileName]
         else:
             origFrom=""
         sysDir=self.config[configKey.dir]
         l1=len(sysDir)
         origs=origFrom.split(",")
         newOrigFrom=""
         for origFrom in  origs:
            if len(newOrigFrom)>0:
                newOrigFrom=newOrigFrom+","
            if  len(origFrom)>l1:
               newOrigFrom=newOrigFrom+origFrom[l1+1:]
         if  self.reconfilemod!=None:   # this  patch
             newOrigFrom=self.reconfilemod.origFrom+","+newOrigFrom
         if len(newOrigFrom)>0 and newOrigFrom[-1]==",":
             newOrigFrom=newOrigFrom[:-1]
         return  newOrigFrom

     def getExcelDate2Str(self,xlsBook,val):
          year, month, day, hour, minute, second = xlrd.xldate_as_tuple(val.value,xlsBook.datemode)
          pyDate = datetime(year, month, day, hour, minute, second)
          strDate=pyDate.strftime("%Y-%m-%d %H:%M:%S")
          return  strDate

     # ====================================================
     # = processWithXls   modi by QiQi on 2017/10/20
     # ====================================================
     def  processWithXls(self,fullFileName,fileName,dir):
         origFileName = self.getOrigFrom(fullFileName)
         startRow = int(self.config[configKey.startRow])
         xlsBook = xlrd.open_workbook(fullFileName)
         for  xlsSheet  in   xlsBook.sheets():
             #== write Head
             ifHeadMod = self.writeIfHead(origFileName, fileName, dir)
             ifHeadMod.sheetName=xlsSheet.name
             #==
             for  row  in   range(0,xlsSheet.nrows):
                  cols=[]
                  for  col  in  range(0,xlsSheet.ncols):
                       cellObj=xlsSheet.cell(row, col)
                       if  col==3:
                           isDebug=True
                       if  cellObj.ctype==xlrd.XL_CELL_DATE:   #if  is datetime
                          strValue=self.getExcelDate2Str(xlsBook,cellObj)
                       elif  cellObj.ctype==xlrd.XL_CELL_NUMBER:   #if  is  number
                           strValue =str(cellObj.value)
                       else:
                          strValue = cellObj.value
                       cols.append(strValue)
                  self.writeIfLine(ifHeadMod.IfHeadId, row+1, cols)

     #====================================================
     #= processWithCsv
     # ====================================================
     def processWithCsv(self,fullFileName,fileName,dir):
        origFileName=self.getOrigFrom(fullFileName)
        startRow=int(self.config[configKey.startRow])
        ifHeadMod=self.writeIfHead(origFileName,fileName,dir)
        lineNo=1
        encoding=self.config[configKey.encoding]
        with open(fullFileName , 'rb') as csvfile:
            spamreader = csv.reader(csvfile,delimiter=self.config[configKey.delimiter],quotechar=self.config[configKey.quote])
            for rows in spamreader:
                  cols=[]
                  colNo=0
                  for col in rows:
                      colNo=colNo+1
                      isUnicode=None
                      if  isinstance(col,unicode):
                         s1=col.decode("utf-8")
                         isUnicode=True
                      else:
                         s1=col
                         isUnicode = False
                      cols.append(s1)     # decode  by  config encoding  !!!
                  self.writeIfLine(ifHeadMod.IfHeadId,lineNo,cols)
                  lineNo=lineNo+1

     #============================
     #== removeReplaceFile
     #============================
     def removeReplaceFile(self,dir,compressList):
         for  fileName in compressList:
             fullFileName=os.path.join(dir,fileName)
             if  os.path.exists(fullFileName):
                 os.remove(fullFileName)

     def getRelateFileName(self,fullFileName):
         sysRootDir = self.config[configKey.dir]
         if  sysRootDir[-1]!="\\":
             sysRootDir=sysRootDir+"\\"
         len1=len(sysRootDir)
         relateFileName=fullFileName[len1:]
         return relateFileName

     #============================
     #==  unzipFile, (recursion)
     # ============================
     def  getUnZipFiles(self,files):
        fileList=[]
        sysRootDir = self.config[configKey.dir]
        for  fullFileName in files:
           logging.debug("getUnzipFiles(),fileName="+fullFileName)
           dir,fileName=os.path.split(fullFileName)
           fileNameNoExt,ext=os.path.splitext(fileName)
           if  ext.lower()==".zip":
               zipFileName=fileName
               haveZipFile=True
               zf = zipfile.ZipFile(fullFileName,'r')
               compressList=zf.namelist()
               #self.removeReplaceFile(dir,compressList)
               zf.extractall(dir)
               zf.close()
               for  compileFileName in compressList:
                   newFileName=os.path.join(dir,compileFileName)
                   _,compileFileExt=os.path.splitext(compileFileName)
                   if  compileFileExt=="":  #maybe is directory
                       self.zipDir[compileFileName]=compileFileName            #
                       continue
                   elif compileFileExt.lower()==".zip":                     #recursion
                       compileFullFileName = os.path.join(sysRootDir, compileFileName)
                       #--
                       if newFileName in self.fileZipOrign:
                           self.fileZipOrign[compileFullFileName]=self.fileZipOrign[newFileName]+","+fullFileName
                       else:
                           self.fileZipOrign[compileFullFileName] = fullFileName
                       #--
                       extendFileList=self.getUnZipFiles([newFileName])    #must be  list
                       fileList.extend(extendFileList)
                   else:
                      if  fullFileName in  self.fileZipOrign:               # find  orig fileName
                          origFileName=self.fileZipOrign[fullFileName]+","+fullFileName
                      else:
                          origFileName=fullFileName
                      self.fileZipOrign[newFileName]=origFileName
                      fileList.append(newFileName)
           else:
               fileList.append(fullFileName)
        return  fileList
     # =====================================================
     #  Modi by QiQi on 2017/10/17
     # =====================================================
     def  removeOrBackupZip(self,fileName):
         logging.debug("removeOrBackupZip() fileName="+fileName)
         zipFiles = self.fileZipOrign[fileName].split(",")
         if len(zipFiles)==0:
             logging.warning("fileName={0} find  zip file not found".format(fileName))
             return
         j=0
         fileName=""
         for zipFullFileName in zipFiles:
             t1=datetime.now()
             _,zipFileName=os.path.split(zipFullFileName)
             if os.path.exists(zipFullFileName):  # move  zip  to  bak dir
                 zipFileNameNoExt, _ = os.path.splitext(zipFileName)
                 newFileName = zipFileNameNoExt + "__" + t1.strftime("%y%m%d_%H%M%S") + ".zip"
                 bakFileName = os.path.join(self.config[configKey.bakDir], newFileName)
                 if  os.path.exists(zipFullFileName):
                    fileName=zipFileName
                    if  j==0:          # only remove  root  zip
                        shutil.move(zipFullFileName, bakFileName)
                        logging.debug("move from {0} to {1}".format(zipFullFileName,bakFileName))
                    else:
                        logging.debug("remove file {0}".format(zipFullFileName))
                        os.remove(zipFullFileName)
             j=j+1

     def  removeDir(self):
         for  subDir in self.zipDir:
             fullDir=os.path.join(self.config[configKey.dir],subDir)
             os.rmdir(fullDir)

     def getFileNameMsg(self):
         if configKey.section in self.config:
             strDisp = self.config[configKey.section]
         else:
             strDisp = ""
         strDisp="["+strDisp+"]"
         strMsg = strDisp +"   " + os.path.join(self.config[configKey.dir], self.config[configKey.filePattern])
         return  strMsg


     def _removeFile(self,fullFileName,fileName):
         fileNameNoExt, fileExt = os.path.splitext(fileName)
         # if fileNameNoExt=="153478200-2017-07-31":
         #     isDebug=True
         t1 = datetime.now()
         if fullFileName in self.fileZipOrign:  # If file is unzip
             os.remove(fullFileName)  # remove csv at  first !!
             self.removeOrBackupZip(fullFileName)
         else:
             newFileName = fileNameNoExt + "__" + t1.strftime("%y%m%d_%H%M%S") + fileExt
             bakFileName = os.path.join(self.config[configKey.bakDir], newFileName)
             shutil.move(fullFileName, bakFileName)

     #  Add
     def callExtMudule(self):
         s1=self.config
         try:
             findCallMode=configKey.callmodule in self.config
             if  not findCallMode:
                 logging.info("not set callmodule")
                 return
             moduleName=self.config[configKey.callmodule]
             if  moduleName=="":  # if no callmodule
                 return
             modulePath, moduleFile = os.path.split(moduleName)
             if not  os.path.exists(modulePath):
                 self.errMsg="module path {0} not exist".format(modulePath)
                 logging.error(self.errMsg)
                 return
             className=moduleFile+"."+self.config[configKey.callclass]
             methodName = self.config[configKey.callmethod ]
             # ==
             sys.path.insert(0, modulePath)
             __import__(moduleFile)
             runClass = locate(className)
             if runClass==None:
                 logging.error("callExtModule  class ={0} is null".format(className))
                 return
             runObj=runClass()
             # ===
             runObj.ifJobId=self.ifJobId
             #run_class.ifJobId=   #  set job_id
             getattr(runObj, methodName)()  # call  method name
         except  Exception as e:
            self.errMsg="callExtModule error= {0}".format(e)
            logging.error(self.errMsg)

     #  run
     def run(self):
        if self._preCheck()==False:
            return
        files=self.getFiles()
        if  len(files)==0:     #  if no  file  then   return
            logging.info("no file: {0} to process ".format(self.getFileNameMsg()))
            return
        # if  have zip  file ,unzip to files by . files is list  only csv or xls,xlsx  file ,no zip file
        startTime = datetime.now()
        logging.info("ready unzip file, startTime={0}".format(startTime.strftime("%H:%M:%S")))
        files=self.getUnZipFiles(files)
        logging.info("total get files={0}".format(len(files)))
        self.initConn()
        self.writeIfJob()
        j=1
        for fullFileName in files:
            try:
                logging.info("process file:{0},index={1}".format(fullFileName,j))
                origFileDir,_=os.path.split(fullFileName)
                if  os.path.exists(fullFileName)==False:
                    logging.warning("file:{0} not found maybe is compressed many times".format(fullFileName))
                    continue
                fileSize = os.path.getsize(fullFileName)
                if fileSize == 0:
                    logging.info("fileName:{0} file length size is 0 ,pass ".format(fullFileName))
                    continue
                dir,fileName = os.path.split(fullFileName)
                _,fileExt=os.path.splitext(fileName)
                if fileExt.lower()==".csv" or fileExt.lower()==".txt":
                     self.processWithCsv(fullFileName,fileName,dir)
                elif fileExt.lower()==".xls" or fileExt.lower()==".xlsx":
                     self.processWithXls(fullFileName,fileName,dir)
                else:
                    logging.error("fileType={0} not support".format(self.config[configKey.fileType]))
                    continue
                self.session.commit()
                self._removeFile(fullFileName,fileName)
                j=j+1
            except (KeyboardInterrupt, SystemExit):
                self.session.rollback()
                logging.warning("user terminal")
                return
            except Exception as e:
                self.errMsg=e
                logging.error(e)
                #logging.error(e.message)
                logging.error("section="+self.config[configKey.section]+"error:"+traceback.format_exc())
                self.session.rollback()
        self.session.close()
        #==
        self.callExtMudule()   #  add  this by QiQi on  2018/06/05
        #===
        endTime = datetime.now()
        logging.info("endtime={0}".format(endTime.strftime("%H:%M:%S")))
        total_seconds=(endTime-startTime).total_seconds()
        logging.info("section={0} process over total seconds={1}".format(self.getFileNameMsg(),total_seconds))
        self.removeDir()
        #==== run end  !!

if  __name__=="__main__":
    print ("good morning")

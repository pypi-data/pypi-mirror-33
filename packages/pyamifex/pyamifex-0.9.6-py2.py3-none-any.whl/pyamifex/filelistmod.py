#-*- encoding=utf-8 -*-
import  datetime
import sys
import uuid
import redis
import  sqlalchemy
import amiconn
import  binascii
from  datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship


#reload(sys)
#sys.setdefaultencoding('gbk')

Base = declarative_base()

class FileListMod(Base):
    __tablename__ ="file_list"
    fileListId=Column("File_list_id",BigInteger,primary_key=True,autoincrement=True)
    jobId=Column("Job_id",String)
    pjId = Column("Pj_id", BigInteger)
    stoteId = Column("Store_id", BigInteger)
    fileName = Column("File_name", String)
    fileType =Column("File_type",String)
    operateTime=Column("Operate_time",DateTime)
    dateBegin=Column("Date_begin",DateTime)
    dateEnd = Column("Date_end", DateTime)
    operateUserId=Column("Operate_user_id",Integer)

def getSession():
   engine = create_engine('mssql+pyodbc://sw:Basicnote2015@10.10.10.31/g2cn')
   dbSession = sessionmaker(bind=engine)
   session = dbSession()
   return session

def testInsert():
    session=getSession()




if  __name__=="__main__":



#-*- encoding=utf-8 -*-
#Author:QiQi
from datetime import datetime
import sys
import uuid
import  sqlalchemy
import amiconn
import  binascii
import  amiconn
from  datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

#reload(sys)
#sys.setdefaultencoding('gbk')

Base = declarative_base()

class IfJobMod(Base):
    __tablename__ ="If_job"
    IfJobId=Column("If_job_id",String(36),primary_key=True)
    pjId = Column("Pj_id", BigInteger)
    storeId = Column("Store_id", BigInteger)
    createTime=Column("Create_time",DateTime,default=func.getdate())
    operateTime=Column("Operate_time",DateTime,default=func.getdate())
    idIndex= Column("Id_index", Integer, autoincrement=True,primary_key=True)
    refIfId=Column("Ref_if_id", String)  #  ref_if_id
    status=Column("Status",Integer,default=0)

def getSession():
    connString=amiconn.GetMsSqlConnStringByConnName("invoice",11)
    engine = create_engine(connString)
    dbSession = sessionmaker(bind=engine)
    session = dbSession()
    return session


def testInsert():
    session = getSession()
    ifJobMod=IfJobMod()
    ifJobMod.IfJobId=str(uuid.uuid4())
    ifJobMod.pjId=19
    ifJobMod.storeId=20
    session.add(ifJobMod)
    session.commit()

if __name__=="__main__":
    testInsert()



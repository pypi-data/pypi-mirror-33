#-*- encoding=utf-8 -*-
from datetime import datetime
import sys
import uuid
import  sqlalchemy
import amiconn
import  binascii
import  amiconn
from  datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship


#reload(sys)
#sys.setdefaultencoding('gbk')

Base = declarative_base()

class ReconFileMod(Base):
    __tablename__ ="Recon_file"
    reconFileId=Column("Recon_file_id",String(36),primary_key=True)
    pjId = Column("Pj_id", BigInteger)
    storeId = Column("Store_id", BigInteger)
    origFrom=Column("Orig_from",String)
    fileName=Column("File_name",String)
    fileType=Column("File_type",String)
    dateBegin=Column("Date_begin",DateTime)
    dateEnd = Column("Date_end", DateTime)
    status=Column("Status",Integer)
    createTime=Column("Create_time",DateTime,default=func.getdate())
    operateTime=Column("Operate_time",DateTime,default=func.getdate())
    operateUserId=Column("Operate_user_id",Integer)
    idIndex= Column("Id_index", Integer, autoincrement=True,primary_key=True)


if __name__=="__main__":
    connString=amiconn.GetMsSqlConnStringByConnName("invoice",11)
    engine=create_engine(connString)
    dbSession=sessionmaker(engine)
    session=dbSession()
    reconFile=ReconFileMod()
    key1=str(uuid.uuid4())
    reconFile.reconFileId=key1
    reconFile.pjId=123
    reconFile.storeId=332
    reconFile.origFrom="orig.txt"
    reconFile.fileName="f1.txt"
    reconFile.fileType="unknown"
    reconFile.status=0
    reconFile.dateBegin=datetime.now()-timedelta(5)
    reconFile.dateEnd=datetime.now()-timedelta(1)
    reconFile.operateUserId=0
    session.add(reconFile)
    try:
      session.commit()
    except Exception as e:
      msg=e.message.encode()
      logging.error(e.message)
    session.close()










#-*- encoding=utf-8 -*-
#Author:QiQi
import  datetime
import  uuid
import sys
import uuid
import amiconn
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

class IfLineMod(Base):
    __tablename__ ="If_line"
    ifLineId = Column("If_line_id", String(36), primary_key=True)
    ifHeadId=Column("If_head_id",String(36))
    idIndex = Column("Id_index", Integer, autoincrement=True, primary_key=True)
    createTime= Column("Create_time", DateTime,default=func.getdate())
    lineNo=Column("line_no",Integer,default=0)
    col001=Column("Col001", String,default="")
    col002=Column("Col002", String,default="")
    col003=Column("Col003", String,default="")
    col004=Column("Col004", String,default="")
    col005=Column("Col005", String,default="")
    col006=Column("Col006", String,default="")
    col007=Column("Col007", String,default="")
    col008=Column("Col008", String,default="")
    col009=Column("Col009", String,default="")
    col010=Column("Col010", String,default="")
    col011=Column("Col011", String,default="")
    col012=Column("Col012", String,default="")
    col013=Column("Col013", String,default="")
    col014=Column("Col014", String,default="")
    col015=Column("Col015", String,default="")
    col016=Column("Col016", String,default="")
    col017=Column("Col017", String,default="")
    col018=Column("Col018", String,default="")
    col019=Column("Col019", String,default="")
    col020=Column("Col020", String,default="")
    col021=Column("Col021", String,default="")
    col022=Column("Col022", String,default="")
    col023=Column("Col023", String,default="")
    col024=Column("Col024", String,default="")
    col025=Column("Col025", String,default="")
    col026=Column("Col026", String,default="")
    col027=Column("Col027", String,default="")
    col028=Column("Col028", String,default="")
    col029=Column("Col029", String,default="")
    col030=Column("Col030", String,default="")
    col031=Column("Col031", String,default="")
    col032=Column("Col032", String,default="")
    col033=Column("Col033", String,default="")
    col034=Column("Col034", String,default="")
    col035=Column("Col035", String,default="")
    col036=Column("Col036", String,default="")
    col037=Column("Col037", String,default="")
    col038=Column("Col038", String,default="")
    col039=Column("Col039", String,default="")
    col040=Column("Col040", String,default="")
    col041=Column("Col041", String,default="")
    col042=Column("Col042", String,default="")
    col043=Column("Col043", String,default="")
    col044=Column("Col044", String,default="")
    col045=Column("Col045", String,default="")
    col046=Column("Col046", String,default="")
    col047=Column("Col047", String,default="")
    col048=Column("Col048", String,default="")
    col049=Column("Col049", String,default="")
    col050=Column("Col050", String,default="")
    col051=Column("Col051", String,default="")
    col052=Column("Col052", String,default="")
    col053=Column("Col053", String,default="")
    col054=Column("Col054", String,default="")
    col055=Column("Col055", String,default="")
    col056=Column("Col056", String,default="")
    col057=Column("Col057", String,default="")
    col058=Column("Col058", String,default="")
    col059=Column("Col059", String,default="")
    col060=Column("Col060", String,default="")
    col061=Column("Col061", String,default="")
    col062=Column("Col062", String,default="")
    col063=Column("Col063", String,default="")
    col064=Column("Col064", String,default="")
    col065=Column("Col065", String,default="")
    col066=Column("Col066", String,default="")
    col067=Column("Col067", String,default="")
    col068=Column("Col068", String,default="")
    col069=Column("Col069", String,default="")
    col070=Column("Col070", String,default="")
    col071=Column("Col071", String,default="")
    col072=Column("Col072", String,default="")
    col073=Column("Col073", String,default="")
    col074=Column("Col074", String,default="")
    col075=Column("Col075", String,default="")
    col076=Column("Col076", String,default="")
    col077=Column("Col077", String,default="")
    col078=Column("Col078", String,default="")
    col079=Column("Col079", String,default="")
    col080=Column("Col080", String,default="")




def getSession():
    connString=amiconn.GetMsSqlConnStringByConnName("invoice",11)
    #print  connString
    engine = create_engine(connString, echo=False)
    dbSession = sessionmaker(bind=engine)
    session = dbSession()
    return session

def testInsert():
    session=getSession()
    ifLineMod=IfLineMod()
    ifLineMod.ifHeadId=str(uuid.uuid4())
    ifLineMod.ifLineId=str(uuid.uuid4())
    ifLineMod.col001=  "zzaa"
    ifLineMod.col002 = "b"
    ifLineMod.col003 = "c"
    ifLineMod.col004 = "d"
    ifLineMod.col005 = "e"
    ifLineMod.col006 = "f"
    ifLineMod.col007 = "g"
    ifLineMod.col008 = "h"
    ifLineMod.col009 = "i"
    ifLineMod.col010 = "j"
    session.add(ifLineMod)
    session.commit()
    session.close()

if  __name__=="__main__":
     testInsert()

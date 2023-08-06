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

class FileDataMod(Base):
    __tablename__ ="file_data"


#-*- encoding=utf-8 -*-

class configKey:
    section="section"
    startRow="startRow"
    fileType="fileType"
    active="active"
    connName="connName"
    connOdbcVer="connOdbcVer"
    dir="dir"
    filePattern="filePattern"
    bakDir="bakDir"
    callSp="callSp"
    pjId="pjId"
    storeId="storeId"
    delimiter="delimiter"
    quote="quote"
    encoding="encoding"
    callmodule="callmodule"
    callclass="callclass"
    callmethod="callmethod"

    @staticmethod
    def getProps():
        return [i for i in configKey.__dict__.keys() if i[:1] != '_']    # 系统的一些 属性可能是下划线开头的

if  __name__=="__main__":
     v1=configKey.getProps()
     print (v1)

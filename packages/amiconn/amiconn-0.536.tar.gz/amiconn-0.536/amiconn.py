# -*- encoding=utf-8 -*-…
# Create by QiQi on 2017/07/10
import  os
import  sys
import base64
from sqlalchemy import *
import urllib
if (sys.version_info > (3, 0)):
   import winreg
else:
   import _winreg

# create by QiQi on  2017-10-06
def create_db_engine(dbuser, dbpassword, dbhost, database, dbport, clientver=None, dbconntype="class"):
    if dbconntype.lower() == "class":
        if dbport == None or dbport.lower() == "none" or dbport == "":
            connString = "mssql+pyodbc://{0}:{1}@{2}/{3}".format(dbuser, dbpassword, dbhost, database)
        else:
            connString = "mssql+pyodbc://{0}:{1}@{2},{3}/{4}".format(dbuser, dbpassword, dbhost, dbport, database)
        if clientver != None:
            if len(clientver)<3:
              connString = connString + "?driver=SQL+Server+Native+Client+{0}.0".format(clientver)
            else:
              connString = connString + "?driver={0}".format(clientver)
        return create_engine(connString)
    elif dbconntype.lower() == "freetds":
        odbcConn = "DRIVER={FreeTDS};" + "Server={0};Database={1};UID={2};PWD={3};TDS_Version=8.0;Port={4}".format(
            dbhost, database, dbuser, dbpassword, dbport)
        quoted = urllib.quote_plus(odbcConn)
        return create_engine('mssql+pyodbc:///?odbc_connect={0}'.format(quoted))


def _GetAmiRegValue(connName,keyName):
   if (sys.version_info > (3, 0)):
      aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
   else:
      aReg = _winreg.ConnectRegistry(None,_winreg.HKEY_LOCAL_MACHINE)

   regStr=r"SOFTWARE\\AmiSoft\\Connection\\"+connName
   if (sys.version_info > (3, 0)):
      aKey = winreg.OpenKey(aReg, regStr, 0, (winreg.KEY_WOW64_64KEY | winreg.KEY_READ))
      strVal = winreg.QueryValueEx(aKey, keyName)
      winreg.CloseKey(aKey)
   else:
      aKey = _winreg.OpenKey(aReg, regStr,0,(_winreg.KEY_WOW64_64KEY | _winreg.KEY_READ))
      strVal=_winreg.QueryValueEx(aKey, keyName)
      _winreg.CloseKey(aKey)
   str=strVal[0]
   if  keyName.lower()=="connstring" and str.lower().find("password")==-1:
       str=base64.decodestring(str)
   return str

def GetConnStrVal(connStr,key):
    list=connStr.split(";")
    for str in list:
        str=str.replace(" ","")
        list11=str.split("=")
        if len(list11)>=2 and  list11[0].strip().lower()==key.lower():
            val=list11[1].strip()
            return  val
    return ""


def GetMsSqlConnString(userId, password, serverName, dbName):
    pyConnString = "mssql+pyodbc://%s:%s@%s/%s" % (userId, password, serverName, dbName)
    return pyConnString

# **  cleintBersion is require by   clinet driver  like  driver=SQL+Server+Native+Client+11.0 ,if none then don't add
def GetMsSqlConnStringByConnName(connName,clientDriverVersion=None):
    connString=_GetAmiRegValue(connName,"connstring")
    if len(connString)>0:
        password=GetConnStrVal(connString,"password")
        userId=GetConnStrVal(connString,"UserID")
        serverName=GetConnStrVal(connString,"DataSource")  #Initial Catalog
        dbName=GetConnStrVal(connString,"InitialCatalog")  #InitialCatalog
        if password=="":
            raise Exception("amiTools.GetMsSqlConnString() password not found form string" )   # must in
        if userId=="":
            userId=GetConnStrVal(connString,"User")    # add USer
            if userId=="":
               raise Exception("amiTools.GetMsSqlConnString() user Id not found form string" )   # must in
        if serverName=="":
            serverName=GetConnStrVal(connString,"server")  #Initial Catalog
            if serverName=="":
               raise Exception("amiTools.GetMsSqlConnString() Data Source not found form string" )   # must in
        if dbName=="":
            dbName=GetConnStrVal(connString,"database")  #InitialCatalog
            if dbName=="":
               raise Exception("amiTools.GetMsSqlConnString() Initial Catalog not found form string" )   # must in
        #pyConnString="mssql+pyodbc://%s:%s@%s/%s" % (userId,password,serverName,dbName)
        pyConnString=GetMsSqlConnString(userId,password,serverName,dbName)
        if len(pyConnString)>0:
            if  clientDriverVersion==None or clientDriverVersion=="0" or clientDriverVersion==0:
                pyConnString = pyConnString + "?driver=SQL+Server"
            else:
                pyConnString=pyConnString+"?driver=SQL+Server+Native+Client+{0}.0".format(clientDriverVersion)
        return  pyConnString
    return  ""

def main():
    #str1=GetMsSqlConnStringByConnName("300",11)
    #print  str1
    create_db_engine("sw","Basicnote2015", "10.10.10.31", "buffer", "1433", "11","class")

if  __name__=="__main__":
    main()



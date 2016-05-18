import sys
sys.path.insert(0, '.')
from ASPaths.ASPath import ASPath
from DBAccess.mysqlConnector import mysqlConnector

mysql=mysqlConnector(dbname='bgp_archive') 
messages=mysql.getMessages('updates','2015','11','06','195_208_112_161')
print(messages)
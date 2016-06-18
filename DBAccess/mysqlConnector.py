import pymysql
from contextlib import closing

class mysqlConnector:
    
    def __init__(self,host='marshal.netsec.colostate.edu',user='root',passwd='****',dbname='bgp_archive'):
    
    #Prepare DB info
        self.db = pymysql.connect(host=host,
                     user=user, 
                     passwd=passwd, 
                    db=dbname)
        self.dbname=dbname

    def getMessages(self,type,year,month,day,peer):
        
        tableToQuery=type+'_d'+year+month+day+'_p'+peer
        #startTime=year+'-'+month+'-'+day+' '+hour+':00:00.0000'
        #endTime=year+'-'+month+'-'+day+' '+hour+':59:59.000'
        toReturn=[]
        with closing( self.db.cursor() ) as cur: 
            try:
                cur.execute("select MsgTime,inet_ntoa(PrefixIP),PrefixMask,ASPath from {0}.{1} limit 10".format(self.dbname,tableToQuery))
                row=cur.fetchone()
                while row:            
                    try:
                        timeStamp=str(row[0])
                        prefixIP=row[1]
                        prefixMask=str(row[2])
                        prefix=prefixIP+'/'+prefixMask
                        as_path=row[3]
                        entry=timeStamp+"|"+peer+"|"+prefix+"|"+as_path
                        
                        toReturn.append(entry)
                    except:
                        print('Error: '+str(row))
                    row=cur.fetchone()
                    
            except:
                raise Exception('Select to table failed!')

        return toReturn
    
    def close(self):       
        self.db.close()

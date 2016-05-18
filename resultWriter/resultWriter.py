import threading
from contextlib import closing
import os.path
import os
import subprocess
import traceback
from customUtilities.helperFunctions import *
from customUtilities.logger import logger


class ResultWriter():

    def __init__(self,resultfilename,logger=logger('detourResultWriter.log')):
        self.lock = threading.RLock()
        self.resultfilename = resultfilename
        #There could be some old garbage result file with same name, remove it
        if os.path.exists(self.resultfilename):
            os.remove(self.resultfilename)
    
        self.logger=logger
        self.peers = []
        self.rib_name=None
        self.rib_time='NULL'
        self.num_entries=0
        self.num_def_detours=0
        self.num_poss_detours=0
        
        self.ProcessedRibData=[] #List to hold summarized information about result file
        self.ProcessedPeerData=[] #List to hold summarized information per peer
        self.ProcessedPeerInfo=[] #List to hold peer location info
        
    def resetparams(self):
        if os.path.exists(self.resultfilename):
            os.remove(self.resultfilename)
        self.peers = []
        self.rib_name=None
        self.rib_time='NULL'
        self.num_entries=0
        self.num_def_detours=0
        self.num_poss_detours=0
        

    def write(self,val):
        self.lock.acquire()
        try:
            #Log file
            resultfile = open(self.resultfilename,'a')
            valList=eval(val)
            strg=''
            for field in valList:
                #logger.warn(str(field))
                strg=strg+str(field)+'|'
            print(strg[:-1],file=resultfile)
            resultfile.close()
        finally:
            self.lock.release()
    
    def populateProcessedPeerData(self,processedRibsID):
        self.ProcessedPeerData=[]
        for iter in range(0,len(self.peers)):
            flist=[]
            #flist.append('None') # For ID
            flist.append(processedRibsID) 
            flist.append(self.peers[iter].peerIP)
            flist.append(self.peers[iter].peer_num_entries)
            flist.append(self.peers[iter].peer_num_poss_detours)
            flist.append(self.peers[iter].peer_num_def_detours)
            self.ProcessedPeerData.append(flist)

        
    def populateProcessedRibData(self,status):
        self.ProcessedRibData=[]
        flist=[]
        flist.append('None') # For ID
        flist.append(self.rib_name)
        flist.append(self.rib_time)
        curr_epoch,_=currentTime()
        flist.append(curr_epoch)
        flist.append(status)
        flist.append(self.num_entries)
        flist.append(self.num_poss_detours)
        flist.append(self.num_def_detours)
        self.ProcessedRibData.append(flist)
        
    def populateProcessedPeerInfo(self):
        self.ProcessedPeerInfo=[]
        for iter in range(0,len(self.peers)):
            flist=[]
            flist.append('None') # For ID
            flist.append(self.peers[iter].peerAS)
            flist.append(self.peers[iter].peerIP)
            flist.append(self.peers[iter].peerCountry)
            self.ProcessedPeerInfo.append(flist)
            
    def get_ASPath(self,db,as_path): 
        with closing( db.cursor() ) as cur: 
            try:
                cur.execute("select as_path from UniqueAbnormalPaths where as_path = '{0}'".format(as_path))
                retval=cur.fetchone()
            except:
                logger.error("Invalid Path: "+as_path)
                raise Exception('Select ASPath to UniqueAbnormalPaths Failed')
            return retval
        
    def push_UniqueAbnormalPaths(self,db,data): 
        with closing( db.cursor() ) as cur: 
            try:
                #TODO: Check if this path has been pushed previously
                cur.executemany("insert into UniqueAbnormalPaths(id,as_path,countries,analysis,detour_origin_asn,detour_origin_countries,detour_return_asn,detour_return_countries,detour_length,detour_destination_asn,detour_destination_countries,detour_countries_affected) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",data)
                db.commit()
            except:
                raise Exception('Multi-Insert to UniqueAbnormalPaths Failed')


    def push_AbnormalRibEntries(self,db,data): 
        with closing( db.cursor() ) as cur: 
            try:
                cur.executemany("insert into AbnormalRibEntries(id,rib_time,peer,prefix,as_path) values (%s,%s,%s,%s,%s)",data)
                db.commit()
            except:
                raise Exception('Multi-Insert to AbnormalRibEntries Failed')

    def push_ProcessedRibs(self,db,data):
        with closing( db.cursor() ) as cur: 
            try:
                cur.execute("insert into ProcessedRibs(id,rib_name,rib_time,insert_time,read_status,num_entries,num_poss_detours,num_def_detours) values (%s,%s,%s,%s,%s,%s,%s,%s)",data[0])
                db.commit()
                cur.execute("select id from ProcessedRibs where rib_name= '{0}'".format(data[0][1]))
                processedRibsID=cur.fetchone()
                return processedRibsID[0]
            except:
                raise Exception('Multi-Insert to push_ProcessedRibs Failed')
            
    def push_ProcessedPeers(self,db,data):
      
        with closing( db.cursor() ) as cur: 
            try:
                cur.executemany("insert into ProcessedPeers(processedRibsID,peerIP,peer_num_entries,peer_num_poss_detours,peer_num_def_detours) values (%s,%s,%s,%s,%s)",data)
                db.commit()
            except:
                raise Exception('Multi-Insert to ProcessedPeers Failed')
            
    def push_PeerInfo(self,db,data):
       
        with closing( db.cursor() ) as cur: 
            try:
                for datarow in data:
                    cur.execute("select id from PeerInfo where peerIP = '{0}'".format(datarow[2]))
                    retval=cur.fetchone()
                    if not retval:
                        cur.execute("insert into PeerInfo(id,peerAS,peerIP,peerIP_Country) values (%s,%s,%s,%s)",datarow)
                        db.commit()
                       
            except:
                raise Exception('Multi-Insert to push_PeerInfo Failed')
    
              
    def loadtoDB(self,db):
        self.lock.acquire()
        toPushUniqueAbnormalPaths=[]
        toPushAbnormalRibEntries=[]
        try:
            
            #if not os.path.exists(self.resultfilename):
            #    logger.warn('No result file for: '+str(self.resultfilename))
            #    self.resetparams()
            #    return
            
            self.logger.info("Pushing "+self.resultfilename+" to DB.")

            seenASPaths=[]
            if os.path.exists(self.resultfilename):
                f=open(self.resultfilename, 'r')
                for line in f:
                    if line == "":
                        continue
                    rl = line.strip()
                    #TODO: rline should be a dict
                    rline=rl.split('|')
                    if rline[6] == 'poss':
                        self.num_poss_detours+=1  
                    elif rline[6] == 'def':
                        self.num_def_detours+=1    
                        
                    iter=0
                    for pObj in self.peers:
                        if pObj.peerIP == rline[2]:
                            #print(pObj.peerIP, rline[2])
                            if rline[6] == 'poss':
                                self.peers[iter].peer_num_poss_detours+=1
                            elif rline[6] == 'def':
                                self.peers[iter].peer_num_def_detours+=1
                            break
                        iter+=1   
                  
                    if rline[4] not in seenASPaths:
                        if self.get_ASPath(db,rline[4]) is None:
                           
                            finalent=[]
                            finalent.append(rline[0])
                            finalent.append(rline[4])
                            seenASPaths.append(rline[4])
                            finalent.append(str(rline[5]))
                            finalent.append(rline[6])
                            finalent.append(rline[7])
                            #finalent.append("\'"+str(rline[8])+"\'")
                            finalent.append(str(rline[8]))
                            finalent.append(rline[9])
                            finalent.append(str(rline[10]))
                            finalent.append(rline[11])
                            finalent.append(str(rline[12]))
                            finalent.append(str(rline[13]))
                            finalent.append(str(rline[14]))
                            toPushUniqueAbnormalPaths.append(finalent)
                    if rline[6] == 'def':
                        fentry=[]
                        fentry.append(rline[0])
                        fentry.append(rline[1])
                        fentry.append(rline[2])
                        fentry.append(rline[3])
                        fentry.append(rline[4])
                        toPushAbnormalRibEntries.append(fentry)
                f.close()
            #Update ProcessedRibs table
            self.populateProcessedRibData('OK')
            processedRibsID=self.push_ProcessedRibs(db,self.ProcessedRibData) 
            #Update ProcessedPeers table
            self.populateProcessedPeerData(processedRibsID)
            self.push_ProcessedPeers(db,self.ProcessedPeerData)        
            #Update ProcessedPeers table
            self.populateProcessedPeerInfo()
            self.push_PeerInfo(db,self.ProcessedPeerInfo)   
            

            self.push_UniqueAbnormalPaths(db,toPushUniqueAbnormalPaths)
            self.push_AbnormalRibEntries(db,toPushAbnormalRibEntries)
            self.logger.info("Pushed "+self.resultfilename+" to DB.")
            self.resetparams() #resultfile must be closed before this call
            
            
        finally:
            self.lock.release()
        db.commit()
        return toPushAbnormalRibEntries

    def loadTracestoDB(self,db,normalizeabnormalRibEntries):
        for entry in normalizeabnormalRibEntries:
            try:
                id=entry[0]
                ribTime=entry[1]
                peer=entry[2]
                prefix=entry[3]
                net=entry[4]
                randomHost=entry[5]
                asPath=entry[6]
                outfileName=entry[7]
                #Read the warts file
                lines = subprocess.check_output(["sc_warts2json", outfileName],universal_newlines=True)
                data=[]
                data.append(id)
                data.append(ribTime)
                data.append(peer)
                data.append(prefix)
                data.append(net)
                data.append(randomHost)
                data.append(asPath)
                data.append(lines)
                with closing( db.cursor() ) as cur:
                    try:
                        cur.execute("insert into Traceroutes(id,rib_time,peer,prefix,net,host_ip,as_path,json_trace) values (%s,%s,%s,%s,%s,%s,%s,%s)",data)
                        db.commit()
                    except:
                        raise Exception('Multi-Insert to UniqueAbnormalPaths Failed')
                os.remove(outfileName)
            except:
                traceback.print_exc()
                self.logger.error('Problem in inserting data to Traceroutes table.')

            db.commit()

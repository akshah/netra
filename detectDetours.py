#!/usr/bin/python

from __future__ import print_function
from contextlib import closing
import configparser
from queue import Queue
from operator import itemgetter
import threading
import subprocess
import getopt
import time
import pymysql
import ipaddress
import random
import sys
import os
import traceback
from os import listdir
from os.path import isfile, join

from ASPaths.ASPath import ASPath
from ASPaths.DeepPathAnalysis import DeepPathAnalysis
from geoInfo.ASNtoCountryRepo import ASNtoCountryRepo
from geoInfo.MaxMindRepo import MaxMindRepo
from customUtilities.helperFunctions import *
from customUtilities.logger import logger
from customUtilities.processPool import processPool
from Cache.detoursCache import Cache
from resultWriter.resultWriter import ResultWriter
from bgpDataEngine.bgpDataEngine import bgpDataEngine
        
class Peer():

    def __init__(self,peerIP,peerAS,peerCountry):
        self.peerIP = peerIP
        self.peerAS = peerAS
        self.peerCountry = peerCountry
        self.peer_num_entries=0
        self.peer_num_def_detours=0
        self.peer_num_poss_detours=0

         
def usage(msg="Usage"):
    print(msg)
    print('python3 '+sys.argv[0]+' [-l LOGFILE] -c CACHE_FILE -o OUTPUT_FILE -d RIBS_LOCATION [-h]')
    sys.exit(2)

def analyze_path(aspath,peer,prefix):
    tmpPref=[]
    analysis="norm"
    detour_origin_asn = "-"
    detour_origin_country = "-"
    detour_return_asn = "-"
    detour_return_country = "-"
    detour_length = "-"
    detour_destinations = "-"
    detour_destination_asn = "-"
    detour_countries_affected = "-"

    tmpPref.append(prefix)
    aspath.setCountries(asnRepo)
    aspath.cleanUpPaths()#Removes the set() and False entries
    countries=aspath.countries
    if len(countries) > 3:
        if aspath.sameDestAndOriginCountry():
            analysis,countries = aspath.analyze()
            if analysis == "def":
                deepAnalysis=DeepPathAnalysis(aspath)
                detour_origin_asn=str(deepAnalysis.getASNResponsible())
                detour_origin_country=asnRepo.getCountries(detour_origin_asn)
                detour_length=str(deepAnalysis.getLengthOut())
                detour_destinations=str(deepAnalysis.getInternationalCountries())
                detour_destination_asn=str(deepAnalysis.getASNDestination())
                detour_return_asn=str(deepAnalysis.getASNPathReturns())
                detour_return_country=asnRepo.getCountries(detour_return_asn)
                detour_countries_affected=str(deepAnalysis.getCountriesAffected())

    return analysis,countries,detour_origin_asn,detour_origin_country,detour_return_asn,detour_return_country,detour_length,detour_destination_asn,detour_destinations,detour_countries_affected

#Functions that are used to read prefix and peer filters 
def readPrefs(loc):
    toReturn = {}
    with open(loc, 'r') as f:
        for line in f:
            if line == "":
                continue
            prefix = line.strip()
            toReturn[prefix] = True
    return toReturn

def readRVPeers(loc):
    toReturn = {}
    with open(loc, 'r') as f:
        for line in f:
            if line == "":
                continue
            rvpeer = line.strip()
            toReturn[rvpeer] = True
    return toReturn

def isProcessedRib(db,rib_name):
    with closing( db.cursor() ) as cur: 
        try:
            cur.execute("select rib_name from ProcessedRibs where rib_name = '{0}'".format(rib_name))
            retval=cur.fetchone()
        except:
            raise Exception('Select RIB name to isProcessedRib Failed')
        return retval



def simplfyPath(all_ASes):
    prev=''
    strpath=''
    clean_aspath=[]
    for AS in all_ASes:
        if AS != prev:
            prev=AS
            clean_aspath.append(AS)
            strpath=strpath+str(AS)+' '
    return strpath[:-1],clean_aspath

# The worker thread pulls an item from the queue and processes it
def worker():
    while True:
        item = queue.get()
        resolvePaths(item)
        queue.task_done()

def runAnalysis(mrtfiles):
    import os.path
    
    for i in range(NUM_THREADS):
        t = threading.Thread(target=worker)
        t.daemon = True  # Thread dies when main thread (only non-daemon thread) exits.
        t.start()

    numfile=0
    #totalfiles=len(onlyfiles)
    #processedFileCount=1 #Different than numfile, does not count skipped files
    #Chances are cache was populated earlier and written to disk for future use, load it
    if os.path.exists(cache.cachefilename):
        logger.info('A previous cache was seen. Loading cache from disk.')
        cache.load_from_disk()
                
    for fn in mrtfiles:
        
        #File may have moved, check if exists
        if not os.path.exists(fn):
            continue
        #Check if this file was not processed before
        retval=isProcessedRib(db,fn)
        if retval is not None:
            logger.info('MRT file '+fn+' was previously processed. Skipping it.') 
        else:
            numfile+=1
            output.rib_name=os.path.basename(fn)
            filename=fn
            logger.info("bgpdump on " + filename)  
            #bashCommand='bgpdump -m '+filename 

            lines=[]
            try:
                lines = subprocess.check_output(["bgpdump", "-m", filename],universal_newlines=True)
            except:
                logger.warn('BGP file'+filename+' could not be read properly. Skipping it.')
                output.populateProcessedRibData('ERR')
                output.push_ProcessedRibs(db,output.ProcessedRibData) 
                continue
            
            #Prepare Queue
            queue.queue.clear()
            #Buffer
            buffer=[]
           
            logger.info('Reading RIB entries for '+filename) 
            for line in lines.split("\n"):
                if not line.startswith("TAB"):
                    continue
                pieces = line.split('|')

                prefix = pieces[5]
                peer = pieces[3]
                
                if peerFilterEnabled:
                    if peer not in RVPeers:
                        continue #Peer does not match filters
                if prefixFilterEnabled:
                    if prefix not in prefixHash:
                        continue #Prefix does not match filters
                     
                v4Flag=False
                v6Flag=False
                try:
                    net1 = ipaddress.IPv4Address(peer)
                    if net1:
                        v4Flag=True #Valid v4 peer and prefix
                except:
                    try:
                        net1 = ipaddress.IPv6Address(peer)
                        if net1:
                            v6Flag=True #Valid v6 peer and prefix
                    except:
                        if not v6Flag:
                            logger.warn("Saw invalid Peer IP: "+peer)


                v4FlagP=False
                v6FlagP=False
                try:
                    net2 = ipaddress.IPv4Network(prefix)
                    if net2:
                        v4FlagP=True #Valid v4 prefix
                except:
                    try:
                        net2 = ipaddress.IPv6Network(prefix)
                        if net2:
                            v6FlagP=True #Valid v6 prefix
                    except:
                        if not v6FlagP:
                            logger.warn("Saw invalid Prefix: "+prefix)

                if not v4Flag or not v4FlagP:
                    continue #Don't process v6 peers or prefixes

                    
                timestamp = pieces[1]
                output.rib_time=timestamp
                aspath = pieces[6]
               
                all_ASes_orig=aspath.split(' ')
                clean_aspath,all_ASes=simplfyPath(all_ASes_orig)
                #print('Original: '+str(all_ASes_orig)+'Simple: '+str(all_ASes))
                #Check AS path is okay
                if len(all_ASes) < 3:
                    continue
                #peer_as=all_ASes[0]
                output.num_entries+=1
                
                #For PeerInfo Table
                peerlocation = set()
                peerlocation.update(maxmind.ipToCountry(str(peer)))
                peerObj=Peer(peer,all_ASes_orig[0],str(peerlocation))#PeerIP and PeerAS
                peerIsPresent=False
                for po in output.peers:
                    if po.peerIP == peerObj.peerIP:
                        peerIsPresent=True
                if not peerIsPresent:
                    output.peers.append(peerObj)                    
                itr=0
                for pObj in output.peers:
                    if pObj.peerIP == peer:
                        #pObj.peer_num_entries+=1
                        output.peers[itr].peer_num_entries+=1
                    itr+=1
                
                #Populate Queue
                entry=[] 
                entry.append(timestamp)
                entry.append(peer)
                entry.append(prefix)
                entry.append(clean_aspath) 
                #key=prefix+clean_aspath
                #queue.put(entry)
                #logger.info(str(len(buffer)))
                if len(buffer) < BUFFER_SIZE:
                    buffer.append(entry)
                else:
                    for bufferEntry in sorted(buffer,key = itemgetter(3)):
                        queue.put(bufferEntry)
                    del buffer[:]
            
            #There could be leftover items in buffer        
            if len(buffer)>0:
                for bufferEntry in sorted(buffer,key = itemgetter(3)):
                    queue.put(bufferEntry)
                                               
            queue.join() #Block until all queue items are processed
            if(output.num_entries != 0):
                logger.info('Cache hit ratio for '+filename+": "+str(cache.hitcount/output.num_entries))
            #Reset cache hit counter
            cache.reset()  
            logger.info('Done resolving all paths for '+filename)              
                        
            #Load result file in DB and then delete it.
            abnormalRibEntries=[]
            abnormalRibEntries=output.loadtoDB(db)

            #Save at least one cache dump
            if numfile==1:
                cache.write_to_disk()

            logger.info('Done with '+filename)
            #processedFileCount+=1
            
    logger.info('Writing Cache to '+cachefile+' on disk for future use.')
    cache.write_to_disk()
    
def resolvePaths(oneEntry):
    resolveFlag=True
    timestamp=oneEntry[0]
    peer=oneEntry[1]
    prefix=oneEntry[2]
    path=oneEntry[3]
    
    key=path
    
    #Reading Cache
    if key in cache.entry.keys():
        try:
            cache.hit()
            tmplist=eval(cache.get(key))
            resolveFlag=False
            
            if tmplist[2] == "def" and tmplist[9]!="'{False}'":
                finalent=[]
                finalent.append(None)
                finalent.append(timestamp)
                finalent.append(peer) 
                finalent.append(prefix)
                finalent.append(tmplist[0])
                finalent.append("\'"+str(tmplist[1])+"\'")
                finalent.append(tmplist[2])
                finalent.append(tmplist[3])
                finalent.append("\'"+str(tmplist[4])+"\'")
                finalent.append(tmplist[5])
                finalent.append("\'"+str(tmplist[6])+"\'")
                finalent.append(tmplist[7])
                finalent.append(tmplist[8])
                finalent.append("\'"+str(tmplist[9])+"\'")
                finalent.append("\'"+str(tmplist[10])+"\'")
                
                output.write(str(finalent))
        
        except:
            #logger.warn("Reading entry for cache failed")
            resolveFlag=True
            
    if(resolveFlag):       
        toReturn=[]
        toCache=[]
        
        pathObj=ASPath(path)
        verdict,countries,detour_origin_asn,detour_origin_country,detour_return_asn,detour_return_country,detour_length,detour_destination_asn,detour_destinations,detour_countries_affected=analyze_path(pathObj,None,prefix) 
    
        #toCache.append(prefix)
        #TODO: write a type conversion function to map types and then append in for loop
        toCache.append(path)
        toCache.append(countries)
        toCache.append(verdict)
        toCache.append(detour_origin_asn)
        toCache.append(detour_origin_country)
        toCache.append(detour_return_asn)
        toCache.append(detour_return_country)
        toCache.append(detour_length)
        toCache.append(detour_destination_asn)
        toCache.append(detour_destinations)
        toCache.append(detour_countries_affected)
        key=path
        value=str(toCache)
   
        cache.push(key,value)
        
        if verdict == "norm" or detour_destinations=="{False}":
            return
    
        if verdict == "def":
            #all_ases=path.split(" ")
            #origin_asn=all_ases[len(all_ases)-1]
               
            NULL=None
            toReturn.append(NULL)
            toReturn.append(timestamp)
            toReturn.append(peer)
            toReturn.append(prefix)
            toReturn.append(path)
            toReturn.append("\'"+str(countries)+"\'")
            toReturn.append(verdict)
            toReturn.append(detour_origin_asn)
            toReturn.append("\'"+str(detour_origin_country)+"\'")
            toReturn.append(detour_return_asn)
            toReturn.append("\'"+str(detour_return_country)+"\'")
            toReturn.append(detour_length)
            toReturn.append(detour_destination_asn)
            toReturn.append("\'"+str(detour_destinations)+"\'")
            toReturn.append("\'"+str(detour_countries_affected)+"\'")
            
            output.write(str(toReturn))
        
            return



if __name__ == "__main__":
    
    if sys.version_info < (3,0):
        print("ERROR: Please use python3.")
        exit(0)

    configFile='conf/detourDetection.conf'
    config = configparser.ConfigParser()
    config.read(configFile)
    config.sections()

    try:
        dbname=config['MySQL']['dbname']

        peerFilterEnabled=eval(config['FILTERS']['peerFilterEnabled'])
        prefixFilterEnabled=eval(config['FILTERS']['prefixFilterEnabled'])

        NUM_THREADS=int(config['EXEC']['numThreads'])
        BUFFER_SIZE=int(config['EXEC']['bufferSize'])
        CACHE_SIZE=int(config['EXEC']['cacheSize'])

        logfilename=config['DEFAULTS']['logFile']
        dirpath=config['DEFAULTS']['MRTDir']
        tracerouteDir=config['DEFAULTS']['tracerouteDir']
    except:
        print('Error in reading config '+configFile)
        exit(1)

    cachefile=None
    resultfile=None
    try:
        opts,args = getopt.getopt(sys.argv[1:],'c:o:h',['cachefile','outputfile','help'])
    except getopt.GetoptError:
        traceback.print_exc()
        usage('GetoptError: Arguments not correct') 

    for opt,arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif opt in ('-c', '--cachefile'):
            cachefile = arg
        elif opt in ('-o', '--outputfile'):
            resultfile = arg

    if not dirpath:
        usage('Missing directory to read MRT from')

    #Logger
    if not logfilename:
        scriptname=sys.argv[0].split('.')
        logfilename=scriptname[0]+'.log'
    logger=logger(logfilename)
    
    #Cache to save already seen paths 
    if not cachefile:
        cachefile=config['DEFAULTS']['cacheFile']
    cache=Cache(cachefile,logger,CACHE_SIZE)
    
    if not resultfile:
        resultfile=config['DEFAULTS']['resultFile']
    output=ResultWriter(resultfile,logger)
    
    #Queue to hold data
    queue=Queue()
 
    #Prepare DB info
    db = pymysql.connect(host="proton.netsec.colostate.edu",
                     user="root", 
                     passwd="****",
                    db=dbname)
    
    
    #Reading ASN Geolocation
    asnRepo = ASNtoCountryRepo()
    asnRepo.load()
    logger.info('ASN to Country Mappings Read.')

    if peerFilterEnabled:
        logger.info("Peer filter is enabled")
        RVPeersLoc= config['FILTERS']['peerFilter']
        RVPeers = None      
        RVPeers = readRVPeers(RVPeersLoc)
        
    if prefixFilterEnabled:
        logger.info("Prefix filter is enabled")
        prefixFileLoc = config['FILTERS']['prefixFilter']
        prefixHash = None
        prefixHash = readPrefs(prefixFileLoc)
    
    maxmind = MaxMindRepo()
    NUM_HOURS_PREV=int(config['EXEC']['numHoursInterval'])
    while True:
        start_time,_=currentTime()

        currEpoch,strTime=currentTime()
        currEpoch=int(str(currEpoch).split('.')[0])-3600
        strTime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(currEpoch))
        preTime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(currEpoch-(NUM_HOURS_PREV*3600)))
        srtTimeFormatted=strTime.replace(' ','').replace(':','').replace('-','')
        strPreTimeFormatted=preTime.replace(' ','').replace(':','').replace('-','')

        logger.info('-----Running detour detection for {0} to {1}-----'.format(preTime,strTime))

        bde=bgpDataEngine()
        #select source of BGP data
        bde.accessToBGPMonArchive = False
        bde.accessToRVArchive = True
        bde.accessToRipeArchive = False
        bde.getRange('ribs',strPreTimeFormatted,srtTimeFormatted)
        mrtfilesTmp=bde.filesDownloaded
        del(bde)

        mrtfiles=[]
        for name in mrtfilesTmp:
            if name.lower().endswith('.gz') or name.lower().endswith('.mrt') or name.lower().endswith('.bz2'):
                if 'rib' in name or 'bview' in name:
                    #Sampling
                    #or '.0800.' in name or '.1600.' in name
                    if '.0000.' in name:
                        mrtfiles.append(name)

        if len(mrtfiles)==0:
            logger.warn("No MRT file found")
            print("WARN: Given directory does not contain MRT files.")

        mrtfiles.sort()

        runAnalysis(mrtfiles)

        end_time,_=currentTime()
        processingTime=str(int((end_time-start_time)/60))+' minutes and '+str(int((end_time-start_time)%60))+' seconds'
        db.commit()

        command="python2.7 runRIPETraceroute.py &> riperun.stdout"
        os.system(command)

        logger.info('-----Finished detour detection for {0} to {1} in {2}-----'.format(preTime,strTime,processingTime))

        time.sleep(NUM_HOURS_PREV*3600)


    db.close()



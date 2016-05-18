import os
import threading
from cachetools import LRUCache
from customUtilities.logger import logger

class Cache():

    def __init__(self,cachefilename,CACHE_SIZE,logger=logger('detoursCache.log')):
        self.lock = threading.RLock()
        self.cachefilename = cachefilename
        self.entry = LRUCache(maxsize=CACHE_SIZE)
        self.logger=logger
        self.hitcount=0
       
    def hit(self):
        self.lock.acquire(blocking=1)
        try:
            self.hitcount+=1
        finally:
            self.lock.release()
            
    def reset(self):
        self.lock.acquire(blocking=1)
        try:
            self.hitcount=0
        finally:
            self.lock.release()
            
    def push(self,key,val):
        self.lock.acquire(blocking=1)
        try:
            self.entry[key]=val
        except:
            return
        finally:
            self.lock.release()
    
    def get(self,key):
        self.lock.acquire(blocking=1)
        try:
            return self.entry[key]
        except:
            return False
        finally:
            self.lock.release()
            
    def write_to_disk(self):
        self.lock.acquire(blocking=1)
        try:
            cachefile = open(self.cachefilename,'w')
            for key,val in self.entry.items():
                print(key+'\t'+val,file=cachefile)
            cachefile.close()
        finally:
            self.lock.release()
            
    def load_from_disk(self):
        self.lock.acquire(blocking=1)
        try:
            if os.path.exists(self.cachefilename):
                with open(self.cachefilename, 'r') as f:
                    for line in f:
                        if line == "":
                            continue
                        rline = line.strip()
                        splitvals=rline.split('\t')
                        if len(splitvals) == 2:
                            key=splitvals[0]
                            valstr=splitvals[1] 
                            self.entry[key]=valstr    
                        else:
                            continue
        except:
            self.logger.error("Failed to read existing cache file")
            raise("Error in loading previous cache file")
        
        finally:
            self.lock.release()
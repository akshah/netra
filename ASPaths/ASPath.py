from ASPaths.PathAnalysis import PathAnalysis


class ASPath:
    
    def __init__(self, aspathlst):
        #Key for hashing
        self.aspathstr = None
        
        if isinstance(aspathlst, str):
            self.aspathstr = aspathlst
            aspathlsttmp = aspathlst.split()
            aspathlst = aspathlsttmp
        #Path    
        self.aspath = aspathlst
        
        
        if self.aspathstr == None:
            self.aspathstr = " ".join(self.aspath)
            
        #Countries for path
        self.countries = None

        
    '''
    Use ASN repo to geolocate all ASes
    '''
    def setCountries(self,asnRepo):
        getCou = asnRepo.getCountries
        self.countries = []
        
        for asn in self.aspath:
            self.countries.append(getCou(asn))
    
    def cleanUpPaths(self):      
        #print("Orig: "+str(self.aspath))
        #print("Orig: "+str(self.countries))
        itemsToRemove = []
        for i in range(len(self.countries)):
            cSet = self.countries[i]
            if cSet == False:
                itemsToRemove.append(i)
            elif len(cSet) == 0:
                itemsToRemove.append(i)
        itemsToRemove.reverse()
        for index in itemsToRemove:
            self.aspath.pop(index)
            self.countries.pop(index)
        #print("After: "+str(self.aspath))
        #print("After: "+str(self.countries))
            
    def sameDestAndOriginCountry(self):
        if len(self.countries[0]) == 1 and self.countries[0] == self.countries[len(self.countries)-1]:
            return True
        else:
            return False
        
        
    def isCompletelyDefined(self):
        return all(map(lambda x : len(x) > 0, self.countries))
        
    def analyze(self):
        self.beenAnalyzed = True
        definite = False
        possible = False
        
        analysis = PathAnalysis(self.countries)
        result = analysis.getResult()
        #We only care if the path is defBad or possBad. If undef or fine, don't care
        if result == 1:
            definite = True
        elif result == 2:
            possible = True
            
        if definite:
            self.defIntern = definite
            return 'def',self.countries
        elif possible:
            self.potentialIntern = possible
            return 'poss',self.countries
        else:
            return 'norm',self.countries
        
        
    def getOriginCountries(self):
        return self.countries[-1]

    def hasASN(self, asn):
        return asn in self.aspath
    
    def getOrigin(self):
        return self.aspath[-1]
    def getPeer(self):
        return self.aspath[0]
    def getPath(self):
        return self.aspath
    def getPathLessPeerOrigin(self):
        return self.aspath[1:-1]
       
    def asStr(self):
        return self.aspathstr
    

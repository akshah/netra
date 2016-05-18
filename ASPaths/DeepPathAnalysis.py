from ASPaths.PathAnalysis import PathAnalysis


class DeepPathAnalysis(object):
    '''
    Checks to see that we are giving it a path that is def abnormal.  Othersize it just gives data from PathAnalysis
    '''
    def __init__(self, aspath):
        self.aspath = aspath
        
        self.data = list(zip(aspath.aspath, aspath.countries))
        #print("ORIGINAL: "+str(self.data))
        # Making sure we have something at each hop
        itemsToRemove = []
        for i in range(len(self.data)):
            _, cSet = self.data[i]
            if cSet == False:
                itemsToRemove.append(i)
            elif len(cSet) == 0:
                itemsToRemove.append(i)
        itemsToRemove.reverse()
        for index in itemsToRemove:
            self.data.pop(index)
        
        self.pathAnalysisResult = None
        self.goodCountry = None
        self.badCountires = None
        self.affectedCountry = None
        self.badOutASN = None
        self.badInASN = None
        self.DestinationASN = None
        self.lengthOut = None
        self.processedSuccessfully = False
        
        self._runAnalysis()
        
    def _runAnalysis(self):
        
        # running regular analysis
        analysis = PathAnalysis(self.aspath.countries)
        self.pathAnalysisResult = analysis.getResult()
        
        # Making sure we only have a def bad path
        if self.pathAnalysisResult != 1:
            return
        
        # Getting the path and the set of counties and joining them into tuples [index, (asn, set(countries))]
        originalData = list(enumerate(self.data))
        
        # Getting one example of the problem
        #sampleData = self._getZipSampleData()
        #print(sampleData)
        #print(originalData)
        #sampleData = self._simplify(sampleData)

        #print(sampleData)
        # Finding where the jump occurs and marking indexes in the regular path for final analysis
        #outIndex, inIndex = self._findIndexesForJump(sampleData)
        #originalData=self._simplify(originalData)
        outIndex, inIndex, detourIndex = self._findIndexesForJumpSetNew(originalData)
        
        # Transforming back to the original data
        oOutIndex = originalData[outIndex][0]
        oInIndex = originalData[inIndex][0]
        oDetourIndex = originalData[detourIndex][0]
        
        # Finding length out
        self.lengthOut = oInIndex - (oOutIndex + 1)
        
        # Marking ASNs for this cause
        self.badOutASN = originalData[oOutIndex][1][0]
        self.DestinationASN = originalData[oDetourIndex][1][0]
        self.badInASN = originalData[oInIndex][1][0]
        
        # Finding all of the countries the route could have gone to
        self.badCountires = set()
        #for i in range(oInIndex+1, oOutIndex):
        thisCountry = originalData[oDetourIndex][1][1]
        self.badCountires.update(thisCountry)
            
        #self.badCountires.difference_update(originalData[0][1][1])

        # Finding countries affected
        self.affectedCountry = originalData[outIndex][1][1].intersection(originalData[inIndex][1][1])
        
        self.processedSuccessfully = True
        
        
    def _getZipCountriesAndASNs(self):
        return list(enumerate(zip(self.aspath.aspath, self.aspath.countries)))
    
    
    def _findIndexesForJumpSet(self, originalData):
        print(originalData)
        seen = set()
        #seen.add(originalData[0][1][1])
        FlagSearch=False
        badCountry =set()
        #sampleDataLessOne=sampleData[1:]
        outIndex = None
        inIndex = None
        badCountry = None
        
        # Finding the index and country that have jump
        #print(sampleData)
        
        for index, tupSet in originalData:
            _, countrySet = tupSet
            #if country not in seen:
                #seen.add(country)
            #else:
            if index > 0 and countrySet != seen:#Covers for {US}{US}{GE}{US} cases
                FlagSearch=True
                
            if countrySet == seen and FlagSearch:
                outIndex = index
                badCountry = countrySet
                break
            if index == 0:
                seen=countrySet
            
        
        #finding first instance of country
        for index, tupSet in originalData:
            _, countrySet = tupSet
            if countrySet != badCountry:
                inIndex = index-1 #Previous one
                break
            
        return outIndex, inIndex
    
    def _findIndexesForJumpSetNew(self, originalData):
        #print(originalData)
        origCountry = set()
        #seen.add(originalData[0][1][1])
        FlagSearch=False
        badCountry =set()
        #sampleDataLessOne=sampleData[1:]
        outIndex = None
        detourIndex = None
        inIndex = None
        badCountry = None
        
        # Finding the index and country that have jump
        #print(sampleData)
        
        for index, tupSet in originalData:
            _, countrySet = tupSet
            if index == 0:
                origCountry=countrySet
                continue
            if index > 0 and countrySet.intersection(origCountry)!=origCountry and not FlagSearch:#Covers for {US}{US}{GE}{US} cases
                detourIndex=index
                outIndex=index-1#Previous one
                badCountry = countrySet
                FlagSearch=True     
            if FlagSearch and countrySet == origCountry:
                inIndex = index
                break
            
        return outIndex, inIndex, detourIndex
    
        
    def getPathAnalysisResult(self):
        assert self.pathAnalysisResult is not None
        return self.pathAnalysisResult
    
    def getLengthOut(self):
        assert self.badCountires is not None
        return self.lengthOut
    
    def getInternationalCountries(self):
        assert self.badCountires is not None
        return self.badCountires
    
    def getASNResponsible(self):
        assert self.badOutASN is not None
        return self.badOutASN
    
    def getASNDestination(self):
        assert self.DestinationASN is not None
        return self.DestinationASN
    
    def getASNPathReturns(self):
        assert self.badInASN is not None
        return self.badInASN

    def getCountriesAffected(self):
        return self.affectedCountry
    
    

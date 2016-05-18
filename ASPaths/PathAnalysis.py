from itertools import product
from copy import deepcopy

'''Detects if a cycle is present'''

def hasCycle(path):
    if len(path) < 3:
        return False
     
    #simplifying path
    simpPath = [path[0]]
    a = simpPath.append
    restPath = path[1:]
    for country in restPath:
        if country != simpPath[-1]:
            a(country)
    
    #print(simpPath)
    
    #Making sure we have something to look at
    if len(simpPath) < 3:
        return False

    if simpPath[0] != simpPath[len(simpPath)-1]:
        return False

    #checking
    seen = set()
    a = seen.add
    a(simpPath[0])
    simpPathLessone=simpPath[1:]
    for country in simpPathLessone:
        if country in seen:
            #print("Returning True")
            return True
        #a(country)
        #print(seen)
    return False

class PathAnalysis(object):

    def __init__(self, countries):
        self.countries = deepcopy(countries)
        
        #making sure we have something for each jump
        indexToRemove = []
        for i in range(len(self.countries)):
            if len(self.countries[i]) == 0:
                indexToRemove.append(i)
        indexToRemove.reverse()
        for index in indexToRemove:
            self.countries.pop(index)
        
        
        self.result = None
        self.analyze()
        
        
    def analyze(self):
        
        results=[]
            
        #Making all of the possibilities
        allGraphs = product(*self.countries)
        
        for g in allGraphs:
            results.append(hasCycle(g))
        
        #Now searching for cycles
        #results = [hasCycle(graph) for graph in allGraphs]
        numCycles = results.count(True)
        
        #Seeing if it's definately an anomolous path
        if numCycles == len(results):
            self.result = 1
        #Seeing if it's only potentially anomolous    
        elif numCycles > 0:
            self.result = 2
        #Everying seems to be fine
        else:
            self.result = 0
    
    '''
    Returns 1 if def bad
    Returns 2 if possibly bad
    Retuns 0 if not bad
    '''
    def getResult(self):
        return self.result
            
            
        
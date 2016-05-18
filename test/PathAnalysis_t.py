import unittest
from ASPaths.PathAnalysis import PathAnalysis

class Test(unittest.TestCase):


    def setUp(self):
        self.errorPath1 =  [{'US'}, {'AU'}, set()]
        
        self.badPath1 =  [{'US'}, {'AU'},{'US'}]       
        self.badPath2 =  [{'US'}, {'AU'}, {'US'}, {'GE'}, {'US'}]
        self.badPath3 =  [{'US'}, {'CA'}, {'UK'}, {'US'}]
        self.badPath4 =  [{'US'}, {'UK'}, {'UK','DE'}, {'US'}, {'US'}]
        self.badPath5 =  [{'US'}, {'UK'}, {'US','DE'}, {'UK'}, {'US'}]
        self.badPath6 =  [{'US'}, {'IN','US'}, {'CN'}, {'US'}]
        self.badPath7 =  [{'US'}, set(), {'US'}, {'GE'}, {'US'}]
        
        self.possBadPath1 =  [{'GE','US'}, {'AU'}, {'GE','US'}]
        self.possBadPath2 =  [{'GE','US'}, {'AU', 'GE'}, {'GE','US'}]
        self.possBadPath3 =  [{'US','CA'}, {'IN'}, {'CN'}, {'US'}]
        self.possBadPath4 = [{'US','CA'}, {'IN','US'}, {'US'}]
        self.possBadPath5 =  [{'US','CA'}, {'IN','US'}, {'US'}, {'US'}]
        self.possBadPath6 =  [{'US','CA'}, {'AU'}, {'FR'}, {'AU'}, {'US'}]
        self.possBadPath7 =  [{'US'}, {'IN'}, {'UK'}, {'US','CA'}]
        self.possBadPath8 =  [{'US','CA'}, {'AU'}, {'FR'}, {'AU'}, {'US','CA'}]
        self.possBadPath9 =  [{'US'}, {'IN','US'}, {'CN','US'}, {'US'}]
        self.possBadPath10 =  [{'US','CA'}, {'US','FR'}, {'US','UK'}, {'US'}]
        
        self.finePath1 =  [{'US'}, {'US'}, set(), {'US'}]
        self.finePath2 =  [{'GE'},{'SP'},{'US'},{'US'}]
        self.finePath3 =  [{'GE'},{'US'},{'SP'},{'US,GE'},{'US'}]
        self.finePath4 =  [{'GE'},{'US'},{'SP'},{'US','GE'},{'US','SP'}]

    def tearDown(self):
        pass


    def testErrorPaths(self):
        #print("Testing Error Paths")
        analysis = PathAnalysis(self.errorPath1)
        assert analysis.getResult() == 0
             
    def testBadPaths(self):
        #print("Testing Bad Paths")
        analysis = PathAnalysis(self.badPath1)
        assert analysis.getResult() == 1
        
        analysis = PathAnalysis(self.badPath2)
        assert analysis.getResult() == 1
        
        analysis = PathAnalysis(self.badPath3)
        assert analysis.getResult() == 1
        
        analysis = PathAnalysis(self.badPath4)
        assert analysis.getResult() == 1
        
        analysis = PathAnalysis(self.badPath5)
        assert analysis.getResult() == 1
        
        analysis = PathAnalysis(self.badPath6)
        assert analysis.getResult() == 1
        
        analysis = PathAnalysis(self.badPath7)
        assert analysis.getResult() == 1
    
    def testPossBadPaths(self):
        #print("Testing Possible Bad Paths")
        analysis = PathAnalysis(self.possBadPath1)
        assert analysis.getResult() == 2
        
        analysis = PathAnalysis(self.possBadPath2)
        assert analysis.getResult() == 2
        
        analysis = PathAnalysis(self.possBadPath3)
        assert analysis.getResult() == 2
        
        analysis = PathAnalysis(self.possBadPath4)
        assert analysis.getResult() == 2
        
        analysis = PathAnalysis(self.possBadPath5)
        assert analysis.getResult() == 2
        
        analysis = PathAnalysis(self.possBadPath6)
        assert analysis.getResult() == 2
        
        analysis = PathAnalysis(self.possBadPath7)
        assert analysis.getResult() == 2
        
        analysis = PathAnalysis(self.possBadPath8)
        assert analysis.getResult() == 2
        
        analysis = PathAnalysis(self.possBadPath9)
        assert analysis.getResult() == 2
        
        analysis = PathAnalysis(self.possBadPath10)
        assert analysis.getResult() == 2
    
    def testFinePaths(self):
        #print("Testing Fine Paths")
        analysis = PathAnalysis(self.finePath1)
        assert analysis.getResult() == 0
        
        analysis = PathAnalysis(self.finePath2)
        assert analysis.getResult() == 0
        
        analysis = PathAnalysis(self.finePath3)
        assert analysis.getResult() == 0
        
        analysis = PathAnalysis(self.finePath4)
        assert analysis.getResult() == 0


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
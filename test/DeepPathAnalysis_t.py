import unittest
from ASPaths.ASPath import ASPath
from ASPaths.DeepPathAnalysis import DeepPathAnalysis

class DeepPathAnalysisTest(unittest.TestCase):


    def setUp(self):
        '''
        Setting up ASPaths with their countries already set.  Preparing for deep analysis
        '''
        
        self.errorASPath1 = ASPath(['1221' ,'1234','12145'])
        self.errorASPath1.countries = [{'US'}, {'AU'}, set()]
        
        self.badASPath1 = ASPath(['1221', '1234' ,'12145'])
        self.badASPath1.countries = [{'US'}, {'AU'},{'US'}]
        
        self.badASPath2 = ASPath(['1221', '1234' ,'12145', '666' ,'111111'])
        self.badASPath2.countries = [{'US'}, {'AU'}, {'US'}, {'GE'}, {'US'}]
        
        self.badASPath3 = ASPath(['11537', '22388', '7660', '288'])
        self.badASPath3.countries = [{'US'}, {'CA'}, {'UK'}, {'US'}]
        
        self.badASPath4 = ASPath(['11537' ,'22388' ,'7660', '288' ,'455'])
        self.badASPath4.countries = [{'US'}, {'UK'}, {'UK','DE'}, {'US'}, {'US'}]
        
        self.badASPath5 = ASPath(['11537','22388','7660','288','455'])
        self.badASPath5.countries = [{'US'}, {'UK'}, {'US','DE'}, {'UK'}, {'US'}]
        
        self.badASPath6 = ASPath(['11537','22388','7660','288'])
        self.badASPath6.countries = [{'US'}, {'IN','US'}, {'CN'}, {'US'}]
        
        self.badASPath7 = ASPath(['1221','1234','12145','666','555'])
        self.badASPath7.countries = [{'US'}, set(), False, {'GE'}, {'US'}]
        self.badASPath7.cleanUpPaths()
        
        self.possBadASPath1 = ASPath(['1221','1234','12141'])
        self.possBadASPath1.countries = [{'GE','US'}, {'AU'}, {'GE','US'}]
        
        self.possBadASPath2 = ASPath(['1221','1234','12141'])
        self.possBadASPath2.countries = [{'GE','US'}, {'AU', 'GE'}, {'GE','US'}]
        
        self.possBadASPath3 = ASPath(['1221','1234','12141','228'])
        self.possBadASPath3.countries = [{'US','CA'}, {'IN'}, {'CN'}, {'US'}]
        
        self.possBadASPath4 = ASPath(['1221','1234','12141'])
        self.possBadASPath4.countries = [{'US','CA'}, {'IN','US'}, {'US'}]
        
        self.possBadASPath5 = ASPath(['1221','1234','12141','228'])
        self.possBadASPath5.countries = [{'US','CA'}, {'IN','US'}, {'US'}, {'US'}]
        
        self.possBadASPath6 = ASPath(['1221','1234','12141','228','333'])
        self.possBadASPath6.countries = [{'US','CA'}, {'AU'}, {'FR'}, {'AU'}, {'US'}]
        
        self.possBadASPath7 = ASPath(['1221','1234','12141','228'])
        self.possBadASPath7.countries = [{'US'}, {'IN'}, {'UK'}, {'US','CA'}]
        
        self.possBadASPath8 = ASPath(['1221','1234','12141','228','333'])
        self.possBadASPath8.countries = [{'US','CA'}, {'AU'}, {'FR'}, {'AU'}, {'US','CA'}]
        
        self.possBadASPath9 = ASPath(['1221','1234','12141','228'])
        self.possBadASPath9.countries = [{'US'}, {'IN','US'}, {'CN','US'}, {'US'}]
        
        self.possBadASPath10 = ASPath(['1221','1234','12141','228'])
        self.possBadASPath10.countries = [{'US','CA'}, {'US','FR'}, {'US','UK'}, {'US'}]
        
        
        self.fineASPath1 = ASPath(['1221','1234','12145','666'])
        self.fineASPath1.countries = [{'US'}, {'US'}, set(), {'US'}]
        
        self.fineASPath2 = ASPath(['1221','1234','12145','666'])
        self.fineASPath2.countries = [{'GE'},{'SP'},{'US'},{'US'}]
        
        self.fineASPath3 = ASPath(['1221','1234','12145','666','444'])
        self.fineASPath3.countries =  [{'GE'},{'US'},{'SP'},{'US','GE'},{'US'}]
        
        self.fineASPath4 = ASPath(['1221','1234','12145','666','444'])
        self.fineASPath4.countries =  [{'GE'},{'US'},{'SP'},{'US','GE'},{'US','SP'}]

    
    def tearDown(self):
        pass

    def testErrorPaths(self):
        analysis = DeepPathAnalysis(self.errorASPath1)
        assert analysis.getPathAnalysisResult() == 0


   
 
#         self.badASPath7 = ASPath(['1221','1234','12145','666','555'])
#         self.badASPath7.countries = [{'US'}, set(), False, {'GE'}, {'US'}]
       
    def testBadPaths(self):
        analysis = DeepPathAnalysis(self.badASPath1)
        assert analysis.getPathAnalysisResult() == 1
        assert analysis.getInternationalCountries() == {'AU'}
        assert analysis.getCountriesAffected() == {'US'}
        assert analysis.getLengthOut() == 1
        assert analysis.getASNResponsible() == '1221'
        assert analysis.getASNDestination() == '1234'
        assert analysis.getASNPathReturns() == '12145'
        
        analysis = DeepPathAnalysis(self.badASPath2)
        assert analysis.getPathAnalysisResult() == 1
        assert analysis.getInternationalCountries() == {'AU'}
        assert analysis.getCountriesAffected() == {'US'}
        assert analysis.getLengthOut() == 1
        assert analysis.getASNResponsible() == '1221'
        assert analysis.getASNDestination() == '1234'
        assert analysis.getASNPathReturns() == '12145'
        
        analysis = DeepPathAnalysis(self.badASPath3)
        assert analysis.getPathAnalysisResult() == 1
        #print(analysis.getInternationalCountries())
        assert analysis.getInternationalCountries() == {'CA'}
        assert analysis.getCountriesAffected() == {'US'}
        assert analysis.getLengthOut() == 2
        assert analysis.getASNResponsible() == '11537'
        assert analysis.getASNDestination() == '22388'
        assert analysis.getASNPathReturns() == '288'

        analysis = DeepPathAnalysis(self.badASPath4)
        assert analysis.getPathAnalysisResult() == 1
        assert analysis.getInternationalCountries() == {'UK'} 
        assert analysis.getCountriesAffected() == {'US'}
        assert analysis.getLengthOut() == 2
        assert analysis.getASNResponsible() == '11537'
        assert analysis.getASNDestination() == '22388'
        assert analysis.getASNPathReturns() == '288'
        
       
        analysis = DeepPathAnalysis(self.badASPath5)
        assert analysis.getPathAnalysisResult() == 1
        assert analysis.getInternationalCountries() == {'UK'}
        assert analysis.getCountriesAffected() == {'US'}
        assert analysis.getLengthOut() == 3
        assert analysis.getASNResponsible() == '11537'
        assert analysis.getASNDestination() == '22388'
        assert analysis.getASNPathReturns() == '455'
        
       
        analysis = DeepPathAnalysis(self.badASPath6)
        assert analysis.getPathAnalysisResult() == 1
        assert analysis.getInternationalCountries() == {'CN'}
        assert analysis.getCountriesAffected() == {'US'}
        assert analysis.getLengthOut() == 1
        assert analysis.getASNResponsible() == '22388'
        assert analysis.getASNDestination() == '7660'
        assert analysis.getASNPathReturns() == '288'
        
        analysis = DeepPathAnalysis(self.badASPath7)
        assert analysis.getPathAnalysisResult() == 1
        assert analysis.getInternationalCountries() == {'GE'}
        assert analysis.getCountriesAffected() == {'US'}
        assert analysis.getLengthOut() == 1
        assert analysis.getASNResponsible() == '1221'
        assert analysis.getASNDestination() == '666'
        assert analysis.getASNPathReturns() == '555'  
    
    
    def testPossBadPaths(self):
        analysis = DeepPathAnalysis(self.possBadASPath1)
        assert analysis.getPathAnalysisResult() == 2
        
        analysis = DeepPathAnalysis(self.possBadASPath2)
        assert analysis.getPathAnalysisResult() == 2
        
        analysis = DeepPathAnalysis(self.possBadASPath3)
        assert analysis.getPathAnalysisResult() == 2
        
        analysis = DeepPathAnalysis(self.possBadASPath4)
        assert analysis.getPathAnalysisResult() == 2
        
        analysis = DeepPathAnalysis(self.possBadASPath5)
        assert analysis.getPathAnalysisResult() == 2
        
        analysis = DeepPathAnalysis(self.possBadASPath6)
        assert analysis.getPathAnalysisResult() == 2
        
        analysis = DeepPathAnalysis(self.possBadASPath7)
        assert analysis.getPathAnalysisResult() == 2
        
        analysis = DeepPathAnalysis(self.possBadASPath8)
        assert analysis.getPathAnalysisResult() == 2
        
        analysis = DeepPathAnalysis(self.possBadASPath9)
        assert analysis.getPathAnalysisResult() == 2
        
        analysis = DeepPathAnalysis(self.possBadASPath10)
        assert analysis.getPathAnalysisResult() == 2
        
    
    def testFinePaths(self):
        analysis = DeepPathAnalysis(self.fineASPath1)
        assert analysis.getPathAnalysisResult() == 0
        
        analysis = DeepPathAnalysis(self.fineASPath2)
        assert analysis.getPathAnalysisResult() == 0
        
        analysis = DeepPathAnalysis(self.fineASPath3)
        assert analysis.getPathAnalysisResult() == 0
        
        analysis = DeepPathAnalysis(self.fineASPath4)
        assert analysis.getPathAnalysisResult() == 0
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

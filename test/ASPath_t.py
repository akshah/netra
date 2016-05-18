import unittest
from ASPaths.ASPath import ASPath


class TestASPath(unittest.TestCase):
    
    def setUp(self):
        self.aspath1 = ASPath(['12145','11100', '666'])
        self.aspath2 = ASPath(['12145','11100', '666', '666'])
        self.aspath3 = ASPath(['45','11100', '666'])
        self.aspath4 = ASPath(['12145','11100', '666', '111'])
        self.aspath5 = ASPath(['111','11100', '666', '111'])
        self.aspath5.countries = [{'US'}, {'SN'}, {'GE'}, {'US'}]
        self.aspath2.countries = [{'UK'}, {'SO'}, {'GE'}, {'DE'}]


    def testGetOriginandPeerandLength(self):
        assert self.aspath1.getOrigin() == '666'
        assert self.aspath1.getPeer() == '12145'
        
    def testSameOriginAndDestCountry(self):
        assert self.aspath5.sameDestAndOriginCountry()
        assert not self.aspath2.sameDestAndOriginCountry() 
    

if __name__ == "__main__":
    unittest.main()
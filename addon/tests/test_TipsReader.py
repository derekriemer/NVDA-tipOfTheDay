import unittest
import uuid
import sys, os

#add the appropriate files to the  path so importing them works.
sys.path.append("globalPlugins")
from tipsReader import Tips

class TipsTester(unittest.TestCase):
    def setUp(self):
        self.t1 = Tips(os.path.join(os.path.dirname(__file__), "assetts", "t1.json"))
    
    def test_app_exists(self):
        self.assertIsNotNone(self.t1.app)
    
    def test_app_is_correct(self):
        self.assertEqual(self.t1.app, "winword")
    
    def test_get_invalid_tip_name_is_None(self):
        self.assertIsNone(self.t1.getTip("bananas are awesome"))
    
    def test_iterateTips(self):
        for i in self.t1:
            self.assertIn(i, self.t1.tips)
            self.assertIsNotNone(self.t1.getTip(i))
            self.assertIsInstance(self.t1.getTip(i), dict)
    
    def test_non_existant_file(self):
        with self.assertRaises(IOError):
            Tips(str(uuid.uuid1()))
    
    def test_malformedJson(self):
        with self.assertRaises(ValueError):
            Tips(os.path.join(os.path.dirname(__file__), "assetts", "bad_file.txt"))
    
    

if __name__ == '__main__':
    #suite = unittest.TestLoader().loadTestsFromTestCase(TipsTester)
    unittest.run()
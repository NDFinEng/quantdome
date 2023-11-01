import unittest
import data_microservice
import os
import csv

cwd = os.getcwd()
GOOG = f"{cwd}/../../main/data/GOOG_test.csv"

class TestStringMethods(unittest.TestCase):

    def test_csv(self):
        self.assertEqual(data_microservice(GOOG), csv.reader(f'{GOOG}'))
        
"""
    def test_isupper(self): 
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
"""

if __name__ == '__main__':
    unittest.main()
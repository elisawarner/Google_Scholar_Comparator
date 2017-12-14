# least 1 subclass of unittest.TestCase
# at least 5 total test methods (consider what you most need to test!)
# X at least one use of the setUp and tearDown test methods.
# Each of the test methods you write must be good tests (meaning they won't always pass -- or always fail
# they will catch semantic errors -- not just syntax errors).

import unittest
import csv
import sys
from SI507F17_finalproject import *

class Part1(unittest.TestCase):
    def setUp(self):
        wrapper_call("Parakeet", 1)
        self.cache = open('cache_file.json')
        self.csv_file = open('PARAKEET.csv')

    def test_cache_exists(self):
        self.assertTrue(self.cache.read(), 'No cache found')

    def test_csv_file(self):
        self.assertTrue(self.csv_file.read(), 'No csv found')

    # csv contains rows with 4 columns each
    def test_csv_columns(self):
        # checks first row
        self.assertEqual(len(self.csv_file.readline().split(',')), 7, "Error with csv file length")


class Part2(unittest.TestCase):
    def setUp(self):
        a = Paper(search_google_scholar('Parakeet')[0])
    # csv tags is a list
    def test_title(self):
    	# should return True as a list
        self.assertEqual(a.title, "Hearing in the parakeet (Melopsittacus undulatus): absolute thresholds, critical ratios, frequency difference limens, and vocalizations")

    def test_year(self):
        self.assertEqual(a.year, 1975)

#    def test_blah(self):
#        reader = csv.reader(self.csv1, delimiter=',')
#        row1 = next(reader)
#        row1 = next(reader)
#        self.assertIn('[', row1[3])
#        self.assertIn(']', row1[3])

    # only runs if Debug=True
#    def test_successful_requests(self):
    	# tests if status code is 200
#        data = wrapper_call('clarincomhd')
#        self.assertEqual(data['meta']['status'], 200)


    def tearDown(self):
        self.cache.close()
        self.csv_file.close()


class Part3(unittest.TestCase):
    def setUp(self):
        interface(['Parakeet'])
        self.file_list = open(sys.cmd('ls ./static/ > file_list.txt'))

    def test_fig_exists(self):
        self.assertIn('fig1.png', self.file_list.readlines())

    def tearDown(self):
        self.file_list.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)

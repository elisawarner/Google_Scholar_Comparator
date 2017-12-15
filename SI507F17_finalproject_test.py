# least 1 subclass of unittest.TestCase
# at least 5 total test methods (consider what you most need to test!)
# X at least one use of the setUp and tearDown test methods.
# Each of the test methods you write must be good tests (meaning they won't always pass -- or always fail
# they will catch semantic errors -- not just syntax errors).

import unittest
import csv
import os
from SI507F17_finalproject import *

class Part1(unittest.TestCase):
    def setUp(self):
        wrapper_call("Parakeet", 1)
        self.cache = open('cache_file.json')
        self.csv_file = open('./csv_files/PARAKEET.csv')
        self.config_file = open('config.py')

    def test_cache_exists(self):
        self.assertTrue(self.cache.read(), 'No cache found')

    def test_csv_file(self):
        self.assertTrue(self.csv_file.read(), 'No csv found')

    # csv contains rows with 4 columns each
    def test_csv_columns(self):
        # checks first row
        self.assertEqual(len(self.csv_file.readline().split(',')), 7, "Error with csv file length")

    def test_config_exists(self):
        self.assertTrue(self.config_file.read(), 'No config file found')

    def tearDown(self):
        self.cache.close()
        self.csv_file.close()

class Part2(unittest.TestCase):
    def setUp(self):
        self.a = Paper(search_google_scholar('Parakeet')[1], 'Parakeet')
    # csv tags is a list
    def test_title(self):
    	# should return True as a list
        self.assertEqual(self.a.title, "Hearing in the parakeet (Melopsittacus undulatus): absolute thresholds, critical ratios, frequency difference limens, and vocalizations")

    def test_year(self):
        self.assertEqual(self.a.year, '1975')

    def test_journal(self):
        self.assertEqual(self.a.journal, "Journal of Comparative and")

    def test_no_citations(self):
        self.assertEqual(self.a.no_citations, 150)

    def test_repr_method(self):
        self.assertEqual(self.a.__repr__(), self.a.no_citations)

    def test_contains_method(self):
        self.assertTrue("Hearing" in self.a)

    def test_str_method(self):
        self.assertEqual(self.a.__str__(), "Hearing in the parakeet (Melopsittacus undulatus): absolute thresholds, critical ratios, frequency difference limens, and vocalizations by RJ Dooling, JC Saunders")

    def test_params_unique_comb(self):
        # tests if status code is 200
        data = params_unique_combination("https://scholar.google.com/scholar", params_d= {'q':'Amazon'})
        self.assertEqual(data, "https://scholar.google.com/scholarq-Amazon")

    def test_database(self):
        cur.execute("""SELECT COUNT(*) FROM "Publications" """)
        count_entries = cur.fetchall()
        self.assertTrue(int(count_entries[0]['count']) > 0)

    def test_database2(self):
        cur.execute("""SELECT COUNT(*) FROM "Subjects" """)
        count_entries = cur.fetchall()
        self.assertTrue(int(count_entries[0]['count']) > 0)

class Part3(unittest.TestCase):
    def setUp(self):
        interface(['Parakeet'])
        os.system('ls ./static/ > file_list.txt')
        self.file_list = open('file_list.txt')

    def test_fig_exists(self):
        self.assertIn('fig1.png', self.file_list.readlines()[0])

    def tearDown(self):
        self.file_list.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)

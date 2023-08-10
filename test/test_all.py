from locust_plugins import csvreader
from unittest import TestCase


class TestStuff(TestCase):
    def test_csvreader(self):
        reader = csvreader.CSVReader("test/test.csv")
        self.assertListEqual(next(reader), ["column1", "column2"])
        self.assertListEqual(next(reader), ["1.1", "1.2"])

    def test_csvdictreader(self):
        reader = csvreader.CSVDictReader("test/test.csv")
        self.assertDictEqual(next(reader), {"column1": "1.1", "column2": "1.2"})
        self.assertDictEqual(next(reader), {"column1": "2.1", "column2": "2.2"})
        # loop file
        self.assertDictEqual(next(reader), {"column1": "1.1", "column2": "1.2"})

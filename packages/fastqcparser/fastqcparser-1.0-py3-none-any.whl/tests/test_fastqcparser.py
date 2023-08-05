"""
Tests for FastQCParser.
"""

import sys
import unittest
try:
    from StringIO import StringIO
except:
    from io import StringIO


from fastqcparser import FastQCParser, FastqcDataError
import warnings

class TestFastQCParser(object):

    def test_version(self) :
        self.assertTrue(self.p_data.version=='0.10.1')

    def test_modules_exist(self) :
        module_names = ('Basic Statistics',)
        for name in module_names :
            self.assertTrue(name in self.p_data.modules)

    def test_basic_module(self) :
        self.assertEqual(self.p_data['Basic Statistics']['fieldnames'],
            ['Measure','Value']
        )

    def test_addnl_fields(self) :
        self.assertTrue('Sequence Duplication Levels' in self.p_data.modules)
        self.assertTrue('Total Duplicate Percentage' in self.p_data['Sequence Duplication Levels']['addnl'])

    def test_basic_stats(self) :
        self.assertEqual(self.p_data.filename, 'sample1.fastq')
        self.assertEqual(self.p_data.file_type, 'Conventional base calls')
        self.assertEqual(self.p_data.encoding, 'Sanger / Illumina 1.9')
        self.assertEqual(self.p_data.total_sequences, 1571332)
        self.assertEqual(self.p_data.filtered_sequences, 0)
        self.assertEqual(self.p_data.sequence_length, 29)
        self.assertEqual(self.p_data.percent_gc, 53)

    def test_str(self) :
        out = str(self.p_data)
        self.assertTrue(out.startswith('FastQC version: 0.10.1\n'))
        self.assertTrue(out.endswith('%GC: 53'))

class TestFastQCParserTxt(unittest.TestCase, TestFastQCParser) :

    def setUp(self):
        self.p_data = FastQCParser('tests/fastqc_data.txt')

class TestBadFastqcData(unittest.TestCase) :

    def test_empty(self) :
        with self.assertRaises(FastqcDataError) as e :
            FastQCParser('tests/empty.txt')

        self.assertTrue('empty' in e.exception.args[0])

    def test_bad_header(self) :
        with self.assertRaises(FastqcDataError) as e :
            FastQCParser('tests/bad_fastqc_data.txt')

        self.assertTrue('###FastQC' in e.exception.args[0])

    def test_bad_module_header(self) :
        with self.assertRaises(FastqcDataError) as e :
            FastQCParser('tests/bad_fastqc_data_module_header.txt')

        self.assertTrue('Basic Statistics' in e.exception.args[0])

class TestFastQCParserZip(unittest.TestCase, TestFastQCParser) :

    def setUp(self):
        self.p_data = FastQCParser('tests/fastqc.zip')

class TestFastQCParserEmptyZip(unittest.TestCase) :

    def test_fastqc_data_not_found(self):
        with self.assertRaises(FastqcDataError) :
            FastQCParser('tests/empty.zip')

class TestFastQCParserMultipleDataZip(unittest.TestCase) :

    def test_multi_data(self):
        with warnings.catch_warnings(record=True) as w :
            warnings.simplefilter('always')
            FastQCParser('tests/fastqc_multiple.zip')
            self.assertEqual(len(w),1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertTrue('Multiple files' in str(w[-1].message))
            self.assertTrue('Choosing one_fastqc_data.txt' in str(w[-1].message))
            self.assertTrue('Choosing two_fastqc_data.txt' not in str(w[-1].message))

class TestFastQCParserFp(unittest.TestCase, TestFastQCParser) :

    def setUp(self):
        with open('tests/fastqc_data.txt') as fp :
            self.p_data = FastQCParser(fp)

from pprint import pprint
class TestFastQCParserContextMgr(unittest.TestCase, TestFastQCParser) :

    def setUp(self):
        with FastQCParser('tests/fastqc_data.txt') as f :
            self.p_data = f
        pprint(self.p_data['Basic Statistics'])

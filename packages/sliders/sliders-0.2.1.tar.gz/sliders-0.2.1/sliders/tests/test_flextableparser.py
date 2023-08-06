#!/usr/bin/env python

import unittest

from sliders import flextableparser

class TestFlexTableParser(unittest.TestCase):
    
    def test_init_no_args(self):
        parser = flextableparser.FlexTableParser()
        self.assertIsInstance(parser, flextableparser.FlexTableParser)

    def test_init_with_fastqc(self):
        config_file = '../table_schemas/fastqc.json'
        parser = flextableparser.FlexTableParser(config_file)
        self.assertIsInstance(parser, flextableparser.FlexTableParser)

    def test_init_with_flagstat(self):
        config_file = '../table_schemas/flagstat.json'
        parser = flextableparser.FlexTableParser(config_file)
        self.assertIsInstance(parser, flextableparser.FlexTableParser)

if __name__ == '__main__':
    unittest.main()


#!/usr/bin/env python

import unittest

from sliders import text2table

class TestText2Table(unittest.TestCase):
    
    def test_single_input(self):
        inputs=[
                './text2table.py',
                '--schema=fastqc', 
                'sample_fastqc.data']
        text2table.Text2Table(inputs)

    def test_single_input_out(self):
        inputs=[
                './text2table.py',
                '--schema=fastqc',
                '--output-file=test_fastqc.csv', 
                'sample_fastqc.data']
        text2table.Text2Table(inputs)

    def test_multiple_input_files(self):
        inputs=[
                './text2table.py', 
                '--schema=fastqc',
                'sample_fastqc.data',
                'sample_fastqc_2.data']
        text2table.Text2Table(inputs)

    def test_multiple_input_files_static(self):
        inputs=[
                './text2table.py', 
                '--schema=fastqc',
                '--static-values=series=test,sample=A',
                'sample_fastqc.data',
                'sample_fastqc_2.data']
        text2table.Text2Table(inputs)

    def test_static_out(self):
        inputs=[
                './text2table.py',
                '--schema=fastqc',
                '--static-values=series=test,sample=A',
                '--output-file=test_static_fastqc.csv', 
                'sample_fastqc.data']
        text2table.Text2Table(inputs)

if __name__ == '__main__':
    unittest.main()
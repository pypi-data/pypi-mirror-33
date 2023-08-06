#!/usr/bin/env python
"""Command-line tool for converting text2table using FlexTableParser.
"""

__author__ = 'pbilling@stanford.edu (Paul Billing-Ross)'

import sys
import argparse
import unittest
from pkg_resources import resource_filename

from . import flextableparser

RSC_PACKAGE = __name__
BUILT_IN_SCHEMAS = {
                    'fastqc': resource_filename(
                                                RSC_PACKAGE, 
                                                'table_schemas/fastqc.json'),
                    'flagstat': resource_filename(
                                                  RSC_PACKAGE, 
                                                  'table_schemas/flagstat.json'),
                    'vcflib_stats': resource_filename(
                                                      RSC_PACKAGE,
                                                      'table_schemas/vcflib_vcfstats.json'),
                    'vcflib_hethom': resource_filename(
                                                       RSC_PACKAGE,
                                                       'table_schemas/vcflib_vcfhethom.json'),
                    'rtg_vcfstats': resource_filename(
                                                      RSC_PACKAGE,
                                                      'table_schemas/rtg_vcfstats.json')
                   }

class Text2Table():

    def __init__(self, argv):

        # Create table parser
        table_parser = flextableparser.FlexTableParser()

        # Parse command-line arguments
        #print(sys.argv)
        args = self.parse_args(argv[1:])

        # Configure parser with built-in schema or specify custom config file
        if args.schema:
            schema_file = BUILT_IN_SCHEMAS[args.schema]
        elif args.json_file:
            schema_file = args.json_file
        table_parser.configure(schema_file)

        if args.static_values:
            dict_items = (item.split('=') for item in args.static_values.split(','))
            for item in dict_items:
                print(item)
                table_parser.add_static_value(item[0], item[1])

        if args.output_file:
            sys.stdout = open(args.output_file, 'w')

        # Convert input files to table format
        for input_file in args.input_files:  
            table_parser.parse_file(input_file)

    def parse_args(self, argv):

        parser = argparse.ArgumentParser()
        parser.add_argument(
                            "input_files",
                            type = str,
                            nargs = '+',
                            help = 'Input file path')
        parser.add_argument(
                            "-s",
                            "--schema",
                            dest = "schema",
                            type = str,
                            help = "Use built-in table conversion schema",
                            choices = ["fastqc", "flagstat", "vcflib_stats", "vcflib_hethom", "rtg_vcfstats"],
                            required = False)
        parser.add_argument(
                            "-j",
                            "--json-file",
                            dest = "json_file",
                            type = str,
                            help = "Use custom JSON config file with table conversion schema. Only required if not using '-s' option.",
                            required = False)
        parser.add_argument(
                            "-v",
                            "--static-values",
                            dest = "static_values",
                            #nargs = '+',
                            help = "Static values to be added as columns. i.e. '-v=series=test,sample=A'",
                            required = False)
        parser.add_argument(
                            "-o",
                            "--output-file",
                            dest = "output_file",
                            type = str,
                            help = "Output file path",
                            required = False)
        parser.add_argument(
                            "-a",
                            "--append",
                            dest = "append",
                            type = bool,
                            help = "Append instead of write output file",
                            default = False)

        if len(argv) < 2:
            print("No arguments specified")
            parser.print_help()
            sys.exit()
        args = parser.parse_args(argv)
        return(args)

def main():
    Text2Table(sys.argv)

if __name__ == '__main__':
    main()


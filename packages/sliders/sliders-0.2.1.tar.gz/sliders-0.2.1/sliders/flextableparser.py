#!/usr/bin/env python
"""Convert structured text data into table format.

Available functions:
- parse_file: 
"""

__author__ = 'pbilling@stanford.edu (Paul Billing-Ross)'

import re
import pdb
import sys
import json 
import logging 
import datetime

from collections import OrderedDict

def configure_logger(source_type, name=None, file_handle=False):
    # Configure Logger object
    logger = logging.getLogger(source_type)    # Create logger object
    logger.setLevel(logging.DEBUG)

    timestamp = str(datetime.datetime.now()).split()[0]     # yyyy-mm-dd
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Add logging stream handler
    STREAM = logging.StreamHandler(sys.stderr)
    STREAM.setLevel(logging.DEBUG)
    STREAM.setFormatter(formatter)
    logger.addHandler(STREAM)

    return logger

class FlexTableParser:
    """Convert structured text data into CSV format.
    """

    def __init__(self, config_file=None):

        self.config = None
        self.columns = None
        self.dimensions = None
        self.overlap = None
        self.match_patterns = []
        self.static_values = OrderedDict()

        self.logger = configure_logger('FlexTableParser')

        if config_file:
            self.configure(config_file)

    def _write_single_row(self, dimension_name, value):
        """Write single row to table.

        Args:
            dimension (str):
            value (int/float): 

        """

        self.logger.info('Writing single row for dimension: {}'.format(dimension_name))
        index = ''  # Fixed at 1 when writing single row
        
        # Combine line-entry values with static values
        table_values = {
                        'dimension': dimension_name,
                        'index': index,
                        'value': value
                       }
        static_values = self.static_values.copy()
        table_values.update(static_values)

        # Populate output string ordered by columns
        strings = [str(table_values[column]) for column in self.columns]
        out_str = ','.join(strings)
        # self.out_fh.write(out_str)
        print(out_str)

    def _write_series_rows(self, dimension, in_fh):
        """Write series of rows.
        """

        dimension_name = dimension['name']
        self.logger.info('Writing series of rows for dimension: {}'.format(dimension_name))
        # Indexes of the delimiter separated line.
        # (I know, I know... need better terminology.)
        index_element = dimension['index']  # type: int
        value_element = dimension['value']  # type: int

        delimiter = dimension['delimiter'] # type: str
        if not delimiter:
            delimiter = None
        stop_pattern = dimension['stop_pattern'] # type: str

        stop = False

        while stop == False:
            table_values = self.static_values.copy()
            line = in_fh.readline()
            #pdb.set_trace()
            stop_match = re.match(stop_pattern, line)
            if stop_match:
                stop = True
            else:
                elements = line.split(delimiter)
                #self.logger.info(elements)
                table_values['dimension'] = dimension['name']
                table_values['index'] = elements[index_element]
                table_values['value'] = elements[value_element]

                # Convert all values to column ordered strings
                strings = [str(table_values[column]) for column in self.columns]
                out_str = ','.join(strings)
                #self.out_fh.write(out_str)
                print(out_str)

    def _parse_match(self, match, in_fh):
        """Parse single line pattern match.
        """
        dimension_name = list(match.groupdict().keys())[0]
        row_type = self.dimensions[dimension_name]['row_type']
        if row_type == 'single':
            value = list(match.groupdict().values())[0]
            self._write_single_row(dimension_name, value)
        elif row_type == 'series':
            dimension = self.dimensions[dimension_name]
            self._write_series_rows(dimension, in_fh)
        else:
            self.logger.error('Invalid dimension type: {}'.format(dimension_type))
            pdb.set_trace()

    def configure(self, config_file):
        """Get parsing schema from JSON file.
        """

        self.logger.info("Configuring FlexTableParser using JSON file: {}".format(config_file))
        with open(config_file, 'r') as config_fh:
            self.config = json.load(config_fh)
        self.columns = self.config['columns']
        self.dimensions = self.config['dimensions']
        self.overlap = bool(self.config['overlap'])

        self.match_patterns = []
        for dimension_name in self.dimensions:
            dimension = self.dimensions[dimension_name]
            regex_pattern = dimension['regex_pattern']
            self.match_patterns.append(regex_pattern)

    def add_static_value(self, key, value):
        """Specify static table column values.
        """
        
        self.static_values.update({key:value})
        self.columns.append(key)

        self.logger.info('Added static values: {}'.format(self.static_values))
        self.logger.info('Updated column list: {}'.format(self.columns))

    def parse_file(self, in_file):
        """Parse file.
        """
        with open(in_file, 'r') as in_fh:
            self.logger.info('Parsing file: {}'.format(in_file))
            while in_fh:
                line = in_fh.readline()
                if not line:
                    self.logger.info('End of file: {}\n'.format(in_file))
                    break
                # Dev: what does this return
                matches = [re.match(regex, line) for regex in self.match_patterns]
                #true_matches = list(ifilter(lambda x: x > 0, matches))
                true_matches = [x for x in matches if x != None]
                filter 
                if len(true_matches) == 0:
                    continue
                elif len(true_matches) > 1:
                    self.logger.warning('Multiple regex patterns matched this line.')
                    self.logger.warning(line.strip())

                    if self.overlap:
                        # Potential for error if you have overlapping matches 
                        # & and is a series
                        for match in true_matches:
                            self._parse_match(match, in_fh)
                    else:
                        self.logger.error('Error: Configuration file does not allow for overlapping patterns')
                        sys.exit()

                elif len(true_matches) == 1:
                    self.logger.info('Found single match for line: ')
                    self.logger.info(line.strip())
                    self._parse_match(true_matches[0], in_fh)
                        
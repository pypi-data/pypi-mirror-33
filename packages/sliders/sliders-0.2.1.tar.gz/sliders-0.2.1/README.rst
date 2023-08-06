Sliders
-------

### Installation:

    $ pip install sliders

## text2table 

### Description:
Command-line tool to convert structured text data into CSV format. Currently includes built-in support for fastqc and samtools flagstat files. You can also provide a custom JSON file with instructions for parsing your text files. Text2table is a front-end tool for using the flextableparser python module.

### Usage:
    # Convert a fastqc file into CSV format
    $ text2table --schema=fastqc fastqc.data
    # Write parsed CSV data to a file (1)
    $ text2table --schema=fastqc fastqc.data 2>&1 > fastqc.csv
    # Write parsed CSV data to a file (2)
    $ text2table --schema=fastqc --output_file=out.csv fastqc.data
    # Parse multiple input files
    $ text2table --schema=fastqc 1_fastqc.data 2_fastqc.data
    # Provide static values to be added as columns
    $ text2table --schema=fastqc --output_file=out.csv --static_values=series=test,sample=A fastqc.data
    # For debugging, only write log messages to the console
    $ text2table --schema=fastqc 1_fastqc.data 2_fastqc.data 2>&1 >/dev/null

## flextableparser

### Description:
Python module for converting structred text data to CSV format.

### Usage:
    >>> from sliders import flextableparser
    >>> parser = flextableparser.FlexTableParser()
    >>> parser.configure(json_file)
    >>> parser.add_static_value(key, value)
    >>> parser.parse_file(input_file)
    >>> output = parser.parse_file(input_file)
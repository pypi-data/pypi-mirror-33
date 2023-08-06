#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert numpy text files to binary format.

Binary files are about 20 percent smaller in size and opens far more
quickly than text files when using numpy. This is useful when using
parallelization of tasks, every one of which has to open input data.

Jean-Baptiste Bayle, APC/CNRS/CNES, 28/06/2018.
"""

import os
import argparse
import numpy


def parse_command_line():
    """Build argument parser and parse command line.

    Returns:
        (namespace) Namespace containing parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description='Convert numpy text file to binary format.',
        epilog="Jean-Baptiste Bayle, APC/CNRS/CNES.")
    parser.add_argument('inputs',
                        nargs='+',
                        help='input text files')
    parser.add_argument('-o', '--output',
                        nargs='*',
                        dest='outputs',
                        help='output binary files')
    parser.add_argument('-r', '--reverse',
                        action='store_true',
                        help='convert a binary file into a text file')
    parser.add_argument('-d', '--delete',
                        action='store_true',
                        help='remove input files once they are converted')
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_command_line()

    # Check that `--output` is not given or has the same length as `inputs`
    if args.outputs is not None and len(args.outputs) != len(args.inputs):
        raise ValueError('Please provide enough output files or none.')

    # Loop on the input files
    for index, file in enumerate(args.inputs):

        # Read input file
        if not args.reverse:
            print('Opening text file ' + file + '...')
            data = numpy.loadtxt(file)
        else:
            print('Opening binary file ' + file + '...')
            data = numpy.load(file, mmap_mode='r')

        # Use default output name if not specified
        if args.outputs is None:
            output = os.path.splitext(file)[0]

        # Otherwise use user-specified
        else:
            output = args.outputs[index]

        # Write output files
        if not args.reverse:
            print('Saving binary file as ' + output + '...')
            numpy.save(output, data)
        else:
            print('Saving text file as ' + output + '...')
            numpy.savetxt(output, data)

        # Remove input file if required
        if args.delete:
            print('Deleting original file ' + file + '...')
            os.remove(file)


if __name__ == '__main__':
    main()

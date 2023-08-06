#!/usr/bin/env python

import argparse
import csv
import logging.config
import os

from bioutils.settings import LOGGING_CONFIG
from bioutils import PACKAGE_NAME

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(PACKAGE_NAME + '.' + os.path.basename(__file__))


def get_options():
    parser = argparse.ArgumentParser(description='Create a CSV containing some meta-data for each sample')
    parser.add_argument('--input-dir', required=True, help='input directory of the samples')
    parser.add_argument('--output-dir', required=True, help='output directory for the CSV')
    args = parser.parse_args()
    return args


def main():
    args = get_options()
    output_dir = os.path.abspath(args.output_dir)
    input_dir = os.path.abspath(args.input_dir)
    # get sub directories
    samples = sorted([[o,os.path.join(input_dir,o)] for o in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir,o))])
    logger.info('samples list:' + str(samples))
    with open(os.path.join(output_dir, 'samples.csv'), 'w') as output_csv:
        writer = csv.writer(output_csv, delimiter=',')
        writer.writerow(['sample', 'path'])
        for row in samples:
            if row[0].lower().startswith('sample_'):
                row[0] = row[0][len('sample_'):]
            writer.writerow(row)

if __name__ == '__main__':
    main()

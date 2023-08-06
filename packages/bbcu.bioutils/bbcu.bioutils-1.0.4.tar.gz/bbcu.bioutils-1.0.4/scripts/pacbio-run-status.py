#!/usr/bin/env python

from bioutils.pacbio.primary_files import PrimaryFiles
from bioutils.pacbio.settings import PRIMARY_DIR
import argparse

def get_options():
    parser = argparse.ArgumentParser(description='Run the fastqcTaxonomy pipeline')
    parser.add_argument('--root-dir', type=str, required=False, default=PRIMARY_DIR, help='Path root direcroty of PacBio raw data')
    parser.add_argument('--run-name', type=str, required=True, help='Name of the run, for example: r54109_20161115_072823')
    parser.add_argument('--cell-name', type=str, required=True, help='Name of the cell. for example: 1_A01')
    args = parser.parse_args()
    return args

def main():
    args = get_options()
    pf = PrimaryFiles(**vars(args))
    if pf.data_transfered():
        print "The run %s cell %s is ended" %(args.run_name, args.cell_name)
    else:
        print "The run %s cell %s is don't ended yet" %(args.run_name, args.cell_name)

if __name__ == "__main__":
    main()

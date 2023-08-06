#!/usr/bin/env python

from bioutils.tax_db.tables import UpdateTables
from bioutils.tax_db.settings import GI_2_TAXID_FILE, NAMES_FILE, NODES_FILE, DB, FLUSH_SIZE
import argparse

CREATE_DB = 'create'
UPDATE_DB = 'update'

def get_options():
    parser = argparse.ArgumentParser(description='Run the fastqcTaxonomy pipeline')
    parser.add_argument('--gi2taxid_file', type=str, default=GI_2_TAXID_FILE, help='Path to gi_taxid_nucl.dmp file')
    parser.add_argument('--names_file', type=str, default=NAMES_FILE, help='Path to name.dmp file')
    parser.add_argument('--nodes_file', type=str, default=NODES_FILE, help='True or nodes.dmp file')
    parser.add_argument('--flush_size', type=int, default=FLUSH_SIZE, help='Update DB with this number of records '
                                                                           '(for memory usage)')
    parser.add_argument('--db', type=str, default=DB, help='Database URL, For example see in settings.py file')
    parser.add_argument('--action', required=True, type=str, choices=[CREATE_DB, UPDATE_DB],
                        help='Create a new DB or update exists DB')
    args = parser.parse_args()
    return args

def main():
    args = get_options()
    args.create = True if args.action == CREATE_DB else False
    del args.action
    UpdateTables(**vars(args)).update_db()

if __name__ == "__main__":
    main()

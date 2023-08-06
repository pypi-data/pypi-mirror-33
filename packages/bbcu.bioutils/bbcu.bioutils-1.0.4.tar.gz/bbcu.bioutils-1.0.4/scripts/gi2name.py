#!/usr/bin/env python

from bioutils.tax_db.tables import Query
from bioutils.tax_db.settings import DB
from bioutils.tax_db.db_session import Session
import argparse

CREATE_DB = 'create'
UPDATE_DB = 'update'

def get_names(db, gi_list):
    with Session(db, 60) as db_session:
        query = Query(db_session)
        for gi in gi_list:
            name = query.gi2name(gi)
            print 'Scientific name of gi number %s is %s' %(gi, name)

def get_options():
    parser = argparse.ArgumentParser(description='Run the fastqcTaxonomy pipeline')
    parser.add_argument('--db', type=str, default=DB, help='Database URL, For example see in settings.py file')
    parser.add_argument('--gi-list', default=None, type=int, nargs='+',
                        help='Space-separated list of GeneBank numbers (gi)')

    args = parser.parse_args()
    return args

def main():
    args = get_options()
    get_names(args.db, args.gi_list)


if __name__ == "__main__":
    main()


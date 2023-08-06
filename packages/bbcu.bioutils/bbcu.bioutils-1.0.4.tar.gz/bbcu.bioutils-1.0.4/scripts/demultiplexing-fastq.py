#!/usr/bin/env python

from bioutils.barcodes.demultiplexing import Demultiplexing 
import argparse


def get_options():
    p = argparse.ArgumentParser(description='Run demultiplexing on fastq files')
    p.add_argument('--barcodes', '-b', action='store', required=True, help="barcodes file")
    p.add_argument('--fastq1', '-1', action='store', required=True, help="fastq file with barcode in header", default="f")
    p.add_argument('--fastq2', '-2', action='store', help="second fastq file with barcode in header", default="none")
    p.add_argument('--fastq3', '-3', action='store', help="third fastq file with barcode in header", default="none")
    p.add_argument('--threshold1', '-t', action='store', help='Hamming distance threshold1', default=2, type=int)
    p.add_argument('--threshold2', '-m', action='store', help='Hamming distance threshold2', default=2, type=int)
    p.add_argument('--outdir', '-o', action='store', required=True, help='Output directory', default=".")
    p.add_argument('--notrim', '-n', action='store_true', help="Dont trim reads")
    p.add_argument('--add2header', '-a', action='store_true', default=False,
                 help="Add barcodes to header (influences only at rd mode)")
    p.add_argument('--no-out-read', required=False, default=False, help="No output the index read (1, 2 or 3)")
    p.add_argument('--queue-out', required=False, default=100000, help="After how much input reads to print out the queues to files")

    return p.parse_args()

def main():
    args = get_options()
    Demultiplexing(args.barcodes, args.outdir, args.fastq1, args.fastq2, args.fastq3, args.threshold1,
                   args.threshold2, args.notrim, args.add2header, args.no_out_read, args.queue_out).run_demultiplexing()


if __name__ == "__main__":
    main()

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

def convert_sequence_to_fasta_sequence(str_sequence, id, **kwargs):
    bio_seq = Seq(str_sequence)
    return SeqRecord(bio_seq, id=id, **kwargs)

def write_fasta(seq_records, fasta_output_file_handle):
    SeqIO.write(seq_records, fasta_output_file_handle, "fasta")

import StringIO
import abc
import csv
import json
import logging
import re

import pandas
from bioutils.seqio.fasta import convert_sequence_to_fasta_sequence, write_fasta
from bioutils.fastqc.data import SequenceLengthDistributionCount, OverrepresentedSequence

logger = logging.getLogger(__name__)

MODULE_HEADER_REGEXP = re.compile('^>>(?P<module_name>.+)\\t(?P<module_result>pass|fail|warn)$')
MODULE_END_REGEXP = re.compile('^>>END_MODULE$')

PASS = 'pass'
WARN = 'warn'
FAILED = 'fail'


class ModuleOutputReader(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, lines):
        self.lines = lines

    def fail(self, reason):
        logger.error('[%s]: failure, reason: [%s]' % (self.__class__.__name__, reason))
        self.status = FAILED
        self.reasons.append(reason)

    @abc.abstractmethod
    def do_read(self):
        pass

    def read(self):
        try:
            return self.do_read()
        except Exception, exc:
            error_message = '[%s]: error reading module output. Reason: [%s]' % (self.__class__.__name__, exc.message)
            logger.error(error_message)
            raise


class ModuleOutput(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def do_save(self, *args, **kwargs):
        pass

    def save(self, *args, **kwargs):
        try:
            return self.do_save(*args, **kwargs)
        except Exception, exc:
            error_message = '[%s]: error saving module output. Reason: [%s]' % (self.__class__.__name__, exc.message)
            logger.error(error_message)
            raise


class DummyReader(ModuleOutputReader):
    def do_read(self):
        pass


class DataFrameModuleOutput(ModuleOutput):
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def do_save(self, csv_output_file_handle):
        self.dataframe.to_csv(csv_output_file_handle)


class SequenceLengthDistribution(ModuleOutput):
    def __init__(self, counts):
        self.counts = counts

    def do_save(self, json_output_file_handle, csv_output_file_handle):
        json.dump(self.counts, json_output_file_handle, default=lambda o: o.__dict__, sort_keys=True)
        csv_writer = csv.DictWriter(csv_output_file_handle, fieldnames=('from_length', 'to_length', 'count'),
                                    delimiter=',')
        csv_writer.writeheader()
        csv_writer.writerows([count.__dict__ for count in self.counts])


class SequenceLengthDistributionReader(ModuleOutputReader):
    def do_read(self):
        sequence_length_distribution_counts = []
        csv_in_memory_file = StringIO.StringIO('\n'.join(self.lines))
        csv_reader = csv.reader(csv_in_memory_file, delimiter='\t')
        headers = next(csv_reader, None)
        if tuple(headers) != ('#Length', 'Count'):
            self.fail(reason='Unexpected headers: [%s]' % headers)
            return
        for row in csv_reader:
            logger.debug('Row: %s' % row)
            sequence_length_distribution_counts.append(SequenceLengthDistributionCount.from_raw_count(*row))
        return SequenceLengthDistribution(sequence_length_distribution_counts)


class OverrepresentedSequences(ModuleOutput):
    def __init__(self, sequences, threshold=1.0):
        self.sequences = sequences
        self.threshold = threshold

    def do_save(self, fasta_output_file_handle, csv_output_file_handle):
        if self.sequences and self.sequences[0].percentage is not None:
            top_sequences = [sequence for sequence in self.sequences if sequence.percentage >= self.threshold]
        else:
            top_sequences = self.sequences
        fasta_sequences = []
        csv_rows = []
        for (i, overrepresented_sequence) in enumerate(top_sequences):
            sequence_id = str(i+1)
            fasta_sequences.append(
                convert_sequence_to_fasta_sequence(overrepresented_sequence.sequence, id=sequence_id))
            # in case we don't want a CSV output
            if csv_output_file_handle:
                csv_rows.append(dict(id=sequence_id, sequence=overrepresented_sequence.sequence,
                                     length=overrepresented_sequence.length,
                                     count=overrepresented_sequence.count,
                                     percentage=overrepresented_sequence.percentage))
        write_fasta(fasta_sequences, fasta_output_file_handle)
        # in case we don't want a CSV output
        if csv_output_file_handle:
            csv_writer = csv.DictWriter(csv_output_file_handle,
                                        fieldnames=('id', 'sequence', 'length', 'count', 'percentage'), delimiter=',')
            csv_writer.writeheader()
            csv_writer.writerows(csv_rows)


class OverrepresentedSequencesReader(ModuleOutputReader):
    def do_read(self):
        overrepresented_sequences = []
        csv_in_memory_file = StringIO.StringIO('\n'.join(self.lines))
        csv_reader = csv.reader(csv_in_memory_file, delimiter='\t')
        headers = next(csv_reader, None)
        if tuple(headers) != ('#Sequence', 'Count', 'Percentage', 'Possible Source'):
            self.fail(reason='Unexpected headers: [%s]' % headers)
            return
        for row in csv_reader:
            if len(row) != 4:  # each row should contain 4 fields
                logger.warn('Illegal row skipped: %s' % row)  # TODO: find why this is
            else:  # legal row
                logger.debug('Row: %s' % row)
                overrepresented_sequences.append(OverrepresentedSequence.from_fastqc_output(*row))
        return OverrepresentedSequences(overrepresented_sequences, 1.0)


class BasicStatistics(ModuleOutput):
    def __init__(self, stats_dict):
        self.reads_pf = int(stats_dict['Total Sequences'])
        #TODO add more features?
    def do_save():
        pass

class BasicStatisticsReader(ModuleOutputReader):
    def do_read(self):
        stats_dict = {}   
        csv_in_memory_file = StringIO.StringIO('\n'.join(self.lines))
        csv_reader = csv.reader(csv_in_memory_file, delimiter='\t')
        headers = next(csv_reader, None)
        if tuple(headers) != ('#Measure', 'Value'):
            self.fail(reason='Unexpected headers: [%s]' % headers)
            return
        for row in csv_reader:
            stats_dict[row[0]] = row[1]
        logger.debug('Stats Dict: ' + str(stats_dict))
        return BasicStatistics(stats_dict)


class PerBaseSequenceQuality(DataFrameModuleOutput):
    def __init__(self, dataframe):
        super(PerBaseSequenceQuality, self).__init__(dataframe)
        self.means = self.dataframe['Mean']
        self.bases = self.dataframe['#Base']


class PerBaseSequenceQualityReader(ModuleOutputReader):
    def do_read(self):
        csv_in_memory_file = StringIO.StringIO('\n'.join(self.lines))
        dataframe = pandas.read_csv(csv_in_memory_file, delimiter='\t')
        return PerBaseSequenceQuality(dataframe)


class PerSequenceQualityScores(DataFrameModuleOutput):
    def __init__(self, dataframe):
        super(PerSequenceQualityScores, self).__init__(dataframe)
        self.mean_q_score = sum(self.dataframe['Count'] * self.dataframe['#Quality'])/sum(self.dataframe['Count'])
        self.p_over_q_30 = 100 * sum(self.dataframe['Count'].loc[self.dataframe['#Quality'] >= 30]) / sum(
            self.dataframe['Count'])
        self.count = sum(self.dataframe['Count'])

class PerSequenceQualityScoresReader(ModuleOutputReader):
    def do_read(self):
        csv_in_memory_file = StringIO.StringIO('\n'.join(self.lines))
        dataframe = pandas.read_csv(csv_in_memory_file, delimiter='\t')
        return PerSequenceQualityScores(dataframe)


class FastQcOutputReadException(Exception):
    pass


class FastQcOutputReader(object):
    """
    Reader of a fastqc output file which includes the output of each QC module.
    The file is named fastqc_data.txt by default
    """

    def __init__(self, fastqc_output_file_handle):
        self.fastqc_output_file_handle = fastqc_output_file_handle
        self.file_lines = [line.strip() for line in self.fastqc_output_file_handle]
        self.basic_statistics_reader_output = None
        self.per_base_sequence_quality_reader_output = None
        self.per_sequence_quality_scores_reader_output = None
        self.sequence_length_distribution_reader_output = None
        self.overrepresented_sequences_reader_output = None

    def log_error(self, error_message):
        detailed_error_message = 'Output file handle [%s]: Error reading FastQC output from file handle. Reason: [%s]' \
                                 % (self.fastqc_output_file_handle, error_message)
        logger.error(detailed_error_message)

    def read_header(self, header_line):
        if not header_line.startswith('##FastQC'):
            raise FastQcOutputReadException('first line should start with "##FastQC"')
        self.file_version = header_line.split('\t')[1]
        logger.debug('File version: %s' % self.file_version)

    def read_module_output(self, module_name, module_lines):
        if module_name == 'Basic Statistics':
            self.basic_statistics_reader_output = BasicStatisticsReader(module_lines).read()            
        elif module_name == 'Per tile sequence quality':
            pass
        elif module_name == 'Per base sequence quality':
            self.per_base_sequence_quality_reader_output = PerBaseSequenceQualityReader(module_lines).read()
        elif module_name == 'Per sequence quality scores':
            self.per_sequence_quality_scores_reader_output = PerSequenceQualityScoresReader(module_lines).read()
        elif module_name == 'Per base sequence content':
            pass
        elif module_name == 'Per base GC content':
            pass
        elif module_name == 'Per sequence GC content':
            pass
        elif module_name == 'Per base N content':
            pass
        elif module_name == 'Sequence Length Distribution':
            self.sequence_length_distribution_reader_output = SequenceLengthDistributionReader(module_lines).read()
        elif module_name == 'Sequence Duplication Levels':
            pass
        elif module_name == 'Overrepresented sequences':
            self.overrepresented_sequences_reader_output = OverrepresentedSequencesReader(module_lines).read()
        elif module_name == 'Kmer Content':
            pass
        else:
            error_message = 'Unknown module [%s]' % module_name
            logger.warn(error_message)  # OAOA TODO: explicitly add all FastQC new modules (Adapter Content, etc.)
#             self.log_error(error_message)
#             raise FastQcOutputReadException(error_message)

    def read(self):
        try:
            self.read_header(self.file_lines[0])
            i = 1
            while i < len(self.file_lines):
                line = self.file_lines[i]
                module_start_match = MODULE_HEADER_REGEXP.match(line)
                assert module_start_match, 'Line [%s] - improper module input start' % line
                module_name = module_start_match.group('module_name')
                for j in range(i+1, len(self.file_lines)):
                    line = self.file_lines[j]
                    if MODULE_END_REGEXP.match(line):
                        break
                assert j < len(self.file_lines), 'Could not find end of output for module [%s]' % module_name
                if j == i+1:
                    logger.info('Empty output for module [%s]' % module_name)
                else:
                    module_lines = self.file_lines[i+1:j]
                    self.read_module_output(module_name, module_lines)
                i = j+1
        except Exception, e:
            self.log_error(str(e))
            raise e

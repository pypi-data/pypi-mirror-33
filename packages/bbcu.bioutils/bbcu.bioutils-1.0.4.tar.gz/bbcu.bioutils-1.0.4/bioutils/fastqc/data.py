class SequenceLengthDistributionCount(object):
    def __init__(self, from_length, to_length, count):
        self.from_length = from_length
        self.to_length = to_length
        self.count = count

    @classmethod
    def from_raw_count(cls, length, count):
        if '-' in length:
            from_length, to_length = [int(n) for n in length.split('-')]
        else:
            from_length = to_length = int(length)
        count = float(count)
        return cls(from_length, to_length, count)

class OverrepresentedSequence(object):
    def __init__(self, sequence, count, percentage, possible_source):
        self.sequence = sequence
        self.length = len(sequence)
        self.count = count
        self.percentage = percentage
        self.possible_source = possible_source

    @classmethod
    def from_fastqc_output(cls, sequence, count, percentage, possible_source):
        if(percentage!=None):
            percentage = float(percentage)
        return cls(sequence, int(count), percentage, possible_source)

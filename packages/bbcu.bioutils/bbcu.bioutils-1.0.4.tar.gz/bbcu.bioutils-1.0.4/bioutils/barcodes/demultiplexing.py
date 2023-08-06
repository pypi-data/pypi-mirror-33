import argparse
import gzip
import os

class Demultiplexing(object):
    def __init__(self, barcodes_file, outdir, fastq1, fastq2=None, fastq3=None, threshold1=2, threshold2=2, notrim=True,
                 add2header=False, no_out_read=False, queue_out=100000):
        self.barcodes_file = barcodes_file
        self.outdir = outdir
        self.fastq1 = fastq1
        self.fastq2 = fastq2
        self.fastq3 = fastq3
        self.threshold1 = threshold1
        self.threshold2 = threshold2
        self.notrim = notrim
        self.add2header = add2header
        self.no_out_read = int(no_out_read)
        self.queue_out = int(queue_out)
        self.queues = {}
        self.Barcodes, self.barcode_format, self.Samples = self.readBarcodesFile(self.barcodes_file)
        self.create_samples_folders()

    def create_samples_folders(self):
        for samp in self.Samples+['Undetermined']:
            folder_name = os.path.join(self.outdir, samp)
            os.system('mkdir -p %s' %folder_name)

    def run_demultiplexing(self):
        self.demultiplex()

    def readBarcodesFile(self, filename):
        # position:length:skip
        # position = 5, 3, ind1 or ind2
        # length   = length of barcode to check
        # skip = to skip N characters (if empty not skipping)
        Barcodes = {}
        f = open(filename)

        # read header
        line = f.readline()
        tmp = line.split(' ')
        barcode_format = []
        for i in tmp:
            barcode_format.append(i.split(':'))
            barcode_format[-1][1] = int(barcode_format[-1][1])
            if len(barcode_format[-1]) == 2:
                barcode_format[-1].append(0)
            else:
                barcode_format[-1][2] = int(barcode_format[-1][2])

        Samples = []
        for line in f:
            tmp = line.split(' ')
            cnt = 1
            for n in barcode_format:
                if (len(barcode_format) == 1):
                    Barcodes[tmp[cnt].rstrip()] = tmp[0]
                    Samples.append(tmp[0])
                elif (cnt == 1):
                    if (not Barcodes.has_key(tmp[cnt].rstrip())):
                        Barcodes[tmp[cnt].rstrip()] = {}
                else:
                    Barcodes[tmp[cnt - 1].rstrip()][tmp[cnt].rstrip()] = tmp[0]
                    Samples.append(tmp[0])
                cnt = cnt + 1

        Samples.append('Undetermined')
        return Barcodes, barcode_format, Samples

    def calcDistance(self, seq, barcodes):
        min_dist = 100
        second_best = 100
        barcode = ''
        for b in barcodes.keys():
            dist = sum([1 if seq[i] != b[i] else 0 for i in range(len(seq))])
            if min_dist >= dist:
                second_best = min_dist
                min_dist = dist
                barcode = b

        if (second_best == min_dist):
            min_dist = 100

        return (barcodes[barcode], barcode, min_dist)

    def out_name(self, sample, in_file):
        if '_R1' in in_file:
            return os.path.join(sample, sample + '_R1.fastq')
        if '_R2' in in_file:
            return os.path.join(sample, sample + '_R2.fastq')
        if '_R3' in in_file:
            return os.path.join(sample, sample + '_R3.fastq')
        if '_R4' in in_file:
            return os.path.join(sample, sample + '_R4.fastq')
        if '_I1' in in_file:
            return os.path.join(sample, sample + '_I1.fastq')
        if '_I2' in in_file:
            return os.path.join(sample, sample + '_I2.fastq')

    def demultiplex(self):
        files = {}
        r2 = 0
        r3 = 0
        files2 = {}
        files3 = {}
        counts = {}
        for v in self.Samples:
            counts[v] = 0
            if self.no_out_read == 1 and v != 'Undetermined':
                files[v] = ''
                continue
            tmp = self.fastq1.split("/")
            if (len(tmp) > 0):
                files[v] = open(self.outdir + "/" + self.out_name(v, tmp[-1]), 'w')
            else:
                files[v] = open(self.outdir + "/" + self.out_name(v, self.fastq1), 'w')


        if (self.fastq1[-3:] == '.gz'):
            f = gzip.open(self.fastq1, 'r')
        else:
            f = open(self.fastq1)

        if (self.fastq2 != "none"):
            r2 = 1
            if (self.fastq2[-3:] == '.gz'):
                f2 = gzip.open(self.fastq2, 'r')
            else:
                f2 = open(self.fastq2)

            for v in self.Samples:
                if self.no_out_read == 2 and v != 'Undetermined':
                    files2[v] = ''
                    continue
                tmp = self.fastq2.split("/")
                if (len(tmp) > 0):
                    files2[v] = open(self.outdir + "/" + self.out_name(v, tmp[-1]), 'w')
                else:
                    files2[v] = open(self.outdir + "/" + self.out_name(v, self.fastq2), 'w')
        if (self.fastq3 != "none"):
            r3 = 1
            if (self.fastq3[-3:] == '.gz'):
                f3 = gzip.open(self.fastq3, 'r')
            else:
                f3 = open(self.fastq3)

            for v in self.Samples:
                if self.no_out_read == 3 and v != 'Undetermined':
                    files3[v] = ''
                    continue
                tmp = self.fastq3.split("/")
                if (len(tmp) > 0):
                    files3[v] = open(self.outdir + "/" + self.out_name(v, tmp[-1]), 'w')
                else:
                    files3[v] = open(self.outdir + "/" + self.out_name(v, self.fastq3), 'w')
        index = 0
        lines = ['', '', '', '']
        lines2 = ['', '', '', '']
        lines3 = ['', '', '', '']
        # line 0 is the id1 id2
        # line 1 is the read
        barcode1 = ''
        barcode2 = ''
        while True:
            line = f.readline()
            if (not line):
                break
            if (r2 == 1):
                line2 = f2.readline()
            if (r3 == 1):
                line3 = f3.readline()

            if (index % 4 == 0):
                if (line[0] != '@'):
                    continue

                if (self.barcode_format[0][0] == 'id1'):
                    l = self.barcode_format[0][1]
                    sk = self.barcode_format[0][2]
                    b = line.split(':')[-1]
                    barcode1 = b[sk:sk + l]
                elif (self.barcode_format[0][0] == 'id2'):
                    l = self.barcode_format[1][1]
                    sk = self.barcode_format[1][2]
                    b = line.split(':')[-1]
                    b = b.split('+')[-1]
                    barcode1 = b[sk:sk + l]
                if (len(self.barcode_format) == 2 and self.barcode_format[1][0] == 'id1'):
                    l = self.barcode_format[0][1]
                    sk = self.barcode_format[0][2]
                    b = line.split(':')[-1]
                    barcode2 = b[sk:sk + l]
                elif (len(self.barcode_format) == 2 and self.barcode_format[1][0] == 'id2'):
                    l = self.barcode_format[1][1]
                    sk = self.barcode_format[1][2]
                    b = line.split(':')[-1]
                    b = b.split('+')[-1]
                    barcode2 = b[sk:sk + l]

                lines[0] = line
                if (r2 == 1):
                    lines2[0] = line2
                if (r3 == 1):
                    lines3[0] = line3
            else:
                if (index % 4 == 1):
                    if (self.barcode_format[0][0] == 'rd1'):
                        l = self.barcode_format[0][1]
                        sk = self.barcode_format[0][2]
                        barcode1 = line[sk:sk + l]
                        if (not self.notrim):
                            line = line[sk + l:]
                        if (self.add2header):
                            lines[0].replace(":0:0", ":0:" + barcode1)
                            if (r2 == 1):
                                lines2[0].replace(":0:0", ":0:" + barcode1)
                            if (r3 == 1):
                                lines3[0].replace(":0:0", ":0:" + barcode1)
                    elif (self.barcode_format[0][0] == 'rd2' and r2 == 1):
                        l = self.barcode_format[0][1]
                        sk = self.barcode_format[0][2]
                        barcode1 = line2[sk:sk + l]
                        if (not self.notrim):
                            line2 = line2[sk + l:]
                        if (self.add2header):
                            lines[0] = lines[0].replace(":0:0", ":0:" + barcode1)
                            if (r2 == 1):
                                lines2[0] = lines2[0].replace(":0:0", ":0:" + barcode1)
                            if (r3 == 1):
                                lines3[0] = lines3[0].replace(":0:0", ":0:" + barcode1)
                    if (len(self.barcode_format) == 2 and self.barcode_format[1][0] == 'rd1'):
                        l = self.barcode_format[1][1]
                        sk = self.barcode_format[1][2]
                        barcode2 = line[sk:sk + l]
                        if (not self.notrim):
                            line = line[sk + l:]
                        if (self.add2header):
                            lines[0] += "+" + barcode2
                            if (r2 == 1):
                                lines2[0] += "+" + barcode2
                            if (r3 == 1):
                                lines3[0] += "+" + barcode2
                    elif (len(self.barcode_format) == 2 and self.barcode_format[1][0] == 'rd2' and r2 == 1):
                        l = self.barcode_format[1][1]
                        sk = self.barcode_format[1][2]
                        barcode2 = line2[sk:sk + l]
                        if (not self.notrim):
                            line2 = line2[sk + l:]
                        if (self.add2header):
                            lines[0] += "+" + barcode2
                            if (r2 == 1):
                                lines2[0] += "+" + barcode2
                            if (r3 == 1):
                                lines3[0] += "+" + barcode2

                    lines[index % 4] = line
                    if (r2 == 1):
                        lines2[index % 4] = line2
                    if (r3 == 1):
                        lines3[index % 4] = line3
                if (index % 4 == 2):
                    lines[index % 4] = line
                    if (r2 == 1):
                        lines2[index % 4] = line2
                    if (r3 == 1):
                        lines3[index % 4] = line3
                if (index % 4 == 3):
                    if (self.barcode_format[0][0] == 'rd1'):
                        l = self.barcode_format[0][1]
                        sk = self.barcode_format[0][2]
                        if (not self.notrim):
                            line = line[sk + l:]
                    elif (self.barcode_format[0][0] == 'rd2' and r2 == 1):
                        l = self.barcode_format[0][1]
                        sk = self.barcode_format[0][2]
                        if (not self.notrim):
                            line2 = line2[sk + l:]
                    if (len(self.barcode_format) == 2 and self.barcode_format[1][0] == 'rd1'):
                        l = self.barcode_format[1][1]
                        sk = self.barcode_format[1][2]
                        if (not self.notrim):
                            line = line[sk + l:]
                    elif (len(self.barcode_format) == 2 and self.barcode_format[1][0] == 'rd2' and r2 == 1):
                        l = self.barcode_format[1][1]
                        sk = self.barcode_format[1][2]
                        if (not self.notrim):
                            line2 = line2[sk + l:]
                    lines[index % 4] = line
                    if (r2 == 1):
                        lines2[index % 4] = line2
                    if (r3 == 1):
                        lines3[index % 4] = line3
                    found = False
                    if (len(self.barcode_format) == 2):
                        if (self.Barcodes.has_key(barcode1)):
                            if (self.Barcodes[barcode1].has_key(barcode2)):
                                s = 0
                                b = self.Barcodes[barcode1][barcode2]
                                found = True
                            else:
                                (b1, b, s) = self.calcDistance(barcode2, self.Barcodes[barcode1])
                                if (s <= self.threshold2):
                                    b = self.Barcodes[barcode1][b]
                                    found = True
                        else:
                            (b, b1, s) = self.calcDistance(barcode1, self.Barcodes)
                            if (s <= self.threshold1):
                                if (b.has_key(barcode2)):
                                    s = 0
                                    b = b[barcode2]
                                    found = True
                                else:
                                    (b1, b2, s) = self.calcDistance(barcode2, b)
                                    if (s <= self.threshold2):
                                        b = b[b2]
                                        found = True

                    else:
                        if (self.Barcodes.has_key(barcode1)):
                            s = 0
                            b = self.Barcodes[barcode1]
                            found = True
                        else:
                            (b1, b, s) = self.calcDistance(barcode1, self.Barcodes)
                            if (s <= self.threshold1):
                                b = self.Barcodes[b]
                                found = True
                    if found == True:
                        counts[b] = counts[b] + 1
                        if b in self.queues.keys():
                            self.queues[b][0] += "".join(lines)
                            if (r2 == 1):
                                self.queues[b][1] += "".join(lines2)
                            if (r3 == 1):
                                self.queues[b][2] += "".join(lines3)
                        else:
                            self.queues[b] = ['']
                            [self.queues[b].append('') for r in [r2, r3] if r]
                    else:
                        counts['Undetermined'] = counts['Undetermined'] + 1
                        if 'Undetermined' in self.queues.keys():
                            self.queues['Undetermined'][0] += "".join(lines)
                            if (r2 == 1):
                                self.queues['Undetermined'][1] += "".join(lines2)
                            if (r3 == 1):
                                self.queues['Undetermined'][2] += "".join(lines3)
                        else:
                            self.queues['Undetermined'] = ['']
                            [self.queues['Undetermined'].append('') for r in [r2, r3] if r]

            index += 1
            if index % self.queue_out == 0:
                self.print_queue(files, files2, files3)

        self.print_queue(files, files2, files3)

    def print_queue(self,files, files2, files3):
        for b in self.queues.keys():
            for i, queue in enumerate(self.queues[b]):
                if i == 0 and (self.no_out_read != 1 or b == 'Undetermined'):
                    files[b].write(queue)
                elif i == 1 and (self.no_out_read != 2 or b == 'Undetermined'):
                    files2[b].write(queue)
                elif i == 2 and (self.no_out_read != 3 or b == 'Undetermined'):
                    files3[b].write(queue)
        del self.queues
        self.queues = {}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Run demultiplexing on fastq files')
    p.add_argument('--barcodes', '-b', action='store', required=True, help="barcodes file")
    p.add_argument('--fastq1', '-1', action='store', required=True, help="fastq file with barcode in header",
                   default="f")
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
    p.add_argument('')
    args = p.parse_args()
    Demultiplexing(args.barcodes, args.outdir, args.fastg1, args.fastq2, args.fastq3, args.threshold1,
                   args.threshold2, args.notrim, args.add2header, args.no_out_read, args.queue_out).run_demultiplexing()

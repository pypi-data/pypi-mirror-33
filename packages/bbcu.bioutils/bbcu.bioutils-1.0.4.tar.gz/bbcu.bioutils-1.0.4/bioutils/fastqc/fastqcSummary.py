"""
    given a directory with multiple folders of fastqc output do
        iterate over the folders
        extract sample name
        load the summary and aggregate the results to a table
        
    output table format
    -------------------
    name    read    Basic Statistics    Per base sequence quality   ...
    sample1 R1    PASS                FAIL                        ...
    sample2 R1    PASS                WARN                        ...
    ...
    
"""
import os
import pandas as pd
import argparse

# globals
_VERBOSE=True

def parseArgs():
    help_txt="This module aggregates the Fastqc-Summary files from each sample into a table."
    help_txt+="The Fastqc results should reside in sub-directories under the given input directory, one sub-dir for each sample."
    help_txt+="The output is a CSV file aggregating the results for all samples."
    parser = argparse.ArgumentParser(description=help_txt)
    parser.add_argument('--input-dir',help='Input directory at which all fastqc sub-directories (sub-dir = sample) reside',required=True)
    parser.add_argument('--output-table',help='Output csv filename for the output table',required=True)
    args = parser.parse_args()
    return args

def hashFiles_old(in_dir):
    """
        given the input directory, figure out the sample name from the sub-directories and link the summary files to the sample names
        output: hash table
            table[sample_name]=path-to-summary-file
        notes:
            ignoring files
            raise error in case a directory is not in the expected format
    """
    onlydirs = [ f for f in os.listdir(in_dir) if os.path.isdir(os.path.join(in_dir,f)) ]
    #onlydirs=np.array(onlydirs)
    #onlydirs.sort()
    # parse sample name:
    # split by "_" / go from end to start / drop the last 4 items (lane,read,number,fastqc) / join the 1st elements again
    # push everything to a hash table
    hash_table=dict()
    for item in onlydirs:
        #print item
        readnum = item.split('_')[-3]
        sname = '_'.join(item.split('_')[:-4])
        filename = os.path.join(in_dir,item,"summary.txt")
        if not os.path.isfile(filename):
            print "Could not file file: {} \nExit!".format(filename)
            raise IOError
        hash_table[(sname,readnum)]=filename
        #all_sample_names.append(sname)
        #all_reads_nums.append(readnum)
    #sample_names = np.unique(all_sample_names)
    #read_nums = np.unique(all_reads_nums)
    return hash_table

def loadSummaryFile(filename):
    summ_table = pd.read_table(filename,sep='\t',header=None,names=['status','feature','file'])
    return summ_table.set_index('feature')

def hashFiles(in_dir):
    """
        given the input directory, figure out the sample name from the sub-directories and link the summary files to the sample names
        output: dataframe table
            sample name \ read \ path-to-summary-file
        notes:
            ignoring files
            raise error in case a directory is not in the expected format
    """
    onlydirs = [ f for f in os.listdir(in_dir) if os.path.isdir(os.path.join(in_dir,f)) ]
    # parse sample name:
    # split by "_" / go from end to start / drop the last 4 items (lane,read,number,fastqc) / join the 1st elements again
    # push everything to a hash table
    readnums=[]
    snames=[]
    filenames=[]
    # features:
    features_lists={'Basic Statistics':[],
                    'Per base sequence quality':[],
                    'Per sequence quality scores':[],
                    'Per base sequence content':[],
                    'Per base GC content':[],
                    'Per sequence GC content':[],
                    'Per base N content':[],
                    'Sequence Length Distribution':[],
                    'Sequence Duplication Levels':[],
                    'Overrepresented sequences':[],
                    'Kmer Content':[]}
                    
    
    for item in onlydirs:
        #print item
        readnums.append(item.split('_')[-3])
        snames.append('_'.join(item.split('_')[:-4]))
        filename=os.path.join(in_dir,item,"summary.txt")
        filenames.append(filename)
        if not os.path.isfile(filename):
            print "Could not file file: {} \nExit!".format(filename)
            raise IOError
        # load summary file and append the features
        summ_file = loadSummaryFile(filename)
        for feature_name in summ_file.index:
            try:
                features_lists[feature_name].append(summ_file['status'].loc[feature_name])
            except:
                print 'error: here is the summ file'
                print summ_file
                print '\n\n'
                raise
    input_hash_table = {'sample':snames, 'read':readnums, 'file':filenames}
    for feature_name in features_lists.keys():
        input_hash_table[feature_name]=features_lists[feature_name]
    hash_table=pd.DataFrame(input_hash_table)
    return hash_table[['sample','read','file','Basic Statistics','Per base sequence quality','Per sequence quality scores'
                        ,'Per base sequence content','Per base GC content','Per sequence GC content','Per base N content','Sequence Length Distribution'
                        ,'Sequence Duplication Levels','Overrepresented sequences','Kmer Content']]



    
if __name__=='__main__':
    args = parseArgs()
    hash_table=hashFiles(args.input_dir)
    hash_table.sort(columns='sample',inplace=True)
    hash_table.to_csv(args.output_table)
    
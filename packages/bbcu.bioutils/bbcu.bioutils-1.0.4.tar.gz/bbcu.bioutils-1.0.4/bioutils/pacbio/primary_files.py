import glob
import logging
import os
from settings import PRIMARY_DIR

logger = logging.getLogger(__name__)

class DataNoCreatedException(Exception):
    def __init__(self, message):
        super(DataNoCreatedException, self).__init__(message)

class PrimaryFiles(object):
    def __init__(self, run_name, cell_name, root_dir=PRIMARY_DIR):
        self.root_dir = root_dir
        self.run_name = run_name
        self.cell_dir = os.path.join(root_dir, run_name, cell_name)
        self.pre_file_name = self.get_prefix_files_names()

    def get_prefix_files_names(self):
        logger.info('Access to run %s' %self.cell_dir)
        try:
            metadata_file = glob.glob(os.path.join(self.cell_dir, ".*run.metadata.xml"))[0]
        except IndexError:
            raise DataNoCreatedException('Raw data of the run %s is not created yet' %self.cell_dir)
        return metadata_file.split('.')[1]

    def data_transfered(self):
        transfer_file = os.path.join(self.cell_dir, self.pre_file_name+'.transferdone')
        try:
            with open(transfer_file, 'r') as tf:
                return True if len(tf.readlines()) == 12 else False
        except IOError:
            raise DataNoCreatedException('Raw data of the run %s is not create yet' %self.cell_dir)

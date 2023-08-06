from setuptools import setup, find_packages

with open('VERSION.txt', 'r') as version_file:
    version = version_file.read().strip()

requires = ['biopython', 'pandas', 'sqlalchemy', 'pysqlite']
setup(
    name='bbcu.bioutils',
    version=version,
    packages=find_packages(),
    scripts=['scripts/pacbio-run-status.py',
             'scripts/build-taxonomy-db.py',
             'scripts/gi2name.py',
             'scripts/create-samples-csv.py',
             'scripts/demultiplexing-fastq.py'],
    description='Common code shared among in-house Bioinformatics python packages',
    long_description=open('README.txt').read(),
    install_requires=requires,
    tests_require=requires + ['nose'],
    include_package_data=True,
    test_suite='nose.collector',
)


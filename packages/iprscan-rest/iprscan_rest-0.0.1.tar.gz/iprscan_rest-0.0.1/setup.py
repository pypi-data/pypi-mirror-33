import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='iprscan_rest',
    version='0.0.1',
    author='Damien Vantourout',
    author_email='damien.vantourout@gmail.com',
    description='This package allows to query the InterProScan REST API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    packages=setuptools.find_packages(),
    classifiers=(
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    )
)

import sys
import os
import re
from setuptools import setup
from setuptools import Extension
#from Cython.Build import cythonize
import numpy
import glob
from setuptools import find_packages
'''
'biopython',\
        'pymc>=2.3.4, < 3.0.0',\
        'scikit-learn>=0.15.2, <= 0.16.1',\
        'statsmodels>=0.5.0',\
        'mpmath>=0.19',\
        'pandas>=0.16.0',\
        'argparse',\
        'numpy',\
'''

if (sys.version_info[0], sys.version_info[1]) != (2, 7):
    raise RuntimeError('sortseq is currently only compatible with Python 2.7.\nYou are using Python %d.%d' % (sys.version_info[0], sys.version_info[1]))
#input_data_list_commands = glob.glob('mpathic_tests/commands/*.txt')
#input_data_list_inputs = glob.glob('mpathic_tests/input/*')

# DON'T FORGET THIS
#ext_modules = Extension("src.fast",["src/fast.c"])
ext_modules = Extension("mpathic.src.fast",["mpathic/src/fast.c"])

# main setup command
setup(
    name = 'mpathic',
    description = 'Tools for analysis of Sort-Seq experiments.',
    version = '0.1',
    author = 'Bill Ireland, Ammmar Tareen, Justin Kinney',
    author_email = 'tareen@cshl.edu',
    #long_description = readme,
#    platforms = 'Linux (and maybe also Mac OS X).',
#    packages = ['src'] + find_packages(),
#    package_dir = {'src':'src'},
    install_requires = [
'alabaster==0.7.10',
'Babel==2.5.3',
'backports.functools-lru-cache==1.5',
'biopython==1.71',
'certifi==2018.4.16',
'chardet==3.0.4',
'cvxopt==1.1.9',
'cycler==0.10.0',
'Cython==0.28.1',
'docutils==0.14',
'idna==2.6',
'imagesize==1.0.0',
'Jinja2==2.10',
'kiwisolver==1.0.1',
'MarkupSafe==1.0',
'matplotlib==2.2.2',
'mpmath==1.0.0',
'numpy==1.14.2',
'packaging==17.1',
'pandas==0.22.0',
'Pygments==2.2.0',
'pymc==2.3.6',
'pyparsing==2.2.0',
'python-dateutil==2.7.2',
'pytz==2018.4',
'requests==2.18.4',
'scikit-learn==0.19.1',
'scipy==1.0.1',
'six==1.11.0',
'sklearn==0.0',
'snowballstemmer==1.2.1',
'Sphinx==1.7.3',
'sphinxcontrib-websupport==1.0.1',
'subprocess32==3.2.7',
'typing==3.6.4',
'urllib3==1.22',
'weblogo==3.6.0',

            ],
    zip_safe=False,
    ext_modules = [ext_modules],
    include_dirs=['.',numpy.get_include()],
    include_package_data=True,
    
#    package_data = {
#                     'mpathic_tests.commands': ['*.txt'],
#                     'mpathic_tests': ['*.py','*.sh'],
#                     'mpathic_tests.input': ['*'],
#                     'mpathic_tests.output': ['*']
#                 }
    #package_data = {'mpathic':['tests/*']} # data for command line testing
)



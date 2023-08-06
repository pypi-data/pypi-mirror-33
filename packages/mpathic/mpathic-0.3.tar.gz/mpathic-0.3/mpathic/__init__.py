from contextlib import contextmanager
import os
import numpy as np
import scipy as sp
import argparse
import sys
import csv

class SortSeqError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        #return repr(self.value)
        return self.value

def simple_decorator(decorator):
    '''This decorator can be used to turn simple functions
    into well-behaved decorators, so long as the decorators
    are fairly simple. If a decorator expects a function and
    returns a function (no descriptors), and if it doesn't
    modify function attributes or docstring, then it is
    eligible to use this. Simply apply @simple_decorator to
    your decorator and it will automatically preserve the
    docstring and function attributes of functions to which
    it is applied.'''
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
    # Now a few lines needed to make simple_decorator itself
    # be a well-behaved decorator.
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator

@simple_decorator
def shutthefuckup(func):
    """
    Silences the standard output from any decroated function
    """

    # Define the wrapper function
    def func_wrapper(*arg,**kwargs):
        stdobak = sys.stdout
        with open(os.devnull, "w") as devnull:
            sys.stdout = devnull
            try:
                return func(*arg,**kwargs)
            finally:
                sys.stdout = stdobak
    
    # Return the wrapper function
    return func_wrapper


# To re-compile the fast.pyx/C file, fix code in pyx and run in terminal:
#  python setup.py build_ext --inplace

# simualte library/sort
from mpathic.src.simulate_library import SimulateLibrary
from mpathic.src.simulate_sort import SimulateSort

# profiles
from mpathic.src.profile_mut import ProfileMut
from mpathic.src.profile_freq import ProfileFreq
from mpathic.src.profile_info import ProfileInfo

# models
from mpathic.src.learn_model import LearnModel
from mpathic.src.evaluate_model import EvaluateModel
from mpathic.src.scan_model import ScanModel
from mpathic.src.predictive_info import PredictiveInfo

# input output
from mpathic.src import io_local as io


# to run functional tests from the command line
# from mpathic.tests import functional_tests_mpathic

from mpathic.src.utils import check

# demo functions
def demo(example='simulation'):
    """
    Runs a demonstration of mpathic.

    Parameters
    ----------

    example: (str)
        A string specifying which demo to run. Must be 'simulation',
        'profile', or 'modeling'.

    Returns
    -------

    None.
    """

    import os
    example_dir = os.path.dirname(__file__)

    example_dict = {
        'simulation': 'docs/source/simulations.py',
        'profile': 'docs/source/profiles.py',
        'model': 'docs/source/modeling.py'
    }

    check(example in example_dict,
          'example = %s is not valid. Must be one of %s'%\
          (example, example_dict.keys()))

    file_name = '%s/%s'%(example_dir, example_dict[example])
    with open(file_name, 'r') as f:
        content = f.read()
        line = '-------------------------------------------------------------'
        print('Running %s:\n%s\n%s\n%s'%\
              (file_name, line, content, line))
    exec(open(file_name).read())

"""
sys.exit()

# preprocess
from mpathic.src import preprocess as preprocess
preprocess.add_subparser(subparsers)




#profile_mutrate
import profile_mut as profile_mut
profile_mut.add_subparser(subparsers)

#profile_mutrate
import profile_ct as profile_ct
profile_ct.add_subparser(subparsers)

#profile_mutrate
import profile_freq as profile_freq
profile_freq.add_subparser(subparsers)

#learn_model
import learn_model as learn_model
learn_model.add_subparser(subparsers)

#predictiveinfo
import predictiveinfo as predictiveinfo
predictiveinfo.add_subparser(subparsers)

#profile_info
import profile_info as profile_info
profile_info.add_subparser(subparsers)

#Scan
import scan_model as scan_model
scan_model.add_subparser(subparsers)


#simulate_sort
import simulate_sort as simulate_sort
simulate_sort.add_subparser(subparsers)

#evaluate_model

#simulate_sort
import evaluate_model as evaluate_model
evaluate_model.add_subparser(subparsers)

# #simulate_evaluate
# import mpathic.simulate_evaluate as simulate_evaluate
# simulate_evaluate.add_subparser(subparsers)

#simulate_sort
import simulate_expression as simulate_expression
simulate_expression.add_subparser(subparsers)
"""

    

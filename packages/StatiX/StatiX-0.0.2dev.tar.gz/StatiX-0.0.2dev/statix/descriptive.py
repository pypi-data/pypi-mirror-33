# Package: statix
# Module:  descriptive
# About:   A module for computing descriptive statistics.
# Author:  Matthew D. Kearns
# Contact: mattdkearns@gmail.com

from math import ceil

def mean(data, trim=0, weighted=False):
    """Calculate and return the mean value of the data.

    data: a python list-like object
    trim: [0, 1]; default=0
    weighted: True/False; default=False
    """

    average = 0

    # trim data

    if 0 < trim <= 1:
        trim_amt = ceil(trim*len(data))
        if trim_amt % 2 !=0:
            trim_amt += 1

    # if weighted, compute weighted average

    if weighted:
        pass

    # otherwise, compute normal average

    else:
        pass

    return average


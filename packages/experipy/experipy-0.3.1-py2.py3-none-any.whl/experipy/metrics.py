"""
    experipy.metrics
    ~~~~~~~~~~~~~~~~

    This module provides the Metric class as a means of defining and 
    extracting values from the results of Experiment runs.
"""
import os
import re


class Metric(object):
    """Metric objects define a value to be extracted from a given file.
    
    A metric consists of a base filename, a regex with which to search
    that file, and a parser which converts the value, once found, into 
    the desired type. 

    Parameters
    ----------
    name : str
        The name of the metric.
    filename : str
        The name of the file in a given results directory to search. 
        For instance, if the metric should appear in the standard 
        output of a given experiment, then filename should be set as
        ``raw.out``.
    regex : str
        A string which will be compiled as a regular expression and 
        used to search for the metric. Must contain a Named Group with 
        the name ``value`` (i.e. ``(?P<value>\d+)``).
    parser : callable
        A callable taking a single string argument and returning the
        value converted to the desired type. Defaults to ``float``.
    """
    def __init__(self, name, filename, regex, parser=float):
        self.name = name
        self.filename = filename
        self.parser = parser

        if not re.search(r"\(\?P<value>.*\)", regex):
            raise ValueError("regex must contain a 'value' named group")
        self.regex = re.compile(regex)


    def get_value(self, resultpath, default=None):
        """Given a path to a results directory, attempt to extract the 
        value. Optionally provide a default value in the event the value
        can't be found.
        """
        fname = os.path.join(resultpath, self.filename)
        with open(fname) as f:
            for line in f:
                m = re.search(self.regex, line)
                if m:
                    return self.parser(m.group('value'))
        return default

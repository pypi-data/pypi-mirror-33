"""
Core library module
"""
import multiprocessing as mp
import numpy as np
import pandas as pd

#pylint: disable=too-few-public-methods
class FunctionObject(object):
    """
    Expose a simple interface for creating a function object to apply from

    Args:
        value: A value in the series

    Returns:
        The value of this function object applied to the value
    """
    def __call__(self, value):
        pass


def apply(source, function_obj, **kwargs):
    """
    Apply a function in a series/dataframe values in parallel

    Args:
        source: Pandas DataFrame/Series
        function_obj (FunctionObject): the function object to be applied in source
        kwargs (dict): extra options for the function

    Returns:
        Values produced by application of the function
    """
    if not isinstance(function_obj, FunctionObject):
        raise ValueError('function_obj should be an instance of FunctionObject class')
    workers = mp.cpu_count() - 1
    if 'workers' in kwargs:
        workers = kwargs.pop('workers')
    pool = mp.Pool(processes=workers)
    partitions = np.array_split(source, workers)
    results = pool.map(_apply_function,
                       [(partition, function_obj, kwargs)
                        for partition in partitions])
    result = pd.concat(results)
    pool.close()
    return result


def _apply_function(args):
    """
    Helper function for applying the function in a given source partition
    """
    source, function_obj, kwargs = args
    return source.apply(function_obj, kwargs)

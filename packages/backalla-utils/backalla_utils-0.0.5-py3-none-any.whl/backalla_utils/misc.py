import sys
from itertools import chain
import os
from glob import glob



def recursive_ls(path, get_generator=False, filter="*.*"):
    """Recursively list the files in a given target path.
    
    Arguments:
        path {str} -- Path of root folder to recursively list files
    
    Keyword Arguments:
        get_generator {bool} -- Flag to decide whether to return a generator or a list (default: {False})
        filter {str} -- Regex to filter filenames  (default: {"*.*"})
    
    Returns:
        [list/generator] -- Depending on the get_generator flag return the list
        of files or a generator
    """

    if get_generator:
        result = (chain.from_iterable(glob(os.path.join(x[0], filter)) for x in os.walk(path)))
    else:
        result = [y for x in os.walk(path) for y in glob(os.path.join(x[0], filter))]
    
    return result



def rprint(*args):
    """Print a string in one line by overwriting the current line.
    Used to print training and testing progress. Can accept multiple
    arguments which will be printed with spaces in between.
    """

    
    sys.stdout.write("\r{}".format(" ".join([str(arg) for arg in args])))
    sys.stdout.flush()
import sys

def rprint(*args):
    """Print a string in one line by overwriting the current line.
    Used to print training and testing progress. Can accept multiple
    arguments which will be printed with spaces in between.
    """

    
    sys.stdout.write("\r{}".format(" ".join([str(arg) for arg in args])))
    sys.stdout.flush()
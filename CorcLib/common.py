from contextlib import contextmanager
import os

@contextmanager
def cd(newdir): # pragma: no cover
    '''Change active directory so that the local directory becomes newdir.
    This affects everything from subprocess calls to ROOT Print() and SaveAs()
    commands.
    Example:
        ::
        
            with cd('/path/to/stuff/'):
                ...
                <code acting in /path/to/stuff/ directory>
                ...
    Args:
        newdir (str): Directory to cd to within the `with` statement.
    '''
    print ('cd '+newdir)
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

def lib_path():
    print (
        os.path.dirname(
            os.path.abspath(__file__)
            )
        )
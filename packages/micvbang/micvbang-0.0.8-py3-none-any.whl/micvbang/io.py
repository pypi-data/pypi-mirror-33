import os
import sys
import gzip
import stat


def here(*ps):
    """ Return script execution path os.path.join'ed with the given arguments.
    """
    return os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), *ps)


def list_dir(path, dirs=False, files=True, ext=None):
    """ List the contents of a directory.

    Returns directories if dirs is set.
    Returns files if files is set.
    Returns only files with the given extension if ext is set.
    """
    for fname in os.listdir(path):
        fpath = os.path.join(path, fname)
        mode = os.stat(fpath).st_mode

        isdir = stat.S_ISDIR(mode)
        isfile = stat.S_ISREG(mode)

        d = dirs and isdir
        f = files and isfile and (ext is None or os.path.splitext(fname)[1] == ext)

        if d or f:
            yield fpath


def list_dir_recursive(path, dirs=False, files=True, ext=None):
    """ Recursively list the contents of a directory.

    Returns directories if dirs is set.
    Returns files if files is set.
    Returns only files with the given extension if ext is set.
    """
    for f in list_dir(path, dirs=False, files=True, ext=ext):
        yield f

    for d in list_dir(path, dirs=True, files=False):
        if dirs:
            yield d
        yield from list_dir_recursive(d, dirs, files, ext)


def open_file(path, mode='r'):
    """ Open a file and return a stream.

    If the file has .gz extension, `gzip.open` is used in place of `open`.
    """
    _, ext = os.path.splitext(path)
    if ext == '.gz':
        return gzip.open(path, mode)
    else:
        return open(path, mode)

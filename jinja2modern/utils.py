import os
import errno

def strip_list(list):
    return [x.strip() for x in list if x.strip()]

def open_if_exists(filename, mode='rb'):
    """Returns a file descriptor for the filename if that file exists,
    otherwise `None`.
    """
    try:
        return open(filename, mode)
    except IOError, e:
        if e.errno not in (errno.ENOENT, errno.EISDIR):
            raise

def create_dir_if_not_exist(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


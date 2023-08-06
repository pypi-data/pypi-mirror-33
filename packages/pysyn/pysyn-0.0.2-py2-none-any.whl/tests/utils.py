import os
import shutil

def remove_path(path):
    """
    Remove the file or directory with all of its content.
    """
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
        except OSError:
            print "Unable to remove folder: %s" % path
    else:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            print "Unable to remove file: %s" % path

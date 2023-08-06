import os
import errno
import logging
import json
import subprocess
import pyperclip
import os

import registration
from leap.soledad.client import Soledad

logger = logging.getLogger(__name__)

def create_path_if_not_exists(path):
    """
    Utility function used to create a directory at the specified path.
    :param path: path where directory is to be created
    :return: None
    """
    try:
        if not os.path.isdir(path):
            logger.info('creating directory: %s.' % path)
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            raise


def create_client_from_file():
    """
    If the user is logged in, instantiates a Soledad object and returns it.
    Otherwise, returns None.
    :return: Soledad object if user is logged in, None otherwise
    """
    auth_file = os.path.expanduser('~/.syn/auth_file')

    # If user is logged, read session parameters from auth file
    if registration.db_is_open():

        with open(auth_file, 'r') as cfg:
            client_info = cfg.read()
            client_config = json.loads(client_info)

        return Soledad(
            uuid=client_config['uuid'],
            passphrase=client_config['passphrase'],
            secrets_path=client_config['secrets_path'],
            local_db_path=client_config['local_db_path'],
            server_url=client_config['server_url'],
            cert_file=client_config['cert_file'],
            auth_token=client_config['auth_token']
        )
    else:
        raise registration.DatabaseException("There is no open database")


def copy_to_clipboard(string):
    """
    Copies the provided string to the clipboard.
    This function depends on the xclip system tool. Without it, it will not be able to copy the contents to the
    clipboard.
    :param string: string to copy to the system clipboard
    :return: True if content was copied to clipboard, false otherwise
    """

    if type(string) is not str:
        return False

    FNULL = open(os.devnull, 'w')
    rc = subprocess.call(['which', 'xclip'], stdout=FNULL, stderr=subprocess.STDOUT)

    if rc == 0:
        pyperclip.copy(string)
        return True

    else:
        return False

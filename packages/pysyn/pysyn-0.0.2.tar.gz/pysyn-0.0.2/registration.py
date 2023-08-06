from leap.soledad.client import Soledad
from leap.soledad.client._secrets.util import SecretsError

import syn_utils

import sys
import logging
import os
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Basic handler. Logs to sys.stdout
handler = logging.StreamHandler(sys.stdout)

logger.addHandler(handler)


# Developing using Soledad's offline mode by setting server_url to None
server_url = None

base_db_dir = os.path.expanduser('~/.syn/dbs/')


class DatabaseException(Exception):
    pass


def open_db(uuid, passphrase):
    """
    Logs in a user with the specified uuid and passphrase.
    :param uuid: user unique ID
    :param passphrase: passphrase used to cipher secrets and authenticate user
    :return: Soledad object
    :rtype: leap.soledad.client.Soledad
    """

    if not db_is_open():

        # Database directory
        db_dir = base_db_dir + uuid + '/'

        secrets_path = db_dir + 'secrets.json'
        cert_file = db_dir + 'ca.crt'
        token = db_dir + 'token'
        shared_db_path = db_dir + 'db.sqlite'

        # Error opening file
        if not os.path.exists(secrets_path):
            raise EnvironmentError("Error opening file at {}".format(secrets_path))

        try:

            client = Soledad(
                uuid,
                passphrase,
                secrets_path=secrets_path,
                local_db_path=shared_db_path,
                server_url=server_url,
                cert_file=cert_file,
                auth_token=token
            )


            # If we can make it past this point, it means we were able to log in.
            # Now we store a temporary file to denote that this user is authenticated
            auth_file = os.path.expanduser('~/.syn/auth_file')

            # TODO: create ~/.syn elsewhere
            # syn_utils.create_path_if_not_exists(os.path.expanduser('~/.syn'))


            # TODO: URGENTLY replace this with something cryptographically secure.
            # We want something retrievable while OFFLINE (think hash, seed, prng, rng?)
            # Something that can be randomly written and recovered and authenticated by both.
            # This is to avoid someone simply creating the auth file and writing "authenticated" in it and fooling
            # the offline auth mechanism.
            with open(auth_file, 'w+') as cfg:

                params = {
                    'uuid': uuid,
                    'passphrase': passphrase,
                    'secrets_path': secrets_path,
                    'local_db_path': shared_db_path,
                    'server_url': None,
                    'cert_file': cert_file,
                    'auth_token': token
                }

                # Jsonify the client parameters and write them to auth file
                params = json.dumps(params)
                cfg.write(params)

            return client

        # secrets.json is not properly formatted
        except ValueError as e:
            raise ValueError("%s is not properly formatted." % secrets_path)


        # except IOError as e:
        #     # TODO: better way to unpack and only get one variable?
        #     _, value, _ = sys.exc_info()
        #
        #     # Check that the IOError is regarding the secrets.json file
        #     if value.filename.endswith('secrets.json'):
        #         print("FILENAME")
        #         # click.echo("Necessary cryptographic material not found. Has this user been registered?")
        #         pass
        #     raise

        # SecretsError indicated trouble decrypting secrets.json
            # Most likely due to wrong passphrase

        except SecretsError as e:
            raise SecretsError("Unable to decrypt secrets.json")

        except EnvironmentError as e:
            print(os.strerror(e.errno))
            raise

    else:
        raise DatabaseException("Database already open")


def close_db():
    """
    Closes a database if there is one currently open
    """
    auth_file = os.path.expanduser('~/.syn/auth_file')

    if db_is_open():

        if os.path.exists(auth_file):
            os.remove(auth_file)

    else:
        raise DatabaseException("There is no open database")


def new_db(uuid, passphrase):
    """
    Creates a new, empty database. Also creates the data structure that holds all relevant files.

    :param uuid: unique database ID
    :param passphrase: passphrase used to encrypt and decrypt the database
    :return: None
    """
    # TODO: check that a db doesn't already exist with the provided uuid

    # Database directory
    db_dir = base_db_dir + uuid + '/'

    try:
        # Create necessary user directory
        syn_utils.create_path_if_not_exists(db_dir)

        # When Soledad is in offline mode, secrets.json will be created on-the-fly at this path
        secrets_path = db_dir + 'secrets.json'
        cert_file = db_dir + 'ca.crt'
        token = db_dir + 'token'
        shared_db_path = db_dir + 'db.sqlite'

        # TODO: replace this with a function for creating a secrets.json while offline. It would remove the need
        # of instantiating a Soledad object just for the purpose of creating one a secrets.json.
        # Instantiating a Soledad object is really only useful in the login method.
        client = Soledad(
            uuid,
            passphrase,
            secrets_path=secrets_path,
            local_db_path=shared_db_path,
            server_url=server_url,
            cert_file=cert_file,
            auth_token=token
        )

    except OSError as e:
        type, value, traceback = sys.exc_info()
        raise DatabaseException, ('A database with that UUID already exists', type, value), traceback


def db_is_open():
    """
    Returns whether or not a database is open
    :return: True if a database is open, False otherwise
    """
    auth_file = os.path.expanduser('~/.syn/auth_file')
    return os.path.exists(auth_file)

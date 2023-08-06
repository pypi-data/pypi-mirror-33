import os
import string
import random


def generate_id():
    """
    Generates a random token used for entry ID's. Uses 32 bytes of randomness.
    :return:
    """
    random_bytes = os.urandom(32)

    symbols = string.ascii_letters + string.digits
    len_symbols = len(symbols)

    indices = [int(len_symbols * (ord(byte) / 256.0)) for byte in random_bytes]

    token = "".join([symbols[index] for index in indices])

    return token


def generate_password(length=8):
    """
    Generates a random password of a given length.

    This method uses /dev/urandom as a high entropy data source in order to obtain random bytes.
    This method is non-deterministic.

    :param length: length of the desired password
    :return: a password
    :rtype: str
    """
    random_bytes = os.urandom(length)

    symbols = string.ascii_letters + string.digits
    len_symbols = len(symbols)

    indices = [int(len_symbols * (ord(byte) / 256.0)) for byte in random_bytes]

    password = "".join([symbols[index] for index in indices])

    return password


def generate_password_deterministic(length=8, seed=None):
    """
    Generates a random password of a given length.

    This method uses an optional seed as a data source. If no seed is specified, it uses the system time.
    This method is deterministic.

    :param seed: value used to initialize the pseudo-random number generator.
    :return: a password
    :rtype: str
    """
    random.seed(seed)

    alphabet = string.ascii_letters + string.digits
    password = ''.join(random.choice(alphabet) for i in range(length))

    return password

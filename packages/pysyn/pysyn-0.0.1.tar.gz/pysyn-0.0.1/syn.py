import click
import sys
import logging
import datetime
import json

import registration
import generator
import data
from syn_utils import create_client_from_file

from leap.soledad.common.l2db.errors import RevisionConflict
from leap.soledad.common.l2db.errors import InvalidDocId

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Basic handler. Logs to sys.stdout
handler = logging.StreamHandler(sys.stdout)

logger.addHandler(handler)


@click.group()
def cli():
    """
    Syn is a password manager which offers an easy to use interface and cryptographically secure storage of passwords
    and notes.
    """
    pass


@cli.command()
@click.option('--length', default=8, help='Specifies the amount of characters in the passphrase')
@click.option('--seed', default=None, help='Provides a seed to make password generation follow a deterministic process')
def passphrase(length, seed):
    """
    Generates a passphrase
    """

    # If seed is provided, generate password with deterministic approach
    if seed:
        passphrase = generator.generate_password_deterministic(length, seed)

    # If no seed. use non-deterministic approach
    else:
        passphrase = generator.generate_password(length)

    click.echo("Passphrase is: %s" % passphrase)


@cli.command(name='new')
def new_db():
    """
    Creates a new database
    """
    click.echo("Creating a new database...")
    uuid = click.prompt('UUID', type=str)
    passphrase = click.prompt('Passphrase', type=unicode, hide_input=True, confirmation_prompt=True)

    try:
        registration.new_db(uuid, passphrase)

        click.echo('Successfully created a database!')

    except registration.DatabaseException as e:
        error_message = e[0]
        click.echo(error_message)


@cli.command(name='open')
def open_db():
    """
    Opens the database
    """

    if not registration.db_is_open():
        uuid = click.prompt('UUID', type=str)
        passphrase = click.prompt('Passphrase', type=unicode, hide_input=True)

        try:
            registration.open_db(uuid, passphrase)

            click.echo("Database has been opened")

        except Exception as e:
            click.echo(e)

    else:
        click.echo("A database is already open")


@cli.command(name="close")
def close_db():
    """
    Closes a database
    """
    try:
        registration.close_db()

        click.echo("Database has been closed")

    except Exception as e:
        click.echo(e)


@cli.command(name='add')
def add_entry():
    """
    Store a new entry in the database
    """

    # TODO: make it so entry names are checked "eagerly". No need to finish all the prompt inputs before Syn
    # says that the entry is not valid because the name is taken or because it doesn't have a valid ID (space in
    # doc id for instance).

    def cb(data):
        click.echo("Successfully stored the entry!")

    def eb(failure):
        """
        Error callback function. Raises the exception that fired the Errback
        :param failure: Twisted failure object caught by the Errback
        """
        # This will raise a revision conflict if a doc with the same ID is stored twice.

        # This catches the async failure and returns the Exception type
        err = failure.trap(RevisionConflict, InvalidDocId)

        if err == RevisionConflict:
            click.echo("An entry already exists with the same name")

        if err == InvalidDocId:
            click.echo("Invalid entry name.")

    try:
        client = create_client_from_file()
        data_manager = data.DataManager(client)

        # Prompts
        entry_name = click.prompt("Name the entry", type=str)
        if click.confirm("Would you like to randomly generate a passphrase?"):
            length = click.prompt("Enter the desired length of the passphrase", type=int, default=8)
            seed = click.prompt("Enter a generation seed", default="", type=str)

            # If seed was set, use deterministic passphrase generation
            if seed != "":
                passphrase = generator.generate_password_deterministic(length, seed)

            # Else use non-deterministic passphrase generation
            else:
                passphrase = generator.generate_password(length)
        else:
            passphrase = click.prompt("Enter the desired passphrase", hide_input=True, confirmation_prompt=True)

        # Create entry
        entry = data.Entry(entry_name, passphrase)

        # Attempt to store entry
        data_manager.create_doc(entry, cb=cb, eb=eb)

    except Exception as e:
        click.echo(e)


@cli.command()
def delete_entry():
    """
    Delete an entry from the database
    """

    def eb(failure):
        # This catches the async failure and returns the Exception type
        err = failure.trap(AssertionError)

        # Assertion error means that the entry could not be found
        if err == AssertionError:
            # raise AssertionError()
            click.echo("Could not find an entry by that name.")

    def cb(data):
        click.echo("Entry deleted successfully!")

    client = create_client_from_file()
    data_manager = data.DataManager(client)

    entry_name = click.prompt("Enter the ID of the entry you wish to remove", type=str)

    data_manager.delete_doc(entry_name, cb=cb, eb=eb)


@cli.command(name="list")
def list_entries():
    """
    Lists the names of stored entries
    """
    try:
        client = create_client_from_file()
        data_manager = data.DataManager(client)
        data_manager.list_entries()

    except Exception as e:
        click.echo(e)


@cli.command(name='get')
@click.option('--name', type=str)
def get_entry(name):
    """
    Shows the details of an entry
    """

    def cb(data):

        # If no entry is found
        if data is None:
            click.echo("Did not find any entry by that name.")

        else:
            entry_string = data.get_json()
            entry = json.loads(entry_string)

            click.echo("Found the following entry:")

            # Horizontal line
            click.echo(''.join(u'\u2500' for x in range(25)))

            click.echo("Name: {}".format(entry['name']))
            click.echo(
                "Time of creation: {} UTC".format(datetime.datetime.utcfromtimestamp(entry['timestamp_creation'])))
            click.echo(
                "Time of last modification: {} UTC".format(datetime.datetime.utcfromtimestamp(entry['last_modified'])))

            # TODO: add this functionality
            click.echo("Contents of the entry have been copied to the system clipboard!", nl=True)

            # Horizontal line
            click.echo(''.join(u'\u2500' for x in range(25)))

    try:

        client = create_client_from_file()

        if not name:
            name = click.prompt("Name of the entry you wish to obtain", type=str)

        data_manager = data.DataManager(client)
        data_manager.get_entry(name, cb=cb)

    except Exception as e:
        click.echo(e)

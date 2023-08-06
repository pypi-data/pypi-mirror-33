import time
import json
import logging
import sys
from generator import generate_id

from twisted.internet import defer, reactor
# from leap.soledad.common.l2db.errors import RevisionConflict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Basic handler. Logs to sys.stdout
handler = logging.StreamHandler(sys.stdout)

logger.addHandler(handler)

class DataManager(object):
    """
    Class that wraps Soledad's core functionalities regarding data storage and utilizes
    Twisted natives.
    """

    def __init__(self, soledad):
        self.soledad_client = soledad


    def get_entry(self, name, cb=None, eb=None):
        """
        Obtains the details of an entry provided it exists in the database
        :param name:
        :return:
        """

        def default_cb(doc):
            """
            The default behavior returns the Document with encompasses the Entry object
            """
            entry_json = json.loads(doc.get_json())
            print(entry_json)

        d = self._get_entry(name)

        if cb:
            d.addCallback(cb)
        else:
            d.addCallback(default_cb)

        d.addCallback(lambda _: reactor.stop())

        reactor.run()


    @defer.inlineCallbacks
    def _get_entry(self, name):
        """
        Wrapper function for the get_entry() method
        """
        entry = yield self.soledad_client.get_doc(name)
        defer.returnValue(entry)


    def list_entries(self, cb=None):
        """
        Obtains the list of all entries stored in the database
        :param cb: optional callback function which receives the a tuple comprised of the amount of documents found
        as well as the list of documents itself
        """

        def default_cb(data):
            """
            Callback function for the deferred returned from Soledad.get_all_docs().
            Prints the total amount of entries to stdout as well as the names of the entries
            """
            # num_docs = data[0]
            list_docs = data[1]
            num_docs = len(list_docs)

            print ("Found a total of %s entries:" % num_docs)
            for doc in list_docs:
                print(doc.doc_id)

        d = self._list_entries()

        if cb:
            d.addCallback(cb)
        else:
            d.addCallback(default_cb)

        d.addCallback(lambda _: reactor.stop())

        reactor.run()


    @defer.inlineCallbacks
    def _list_entries(self):
        """
        Wrapper function for list_entries() method
        :param cb:
        :return:
        """
        data = yield self.soledad_client.get_all_docs()
        defer.returnValue(data)


    def create_doc(self, entry, cb=None, eb=None):
        """
        Creates and stores an entry in the database.
        :param entry: Entry object that is to be stored in the database
        :param cb: optional callback function which receives the Document object which wraps the stored Entry
        """

        d = self._create_doc(entry)

        # Add the provided callback to the deferred callback chain
        if cb:
            d.addCallback(cb)

        if eb:
            d.addErrback(eb)

        d.addCallback(lambda _: reactor.stop())

        reactor.run()


    @defer.inlineCallbacks
    def _create_doc(self, entry):
        """
        Wrapper function for create_doc() method
        :param entry: instance of the Entry class
        :return:
        """

        # Set the name of the entry as the ID of the document
        doc_id = entry.name

        # Get the deferred containing the document that was stored
        data = yield self.soledad_client.create_doc_from_json(str(entry), doc_id=doc_id)

        # Have the defer return the value to the calling function
        defer.returnValue(data)


    def delete_doc(self, entry_name, cb=None, eb=None):
        """
        Deletes a document from the database
        :param entry_name: name of the entry contained in the document
        :param cb: Optional callback
        """

        def default_cb(doc):
            # Delete the document

            # TODO: find a way to catch the error in here when no document is found!
            # d.addCallback(lambda _: self.soledad_client.delete_doc(doc))

            self.soledad_client.delete_doc(doc)

        def errfunc(failure):
            print("err")
            print(failure)

        # Since we need to give the doc to delete_doc(), we get it from this preexisting function
        # whose deferred returns a Document object
        d = self._get_entry(entry_name)

        d.addCallback(default_cb)

        if cb:
            d.addCallback(cb)

        # Add custom errback function if provided
        if eb:
            d.addErrback(eb)

        d.addCallback(lambda _: reactor.stop())

        reactor.run()


class Entry(object):

    def __init__(self, name, content, last_modified=None, timestamp_creation=None, uuid=None):
        self.name = name
        self.content = content
        self.timestamp_creation = timestamp_creation or int(time.time())
        self.last_modified = last_modified or self.timestamp_creation
        self.uuid = uuid or generate_id()


    @classmethod
    def from_json(cls, json_string):
        """
        Alternate constructor used for instantiating Entry from a json-formatted string
        """
        attributes = json.loads(json_string)

        if not isinstance(attributes, dict):
            raise ValueError

        return cls(**attributes)

    # TODO: Returning a JSON representation as of now in order to be able to use Soledad's
    # create_doc_from_json(). Try to find another way to simply create a doc by passing this object,
    # or create a specific method which will handle JSON parsing of this class.
    def __str__(self):
        return json.dumps(self.__dict__)

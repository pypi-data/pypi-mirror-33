"""ZODB3 backend."""


# Copyright (c) 2001-2009 ElevenCraft Inc.
# See LICENSE for details.
import schevo
import schevo.mt
#from schevo.store.backend import SchevoStoreBackend
from schevo.database import format_dbclass
from BTrees.OOBTree import OOBTree
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList

from ZODB import DB
from ZEO.ClientStorage import ClientStorage

import transaction
import logging
log = logging.getLogger(__name__)

from gevent import Greenlet

__all__ = ['ZodbBackend', 'ThreadedConnectionPool']


class ZodbBackend(object):

    description = 'Backend that directly uses ZODB > 3.7.4'
    backend_args_help = """
    (no backend options)
    """

    BTree = OOBTree
    PDict = PersistentMapping
    PList = PersistentList

    __test__ = False

    def __init__(self, addr, **kwargs):
        self._kwargs = kwargs
        self._addr = addr
        self.host, self.port = self._addr.split(':')
        if 'storage' in kwargs:
            self._storage = kwargs['storage'] 
        else:
            self._storage = ClientStorage((self.host, int(self.port)))
        self._is_open = False
        self.open()

    @classmethod
    def args_from_string(cls, s):
        """Return a dictionary of keyword arguments based on a string given
        to a command-line tool."""
        kw = {}
        if s is not None:
            for arg in (p.strip() for p in s.split(',')):
                name, value = (p2.strip() for p2 in arg.split('='))
                raise KeyError(
                    '%s is not a valid name for backend args' % name)
        return kw

    @classmethod
    def usable_by_backend(cls, addr):
        """Return (True, additional_backend_args) if the named file is
        usable by this backend, or False if not."""

        host, port = addr.split(':')
        cls.storage = ClientStorage((host, int(port)))
        
        # retrieve the filename of the DB
        filename = cls.storage._info['name']

        with open(filename, 'rb') as f:
            # Get first 128 bytes of file.
            header = f.read(128)
            f.close()
        
        # Look for ZODB signatures.
        if header[:4] == 'FS21' and 'persistent.mapping' in header:
           return (True, {})
        else:
           return False

    def open(self, sync=True):
        if not self._is_open:
            self.zodb = DB(self._storage)
            self.conn = self.zodb.open()
            self._is_open = True

    def get_root(self):
        """Return the connection 'root' object."""
        return self.conn.root()

    @property
    def has_db(self):
        """Return True if the backend has a schevo db."""
        return self.get_root().has_key('SCHEVO')

    def commit(self):
        """Commit the current transaction."""
        try:
            manager = self.conn.transaction_manager
            tx = manager.get()
            assert tx == transaction.get(), 'not the same transaction!'
            tx.commit()
            #self.conn.commit(tx)
        except Exception:
            self.rollback()
            raise

    def rollback(self):
        """Abort the current transaction."""
        transaction.abort()

    def pack(self):
        """Pack the underlying storage."""
        #self.zodb.pack()
        self.conn.db().pack()

    def close(self):
        """Close the underlying storage (and the connection if needed)."""
        self.rollback()
        self.pack()
        self.conn.close()
        self.zodb.close()
        self._storage.close()
        self._is_open = False


class ThreadedConnectionPool(object):


    DatabaseClass = format_dbclass[2]
    connections = {}
    def __init__(self, d=None, sync=True, debug=True, block=True, processes=2):
        if debug:
            if d is not None:
                assert isinstance(d, dict) == True
        self.debug = debug
        self.sync = sync    
        for key,value in d.iteritems():
            thread = Greenlet.spawn(self.run, value)
            db = thread.get(block=block)
            if self.debug:
                log.debug("Initialized ZODB instance: %r" % db)
            self.connections[key] = db
            #thread2.join()
            #thread.join()

    def run(self, url):

        conn = ZodbBackend(url)
        if not conn._is_open:
            log.debug("Opening database...")
            conn.open()
        db = self.DatabaseClass(conn)
        if self.sync:
            db._sync()
        #db._commit()
        #db._label = url
        schevo.mt.install(db)
        return db

    def __getitem__(self, key):
        try:
            v = self.connections[key]
        except KeyError:
            return None
        return v

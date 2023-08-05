# (c) 2009-2018 Martin Wendt and contributors; see WsgiDAV https://github.com/mar10/wsgidav
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Implementation of a WebDAV provider that provides a very basic, read-only
resource layer emulation of a MongoDB database.

Usage: add the following entries to wsgidav.conf::

    from wsgidav.samples.mongo_dav_provider import MongoResourceProvider
    mongo_dav_opts = {}
    addShare("mongo", MongoResourceProvider(mongo_dav_opts))

Valid options are (sample shows defaults)::

    opts = {"host": "localhost",       # MongoDB server
            "port": 27017,             # MongoDB port
            # This options are used with `mongod --auth`
            # The user must be created in the admin db with
            # > use admin
            # > db.addUser(username, password)
            "user": None,              # Authenticate with this user
            "pwd": None,               # ... and password
            }

"""
from pprint import pformat

import pymongo
from bson.objectid import ObjectId
from wsgidav import compat, util
from wsgidav.dav_provider import DAVCollection, DAVNonCollection, DAVProvider
from wsgidav.util import joinUri

__docformat__ = "reStructuredText"

_logger = util.getModuleLogger(__name__)


# ============================================================================
#
# ============================================================================
class ConnectionCollection(DAVCollection):
    """Root collection, lists all mongo databases."""

    def __init__(self, path, environ):
        DAVCollection.__init__(self, path, environ)
        self.conn = self.provider.conn

    def getMemberNames(self):
        return [name.encode("utf8") for name in self.conn.database_names()]

    def getMember(self, name):
        return DbCollection(joinUri(self.path, name), self.environ)


class DbCollection(DAVCollection):
    """Mongo database, contains mongo collections."""

    def __init__(self, path, environ):
        DAVCollection.__init__(self, path, environ)
        self.conn = self.provider.conn
        self.db = self.conn[self.name]

    def getDisplayInfo(self):
        return {"type": "Mongo database"}

    def getMemberNames(self):
        return [name.encode("utf8") for name in self.db.collection_names()]

    def getMember(self, name):
        coll = self.db[name]
        return CollCollection(joinUri(self.path, name), self.environ, coll)


class CollCollection(DAVCollection):
    """Mongo collections, contains mongo documents."""

    def __init__(self, path, environ, coll):
        DAVCollection.__init__(self, path, environ)
        self.conn = self.provider.conn
        self.coll = coll

    def getDisplayInfo(self):
        return {"type": "Mongo collection"}

    def getMemberNames(self):
        res = []
        for doc in self.coll.find():
            res.append(compat.to_native(doc["_id"]))
        return res

    def getMember(self, name):
        doc = self.coll.find_one(ObjectId(name))
        return DocResource(joinUri(self.path, name), self.environ, doc)


class DocResource(DAVNonCollection):
    """Mongo document, returned as virtual text resource."""

    def __init__(self, path, environ, doc):
        DAVNonCollection.__init__(self, path, environ)
        self.doc = doc

    def getContent(self):
        html = "<pre>" + pformat(self.doc) + "</pre>"
        return compat.StringIO(html.encode("utf8"))

    def getContentLength(self):
        return len(self.getContent().read())

    def getContentType(self):
        return "text/html"

    def getDisplayName(self):
        doc = self.doc
        if doc.get("_title"):
            return doc["_title"].encode("utf8")
        elif doc.get("title"):
            return doc["title"].encode("utf8")
        elif doc.get("_id"):
            return compat.to_native(doc["_id"])
        return compat.to_native(doc["key"])

    def getDisplayInfo(self):
        return {"type": "Mongo document"}


# ============================================================================
# MongoResourceProvider
# ============================================================================
class MongoResourceProvider(DAVProvider):
    """DAV provider that serves a MongoDB structure."""

    def __init__(self, options):
        super(MongoResourceProvider, self).__init__()
        self.options = options
        self.conn = pymongo.Connection(options.get("host"), options.get("port"))
        if options.get("user"):
            # If credentials are passed, acquire root access
            db = self.conn["admin"]
            res = db.authenticate(options.get("user"), options.get("pwd"))
            if not res:
                raise RuntimeError("Failed to logon to db %s as user %s" %
                                   (db.name, options.get("user")))
            _logger.info("Logged on to mongo db '%s' as user '%s'" %
                         (db.name, options.get("user")))
        _logger.info("MongoResourceProvider connected to %s" % self.conn)

    def getResourceInst(self, path, environ):
        """Return DAVResource object for path.

        See DAVProvider.getResourceInst()
        """
        _logger.info("getResourceInst('%s')" % path)
        self._count_getResourceInst += 1
        root = ConnectionCollection("/", environ)
        return root.resolve("/", path)

# (c) 2009-2018 Martin Wendt and contributors; see WsgiDAV https://github.com/mar10/wsgidav
# Original PyFileServer (c) 2005 Ho Chun Wei.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Implementation of a WebDAV provider that provides a very basic, read-only
resource layer emulation of a MySQL database.

This module is specific to the WsgiDAV application. It provides a
classes ``MySQLBrowserProvider``.

Usage::

    (see doc/annotated_wsgidav.conf)
    MySQLBrowserProvider(host, user, passwd, db)

    host - host of database server
    user - username to access database
    passwd - passwd to access database
    db - name of database on database server

The ``MySQLBrowserProvider`` provides a very basic, read-only
resource layer emulation of a MySQL database.
It provides the following interface:

    - the root collection shared consists of collections that correspond to
      table names

    - in each table collection, there is a resource called "_ENTIRE_CONTENTS".
      This is a non-collection resource that returns a csv representation of the
      entire table

    - if the table has a single primary key, each table record will also appear
      as a non-collection resource in the table collection using the primary key
      value as its name. This resource returns a csv representation of the record
      and will also include the record attributes as live properties with
      attribute name as property name and table name suffixed with colon as the
      property namespace


This is a very basic interface and below is a by no means thorough summary of
its limitations:

    - Really only supports having numbers or strings as primary keys. The code uses
      a numeric or string comparison that may not hold up if the primary key is
      a date or some other datatype.

    - There is no handling for cases like BLOBs as primary keys or such. Well, there is
      no handling for BLOBs in general.

    - When returning contents, it buffers the entire contents! A bad way to return
      large tables. Ideally you would have a FileMixin that reads the database even
      as the application reads the file object....

    - It takes too many database queries to return information.
      Ideally there should be some sort of caching for metadata at least, to avoid
      unnecessary queries to the database.

"""
from __future__ import print_function

import csv
import hashlib
# import md5
import time

import MySQLdb  # @UnresolvedImport
from wsgidav import compat, util
from wsgidav.dav_error import (
    HTTP_FORBIDDEN,
    DAVError,
    PRECONDITION_CODE_ProtectedProperty
)
from wsgidav.dav_provider import DAVProvider, _DAVResource

__docformat__ = "reStructuredText"

_logger = util.getModuleLogger(__name__)


class MySQLBrowserResource(_DAVResource):
    """Represents a single existing DAV resource instance.

    See also DAVResource and MySQLBrowserProvider.
    """

    def __init__(self, provider, path, isCollection, environ):
        super(MySQLBrowserResource, self).__init__(path, isCollection, environ)
        self._cache = None

    def _init(self):
        """Read resource information into self._cache, for cached access.

        See DAVResource._init()
        """
        # TODO: recalc self.path from <self._filePath>, to fix correct file system case
        #       On windows this would lead to correct URLs
        self.provider._count_getResourceInstInit += 1
        tableName, primKey = self.provider._splitPath(self.path)

        displayType = "Unknown"
        displayTypeComment = ""
        contentType = "text/html"

#        _logger.debug("getInfoDict(%s), nc=%s" % (path, self.connectCount))
        if tableName is None:
            displayType = "Database"
        elif primKey is None:  # "database" and table name
            displayType = "Database Table"
        else:
            contentType = "text/csv"
            if primKey == "_ENTIRE_CONTENTS":
                displayType = "Database Table Contents"
                displayTypeComment = "CSV Representation of Table Contents"
            else:
                displayType = "Database Record"
                displayTypeComment = "Attributes available as properties"

        # Avoid calling isCollection, since it would call isExisting -> _initConnection
        isCollection = primKey is None

        self._cache = {"contentLength": None,
                       "contentType": contentType,
                       "created": time.time(),
                       "displayName": self.name,
                       "etag": hashlib.md5().update(self.path).hexdigest(),
                       # "etag": md5.new(self.path).hexdigest(),
                       "modified": None,
                       "supportRanges": False,
                       "displayInfo": {"type": displayType,
                                       "typeComment": displayTypeComment,
                                       },
                       }

        # Some resource-only infos:
        if not isCollection:
            self._cache["modified"] = time.time()
        _logger.debug("---> _init, nc=%s" % self.provider._count_initConnection)

    def _getInfo(self, info):
        if self._cache is None:
            self._init()
        return self._cache.get(info)

    # Getter methods for standard live properties
    def getContentLength(self):
        return self._getInfo("contentLength")

    def getContentType(self):
        return self._getInfo("contentType")

    def getCreationDate(self):
        return self._getInfo("created")

    def getDisplayName(self):
        return self.name

    def getDisplayInfo(self):
        return self._getInfo("displayInfo")

    def getEtag(self):
        return self._getInfo("etag")

    def getLastModified(self):
        return self._getInfo("modified")

    def getMemberList(self):
        """Return list of (direct) collection member names (UTF-8 byte strings).

        See DAVResource.getMemberList()
        """
        members = []
        conn = self.provider._initConnection()
        try:
            tableName, primKey = self.provider._splitPath(self.path)
            if tableName is None:
                retlist = self.provider._listTables(conn)
                for name in retlist:
                    members.append(MySQLBrowserResource(self.provider,
                                                        util.joinUri(self.path, name),
                                                        True,
                                                        self.environ))
            elif primKey is None:
                pri_key = self.provider._findPrimaryKey(conn, tableName)
                if pri_key is not None:
                    retlist = self.provider._listFields(conn, tableName, pri_key)
                    for name in retlist:
                        members.append(MySQLBrowserResource(self.provider,
                                                            util.joinUri(self.path, name),
                                                            False,
                                                            self.environ))
                members.insert(0, MySQLBrowserResource(self.provider,
                                                       util.joinUri(self.path, "_ENTIRE_CONTENTS"),
                                                       False,
                                                       self.environ))
        finally:
            conn.close()
        return members

    def getContent(self):
        """Open content as a stream for reading.

        See DAVResource.getContent()
        """
        filestream = compat.StringIO()

        tableName, primKey = self.provider._splitPath(self.path)
        if primKey is not None:
            conn = self.provider._initConnection()
            listFields = self.provider._getFieldList(conn, tableName)
            csvwriter = csv.DictWriter(filestream, listFields, extrasaction="ignore")
            dictFields = {}
            for field_name in listFields:
                dictFields[field_name] = field_name
            csvwriter.writerow(dictFields)

            if primKey == "_ENTIRE_CONTENTS":
                cursor = conn.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * from " + self.provider._db + "." + tableName)
                result_set = cursor.fetchall()
                for row in result_set:
                    csvwriter.writerow(row)
                cursor.close()
            else:
                row = self.provider._getRecordByPrimaryKey(conn, tableName, primKey)
                if row is not None:
                    csvwriter.writerow(row)
            conn.close()

        # this suffices for small dbs, but
        # for a production big database, I imagine you would have a FileMixin that
        # does the retrieving and population even as the file object is being read
        filestream.seek(0)
        return filestream

    def getPropertyNames(self, isAllProp):
        """Return list of supported property names in Clark Notation.

        Return supported live and dead properties. (See also DAVProvider.getPropertyNames().)

        In addition, all table field names are returned as properties.
        """
        # Let default implementation return supported live and dead properties
        propNames = super(MySQLBrowserResource, self).getPropertyNames(isAllProp)
        # Add fieldnames as properties
        tableName, primKey = self.provider._splitPath(self.path)
        if primKey is not None:
            conn = self.provider._initConnection()
            fieldlist = self.provider._getFieldList(conn, tableName)
            for fieldname in fieldlist:
                propNames.append("{%s:}%s" % (tableName, fieldname))
            conn.close()
        return propNames

    def getPropertyValue(self, propname):
        """Return the value of a property.

        The base implementation handles:

        - ``{DAV:}lockdiscovery`` and ``{DAV:}supportedlock`` using the
          associated lock manager.
        - All other *live* properties (i.e. name starts with ``{DAV:}``) are
          delegated to self.getLivePropertyValue()
        - Finally, other properties are considered *dead*, and are handled  using
          the associated property manager, if one is present.
        """
        # Return table field as property
        tableName, primKey = self.provider._splitPath(self.path)
        if primKey is not None:
            ns, localName = util.splitNamespace(propname)
            if ns == (tableName + ":"):
                conn = self.provider._initConnection()
                fieldlist = self.provider._getFieldList(conn, tableName)
                if localName in fieldlist:
                    val = self.provider._getFieldByPrimaryKey(conn, tableName, primKey, localName)
                    conn.close()
                    return val
                conn.close()
        # else, let default implementation return supported live and dead properties
        return super(MySQLBrowserResource, self).getPropertyValue(propname)

    def setPropertyValue(self, propname, value, dryRun=False):
        """Set or remove property value.

        See DAVResource.setPropertyValue()
        """
        raise DAVError(HTTP_FORBIDDEN,
                       errcondition=PRECONDITION_CODE_ProtectedProperty)

# ============================================================================
# MySQLBrowserProvider
# ============================================================================


class MySQLBrowserProvider(DAVProvider):

    def __init__(self, host, user, passwd, db):
        super(MySQLBrowserProvider, self).__init__()
        self._host = host
        self._user = user
        self._passwd = passwd
        self._db = db
        self._count_initConnection = 0

    def __repr__(self):
        return "%s for db '%s' on '%s' (user: '%s')'" % (
            self.__class__.__name__, self._db, self._host, self._user)

    def _splitPath(self, path):
        """Return (tableName, primaryKey) tuple for a request path."""
        if path.strip() in (None, "", "/"):
            return (None, None)
        tableName, primKey = util.saveSplit(path.strip("/"), "/", 1)
#        _logger.debug("'%s' -> ('%s', '%s')" % (path, tableName, primKey))
        return (tableName, primKey)

    def _initConnection(self):
        self._count_initConnection += 1
        return MySQLdb.connect(host=self._host,
                               user=self._user,
                               passwd=self._passwd,
                               db=self._db)

    def _getFieldList(self, conn, table_name):
        retlist = []
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DESCRIBE " + table_name)
        result_set = cursor.fetchall()
        for row in result_set:
            retlist.append(row["Field"])
        cursor.close()
        return retlist

    def _isDataTypeNumeric(self, datatype):
        if datatype is None:
            return False
        # how many MySQL datatypes does it take to change a lig... I mean, store numbers
        numerictypes = ["BIGINT",
                        "INTT",
                        "MEDIUMINT",
                        "SMALLINT",
                        "TINYINT",
                        "BIT",
                        "DEC",
                        "DECIMAL",
                        "DOUBLE",
                        "FLOAT",
                        "REAL",
                        "DOUBLE PRECISION",
                        "INTEGER",
                        "NUMERIC"]
        datatype = datatype.upper()
        for numtype in numerictypes:
            if datatype.startswith(numtype):
                return True
        return False

    def _existsRecordByPrimaryKey(self, conn, table_name, pri_key_value):
        pri_key = None
        pri_field_type = None
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DESCRIBE " + table_name)
        result_set = cursor.fetchall()
        for row in result_set:
            if row["Key"] == "PRI":
                if pri_key is None:
                    pri_key = row["Field"]
                    pri_field_type = row["Type"]
                else:
                    return False  # more than one primary key - multipart key?
        cursor.close()

        isNumType = self._isDataTypeNumeric(pri_field_type)

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        if isNumType:
            cursor.execute("SELECT " + pri_key + " FROM " + self._db + "." +
                           table_name + " WHERE " + pri_key + " = " + pri_key_value)
        else:
            cursor.execute("SELECT " + pri_key + " FROM " + self._db + "." +
                           table_name + " WHERE " + pri_key + " = '" + pri_key_value + "'")
        row = cursor.fetchone()
        if row is None:
            cursor.close()
            return False
        cursor.close()
        return True

    def _getFieldByPrimaryKey(self, conn, table_name, pri_key_value, field_name):
        pri_key = None
        pri_field_type = None
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DESCRIBE " + table_name)
        result_set = cursor.fetchall()
        for row in result_set:
            if row["Key"] == "PRI":
                if pri_key is None:
                    pri_key = row["Field"]
                    pri_field_type = row["Type"]
                else:
                    return None  # more than one primary key - multipart key?
        cursor.close()

        isNumType = self._isDataTypeNumeric(pri_field_type)

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        if isNumType:
            cursor.execute("SELECT " + field_name + " FROM " + self._db + "." +
                           table_name + " WHERE " + pri_key + " = " + pri_key_value)
        else:
            cursor.execute("SELECT " + field_name + " FROM " + self._db + "." +
                           table_name + " WHERE " + pri_key + " = '" + pri_key_value + "'")
        row = cursor.fetchone()
        if row is None:
            cursor.close()
            return None
        val = compat.to_native(row[field_name])
        cursor.close()
        return val

    def _getRecordByPrimaryKey(self, conn, table_name, pri_key_value):
        dictRet = {}
        pri_key = None
        pri_field_type = None
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DESCRIBE " + table_name)
        result_set = cursor.fetchall()
        for row in result_set:
            if row["Key"] == "PRI":
                if pri_key is None:
                    pri_key = row["Field"]
                    pri_field_type = row["Type"]
                else:
                    return None  # more than one primary key - multipart key?
        cursor.close()

        isNumType = self._isDataTypeNumeric(pri_field_type)

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        if isNumType:
            cursor.execute("SELECT * FROM " + self._db + "." + table_name +
                           " WHERE " + pri_key + " = " + pri_key_value)
        else:
            cursor.execute("SELECT * FROM " + self._db + "." + table_name +
                           " WHERE " + pri_key + " = '" + pri_key_value + "'")
        row = cursor.fetchone()
        if row is None:
            cursor.close()
            return None
        for fname in row.keys():
            dictRet[fname] = compat.to_native(row[fname])
        cursor.close()
        return dictRet

    def _findPrimaryKey(self, conn, table_name):
        pri_key = None
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DESCRIBE " + table_name)
        result_set = cursor.fetchall()
        for row in result_set:
            fieldname = row["Field"]
            keyvalue = row["Key"]
            if keyvalue == "PRI":
                if pri_key is None:
                    pri_key = fieldname
                else:
                    return None  # more than one primary key - multipart key?
        cursor.close()
        return pri_key

    def _listFields(self, conn, table_name, field_name):
        retlist = []
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT " + field_name + " FROM " + self._db + "." + table_name)
        result_set = cursor.fetchall()
        for row in result_set:
            retlist.append(compat.to_native(row[field_name]))
        cursor.close()
        return retlist

    def _listTables(self, conn):
        retlist = []
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        result_set = cursor.fetchall()
        for row in result_set:
            retlist.append("%s" % (row[0]))
        cursor.close()
        return retlist

    def getResourceInst(self, path, environ):
        """Return info dictionary for path.

        See getResourceInst()
        """
        # TODO: calling exists() makes directory browsing VERY slow.
        #       At least compared to PyFileServer, which simply used string
        #       functions to get displayType and displayTypeComment
        self._count_getResourceInst += 1
        if not self.exists(path, environ):
            return None
        _tableName, primKey = self._splitPath(path)
        isCollection = primKey is None
        return MySQLBrowserResource(self, path, isCollection, environ)

    def exists(self, path, environ):
        tableName, primKey = self._splitPath(path)
        if tableName is None:
            return True

        try:
            conn = None
            conn = self._initConnection()
            # Check table existence:
            tbllist = self._listTables(conn)
            if tableName not in tbllist:
                return False
            # Check table key existence:
            if primKey and primKey != "_ENTIRE_CONTENTS":
                return self._existsRecordByPrimaryKey(conn, tableName, primKey)
            return True
        finally:
            if conn:
                conn.close()

    def isCollection(self, path, environ):
        _tableName, primKey = self._splitPath(path)
        return self.exists(path, environ) and primKey is None

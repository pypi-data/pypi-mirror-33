"""Miscellaneous goodies for psycopg2

This module is a generic place used to hold little helper functions
and classes until a better place in the distribution is found.
"""
# psycopg/extras.py - miscellaneous extra goodies for psycopg
#
# Copyright (C) 2003-2010 Federico Di Gregorio  <fog@debian.org>
#
# psycopg2 is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# In addition, as a special exception, the copyright holders give
# permission to link this program with the OpenSSL library (or with
# modified versions of OpenSSL that use the same license as OpenSSL),
# and distribute linked combinations including the two.
#
# You must obey the GNU Lesser General Public License in all respects for
# all of the code used other than OpenSSL.
#
# psycopg2 is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.

import os as _os
import sys as _sys
import time as _time
import re as _re

try:
    import logging as _logging
except:
    _logging = None

import psycopg2
from psycopg2 import extensions as _ext
from psycopg2.extensions import cursor as _cursor
from psycopg2.extensions import connection as _connection
from psycopg2.extensions import adapt as _A, quote_ident

from psycopg2._psycopg import (                             # noqa
    REPLICATION_PHYSICAL, REPLICATION_LOGICAL,
    ReplicationConnection as _replicationConnection,
    ReplicationCursor as _replicationCursor,
    ReplicationMessage)


# expose the json adaptation stuff into the module
from psycopg2._json import (                                # noqa
    json, Json, register_json, register_default_json, register_default_jsonb)


# Expose range-related objects
from psycopg2._range import (                               # noqa
    Range, NumericRange, DateRange, DateTimeRange, DateTimeTZRange,
    register_range, RangeAdapter, RangeCaster)


# Expose ipaddress-related objects
from psycopg2._ipaddress import register_ipaddress          # noqa


class DictCursorBase(_cursor):
    """Base class for all dict-like cursors."""

    def __init__(self, *args, **kwargs):
        if 'row_factory' in kwargs:
            row_factory = kwargs['row_factory']
            del kwargs['row_factory']
        else:
            raise NotImplementedError(
                "DictCursorBase can't be instantiated without a row factory.")
        super(DictCursorBase, self).__init__(*args, **kwargs)
        self._query_executed = 0
        self._prefetch = 0
        self.row_factory = row_factory

    def fetchone(self):
        if self._prefetch:
            res = super(DictCursorBase, self).fetchone()
        if self._query_executed:
            self._build_index()
        if not self._prefetch:
            res = super(DictCursorBase, self).fetchone()
        return res

    def fetchmany(self, size=None):
        if self._prefetch:
            res = super(DictCursorBase, self).fetchmany(size)
        if self._query_executed:
            self._build_index()
        if not self._prefetch:
            res = super(DictCursorBase, self).fetchmany(size)
        return res

    def fetchall(self):
        if self._prefetch:
            res = super(DictCursorBase, self).fetchall()
        if self._query_executed:
            self._build_index()
        if not self._prefetch:
            res = super(DictCursorBase, self).fetchall()
        return res

    def __iter__(self):
        try:
            if self._prefetch:
                res = super(DictCursorBase, self).__iter__()
                first = next(res)
            if self._query_executed:
                self._build_index()
            if not self._prefetch:
                res = super(DictCursorBase, self).__iter__()
                first = next(res)

            yield first
            while 1:
                yield next(res)
        except StopIteration:
            return


class DictConnection(_connection):
    """A connection that uses `DictCursor` automatically."""
    def cursor(self, *args, **kwargs):
        kwargs.setdefault('cursor_factory', DictCursor)
        return super(DictConnection, self).cursor(*args, **kwargs)


class DictCursor(DictCursorBase):
    """A cursor that keeps a list of column name -> index mappings."""

    def __init__(self, *args, **kwargs):
        kwargs['row_factory'] = DictRow
        super(DictCursor, self).__init__(*args, **kwargs)
        self._prefetch = 1

    def execute(self, query, vars=None):
        self.index = {}
        self._query_executed = 1
        return super(DictCursor, self).execute(query, vars)

    def callproc(self, procname, vars=None):
        self.index = {}
        self._query_executed = 1
        return super(DictCursor, self).callproc(procname, vars)

    def _build_index(self):
        if self._query_executed == 1 and self.description:
            for i in range(len(self.description)):
                self.index[self.description[i][0]] = i
            self._query_executed = 0


class DictRow(list):
    """A row object that allow by-column-name access to data."""

    __slots__ = ('_index',)

    def __init__(self, cursor):
        self._index = cursor.index
        self[:] = [None] * len(cursor.description)

    def __getitem__(self, x):
        if not isinstance(x, (int, slice)):
            x = self._index[x]
        return list.__getitem__(self, x)

    def __setitem__(self, x, v):
        if not isinstance(x, (int, slice)):
            x = self._index[x]
        list.__setitem__(self, x, v)

    def items(self):
        return list(self.items())

    def keys(self):
        return list(self._index.keys())

    def values(self):
        return tuple(self[:])

    def has_key(self, x):
        return x in self._index

    def get(self, x, default=None):
        try:
            return self[x]
        except:
            return default

    def iteritems(self):
        for n, v in self._index.items():
            yield n, list.__getitem__(self, v)

    def iterkeys(self):
        return iter(self._index.keys())

    def itervalues(self):
        return list.__iter__(self)

    def copy(self):
        return dict(iter(self.items()))

    def __contains__(self, x):
        return x in self._index

    def __getstate__(self):
        return self[:], self._index.copy()

    def __setstate__(self, data):
        self[:] = data[0]
        self._index = data[1]

    # drop the crusty Py2 methods
    if _sys.version_info[0] > 2:
        items = iteritems               # noqa
        keys = iterkeys                 # noqa
        values = itervalues             # noqa
        del iteritems, iterkeys, itervalues, has_key


class RealDictConnection(_connection):
    """A connection that uses `RealDictCursor` automatically."""
    def cursor(self, *args, **kwargs):
        kwargs.setdefault('cursor_factory', RealDictCursor)
        return super(RealDictConnection, self).cursor(*args, **kwargs)


class RealDictCursor(DictCursorBase):
    """A cursor that uses a real dict as the base type for rows.

    Note that this cursor is extremely specialized and does not allow
    the normal access (using integer indices) to fetched data. If you need
    to access database rows both as a dictionary and a list, then use
    the generic `DictCursor` instead of `!RealDictCursor`.
    """
    def __init__(self, *args, **kwargs):
        kwargs['row_factory'] = RealDictRow
        super(RealDictCursor, self).__init__(*args, **kwargs)
        self._prefetch = 0

    def execute(self, query, vars=None):
        self.column_mapping = []
        self._query_executed = 1
        return super(RealDictCursor, self).execute(query, vars)

    def callproc(self, procname, vars=None):
        self.column_mapping = []
        self._query_executed = 1
        return super(RealDictCursor, self).callproc(procname, vars)

    def _build_index(self):
        if self._query_executed == 1 and self.description:
            for i in range(len(self.description)):
                self.column_mapping.append(self.description[i][0])
            self._query_executed = 0


class RealDictRow(dict):
    """A `!dict` subclass representing a data record."""

    __slots__ = ('_column_mapping')

    def __init__(self, cursor):
        dict.__init__(self)
        # Required for named cursors
        if cursor.description and not cursor.column_mapping:
            cursor._build_index()

        self._column_mapping = cursor.column_mapping

    def __setitem__(self, name, value):
        if type(name) == int:
            name = self._column_mapping[name]
        return dict.__setitem__(self, name, value)

    def __getstate__(self):
        return (self.copy(), self._column_mapping[:])

    def __setstate__(self, data):
        self.update(data[0])
        self._column_mapping = data[1]


class NamedTupleConnection(_connection):
    """A connection that uses `NamedTupleCursor` automatically."""
    def cursor(self, *args, **kwargs):
        kwargs.setdefault('cursor_factory', NamedTupleCursor)
        return super(NamedTupleConnection, self).cursor(*args, **kwargs)


class NamedTupleCursor(_cursor):
    """A cursor that generates results as `~collections.namedtuple`.

    `!fetch*()` methods will return named tuples instead of regular tuples, so
    their elements can be accessed both as regular numeric items as well as
    attributes.

        >>> nt_cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        >>> rec = nt_cur.fetchone()
        >>> rec
        Record(id=1, num=100, data="abc'def")
        >>> rec[1]
        100
        >>> rec.data
        "abc'def"
    """
    Record = None

    def execute(self, query, vars=None):
        self.Record = None
        return super(NamedTupleCursor, self).execute(query, vars)

    def executemany(self, query, vars):
        self.Record = None
        return super(NamedTupleCursor, self).executemany(query, vars)

    def callproc(self, procname, vars=None):
        self.Record = None
        return super(NamedTupleCursor, self).callproc(procname, vars)

    def fetchone(self):
        t = super(NamedTupleCursor, self).fetchone()
        if t is not None:
            nt = self.Record
            if nt is None:
                nt = self.Record = self._make_nt()
            return nt._make(t)

    def fetchmany(self, size=None):
        ts = super(NamedTupleCursor, self).fetchmany(size)
        nt = self.Record
        if nt is None:
            nt = self.Record = self._make_nt()
        return list(map(nt._make, ts))

    def fetchall(self):
        ts = super(NamedTupleCursor, self).fetchall()
        nt = self.Record
        if nt is None:
            nt = self.Record = self._make_nt()
        return list(map(nt._make, ts))

    def __iter__(self):
        try:
            it = super(NamedTupleCursor, self).__iter__()
            t = next(it)

            nt = self.Record
            if nt is None:
                nt = self.Record = self._make_nt()

            yield nt._make(t)

            while 1:
                yield nt._make(next(it))
        except StopIteration:
            return

    try:
        from collections import namedtuple
    except ImportError as _exc:
        def _make_nt(self):
            raise self._exc
    else:
        def _make_nt(self, namedtuple=namedtuple):
            # ascii except alnum and underscore
            nochars = ' !"#$%&\'()*+,-./:;<=>?@[\\]^`{|}~'
            re_clean = _re.compile('[' + _re.escape(nochars) + ']')

            def f(s):
                s = re_clean.sub('_', s)
                # Python identifier cannot start with numbers, namedtuple fields
                # cannot start with underscore. So...
                if s[0] == '_' or '0' <= s[0] <= '9':
                    s = 'f' + s

                return s

            return namedtuple(
                "Record", [f(d[0]) for d in self.description or ()])


class LoggingConnection(_connection):
    """A connection that logs all queries to a file or logger__ object.

    .. __: http://docs.python.org/library/logging.html
    """

    def initialize(self, logobj):
        """Initialize the connection to log to `!logobj`.

        The `!logobj` parameter can be an open file object or a Logger
        instance from the standard logging module.
        """
        self._logobj = logobj
        if _logging and isinstance(logobj, _logging.Logger):
            self.log = self._logtologger
        else:
            self.log = self._logtofile

    def filter(self, msg, curs):
        """Filter the query before logging it.

        This is the method to overwrite to filter unwanted queries out of the
        log or to add some extra data to the output. The default implementation
        just does nothing.
        """
        return msg

    def _logtofile(self, msg, curs):
        msg = self.filter(msg, curs)
        if msg:
            if _sys.version_info[0] >= 3 and isinstance(msg, bytes):
                msg = msg.decode(_ext.encodings[self.encoding], 'replace')
            self._logobj.write(msg + _os.linesep)

    def _logtologger(self, msg, curs):
        msg = self.filter(msg, curs)
        if msg:
            self._logobj.debug(msg)

    def _check(self):
        if not hasattr(self, '_logobj'):
            raise self.ProgrammingError(
                "LoggingConnection object has not been initialize()d")

    def cursor(self, *args, **kwargs):
        self._check()
        kwargs.setdefault('cursor_factory', LoggingCursor)
        return super(LoggingConnection, self).cursor(*args, **kwargs)


class LoggingCursor(_cursor):
    """A cursor that logs queries using its connection logging facilities."""

    def execute(self, query, vars=None):
        try:
            return super(LoggingCursor, self).execute(query, vars)
        finally:
            self.connection.log(self.query, self)

    def callproc(self, procname, vars=None):
        try:
            return super(LoggingCursor, self).callproc(procname, vars)
        finally:
            self.connection.log(self.query, self)


class MinTimeLoggingConnection(LoggingConnection):
    """A connection that logs queries based on execution time.

    This is just an example of how to sub-class `LoggingConnection` to
    provide some extra filtering for the logged queries. Both the
    `initialize()` and `filter()` methods are overwritten to make sure
    that only queries executing for more than ``mintime`` ms are logged.

    Note that this connection uses the specialized cursor
    `MinTimeLoggingCursor`.
    """
    def initialize(self, logobj, mintime=0):
        LoggingConnection.initialize(self, logobj)
        self._mintime = mintime

    def filter(self, msg, curs):
        t = (_time.time() - curs.timestamp) * 1000
        if t > self._mintime:
            if _sys.version_info[0] >= 3 and isinstance(msg, bytes):
                msg = msg.decode(_ext.encodings[self.encoding], 'replace')
            return msg + _os.linesep + "  (execution time: %d ms)" % t

    def cursor(self, *args, **kwargs):
        kwargs.setdefault('cursor_factory', MinTimeLoggingCursor)
        return LoggingConnection.cursor(self, *args, **kwargs)


class MinTimeLoggingCursor(LoggingCursor):
    """The cursor sub-class companion to `MinTimeLoggingConnection`."""

    def execute(self, query, vars=None):
        self.timestamp = _time.time()
        return LoggingCursor.execute(self, query, vars)

    def callproc(self, procname, vars=None):
        self.timestamp = _time.time()
        return LoggingCursor.callproc(self, procname, vars)


class LogicalReplicationConnection(_replicationConnection):

    def __init__(self, *args, **kwargs):
        kwargs['replication_type'] = REPLICATION_LOGICAL
        super(LogicalReplicationConnection, self).__init__(*args, **kwargs)


class PhysicalReplicationConnection(_replicationConnection):

    def __init__(self, *args, **kwargs):
        kwargs['replication_type'] = REPLICATION_PHYSICAL
        super(PhysicalReplicationConnection, self).__init__(*args, **kwargs)


class StopReplication(Exception):
    """
    Exception used to break out of the endless loop in
    `~ReplicationCursor.consume_stream()`.

    Subclass of `~exceptions.Exception`.  Intentionally *not* inherited from
    `~psycopg2.Error` as occurrence of this exception does not indicate an
    error.
    """
    pass


class ReplicationCursor(_replicationCursor):
    """A cursor used for communication on replication connections."""

    def create_replication_slot(self, slot_name, slot_type=None, output_plugin=None):
        """Create streaming replication slot."""

        command = "CREATE_REPLICATION_SLOT %s " % quote_ident(slot_name, self)

        if slot_type is None:
            slot_type = self.connection.replication_type

        if slot_type == REPLICATION_LOGICAL:
            if output_plugin is None:
                raise psycopg2.ProgrammingError(
                    "output plugin name is required to create "
                    "logical replication slot")

            command += "LOGICAL %s" % quote_ident(output_plugin, self)

        elif slot_type == REPLICATION_PHYSICAL:
            if output_plugin is not None:
                raise psycopg2.ProgrammingError(
                    "cannot specify output plugin name when creating "
                    "physical replication slot")

            command += "PHYSICAL"

        else:
            raise psycopg2.ProgrammingError(
                "unrecognized replication type: %s" % repr(slot_type))

        self.execute(command)

    def drop_replication_slot(self, slot_name):
        """Drop streaming replication slot."""

        command = "DROP_REPLICATION_SLOT %s" % quote_ident(slot_name, self)
        self.execute(command)

    def start_replication(self, slot_name=None, slot_type=None, start_lsn=0,
                          timeline=0, options=None, decode=False):
        """Start replication stream."""

        command = "START_REPLICATION "

        if slot_type is None:
            slot_type = self.connection.replication_type

        if slot_type == REPLICATION_LOGICAL:
            if slot_name:
                command += "SLOT %s " % quote_ident(slot_name, self)
            else:
                raise psycopg2.ProgrammingError(
                    "slot name is required for logical replication")

            command += "LOGICAL "

        elif slot_type == REPLICATION_PHYSICAL:
            if slot_name:
                command += "SLOT %s " % quote_ident(slot_name, self)
            # don't add "PHYSICAL", before 9.4 it was just START_REPLICATION XXX/XXX

        else:
            raise psycopg2.ProgrammingError(
                "unrecognized replication type: %s" % repr(slot_type))

        if type(start_lsn) is str:
            lsn = start_lsn.split('/')
            lsn = "%X/%08X" % (int(lsn[0], 16), int(lsn[1], 16))
        else:
            lsn = "%X/%08X" % ((start_lsn >> 32) & 0xFFFFFFFF,
                               start_lsn & 0xFFFFFFFF)

        command += lsn

        if timeline != 0:
            if slot_type == REPLICATION_LOGICAL:
                raise psycopg2.ProgrammingError(
                    "cannot specify timeline for logical replication")

            command += " TIMELINE %d" % timeline

        if options:
            if slot_type == REPLICATION_PHYSICAL:
                raise psycopg2.ProgrammingError(
                    "cannot specify output plugin options for physical replication")

            command += " ("
            for k, v in options.items():
                if not command.endswith('('):
                    command += ", "
                command += "%s %s" % (quote_ident(k, self), _A(str(v)))
            command += ")"

        self.start_replication_expert(command, decode=decode)

    # allows replication cursors to be used in select.select() directly
    def fileno(self):
        return self.connection.fileno()


# a dbtype and adapter for Python UUID type

class UUID_adapter(object):
    """Adapt Python's uuid.UUID__ type to PostgreSQL's uuid__.

    .. __: http://docs.python.org/library/uuid.html
    .. __: http://www.postgresql.org/docs/current/static/datatype-uuid.html
    """

    def __init__(self, uuid):
        self._uuid = uuid

    def __conform__(self, proto):
        if proto is _ext.ISQLQuote:
            return self

    def getquoted(self):
        return ("'%s'::uuid" % self._uuid).encode('utf8')

    def __str__(self):
        return "'%s'::uuid" % self._uuid


def register_uuid(oids=None, conn_or_curs=None):
    """Create the UUID type and an uuid.UUID adapter.

    :param oids: oid for the PostgreSQL :sql:`uuid` type, or 2-items sequence
        with oids of the type and the array. If not specified, use PostgreSQL
        standard oids.
    :param conn_or_curs: where to register the typecaster. If not specified,
        register it globally.
    """

    import uuid

    if not oids:
        oid1 = 2950
        oid2 = 2951
    elif isinstance(oids, (list, tuple)):
        oid1, oid2 = oids
    else:
        oid1 = oids
        oid2 = 2951

    _ext.UUID = _ext.new_type((oid1, ), "UUID",
            lambda data, cursor: data and uuid.UUID(data) or None)
    _ext.UUIDARRAY = _ext.new_array_type((oid2,), "UUID[]", _ext.UUID)

    _ext.register_type(_ext.UUID, conn_or_curs)
    _ext.register_type(_ext.UUIDARRAY, conn_or_curs)
    _ext.register_adapter(uuid.UUID, UUID_adapter)

    return _ext.UUID


# a type, dbtype and adapter for PostgreSQL inet type

class Inet(object):
    """Wrap a string to allow for correct SQL-quoting of inet values.

    Note that this adapter does NOT check the passed value to make
    sure it really is an inet-compatible address but DOES call adapt()
    on it to make sure it is impossible to execute an SQL-injection
    by passing an evil value to the initializer.
    """
    def __init__(self, addr):
        self.addr = addr

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.addr)

    def prepare(self, conn):
        self._conn = conn

    def getquoted(self):
        obj = _A(self.addr)
        if hasattr(obj, 'prepare'):
            obj.prepare(self._conn)
        return obj.getquoted() + b"::inet"

    def __conform__(self, proto):
        if proto is _ext.ISQLQuote:
            return self

    def __str__(self):
        return str(self.addr)


def register_inet(oid=None, conn_or_curs=None):
    """Create the INET type and an Inet adapter.

    :param oid: oid for the PostgreSQL :sql:`inet` type, or 2-items sequence
        with oids of the type and the array. If not specified, use PostgreSQL
        standard oids.
    :param conn_or_curs: where to register the typecaster. If not specified,
        register it globally.
    """
    import warnings
    warnings.warn(
        "the inet adapter is deprecated, it's not very useful",
        DeprecationWarning)

    if not oid:
        oid1 = 869
        oid2 = 1041
    elif isinstance(oid, (list, tuple)):
        oid1, oid2 = oid
    else:
        oid1 = oid
        oid2 = 1041

    _ext.INET = _ext.new_type((oid1, ), "INET",
            lambda data, cursor: data and Inet(data) or None)
    _ext.INETARRAY = _ext.new_array_type((oid2, ), "INETARRAY", _ext.INET)

    _ext.register_type(_ext.INET, conn_or_curs)
    _ext.register_type(_ext.INETARRAY, conn_or_curs)

    return _ext.INET


def register_tstz_w_secs(oids=None, conn_or_curs=None):
    """The function used to register an alternate type caster for
    :sql:`TIMESTAMP WITH TIME ZONE` to deal with historical time zones with
    seconds in the UTC offset.

    These are now correctly handled by the default type caster, so currently
    the function doesn't do anything.
    """
    import warnings
    warnings.warn("deprecated", DeprecationWarning)


def wait_select(conn):
    """Wait until a connection or cursor has data available.

    The function is an example of a wait callback to be registered with
    `~psycopg2.extensions.set_wait_callback()`. This function uses
    :py:func:`~select.select()` to wait for data available.

    """
    import select
    from psycopg2.extensions import POLL_OK, POLL_READ, POLL_WRITE

    while 1:
        try:
            state = conn.poll()
            if state == POLL_OK:
                break
            elif state == POLL_READ:
                select.select([conn.fileno()], [], [])
            elif state == POLL_WRITE:
                select.select([], [conn.fileno()], [])
            else:
                raise conn.OperationalError("bad state from poll: %s" % state)
        except KeyboardInterrupt:
            conn.cancel()
            # the loop will be broken by a server error
            continue


def _solve_conn_curs(conn_or_curs):
    """Return the connection and a DBAPI cursor from a connection or cursor."""
    if conn_or_curs is None:
        raise psycopg2.ProgrammingError("no connection or cursor provided")

    if hasattr(conn_or_curs, 'execute'):
        conn = conn_or_curs.connection
        curs = conn.cursor(cursor_factory=_cursor)
    else:
        conn = conn_or_curs
        curs = conn.cursor(cursor_factory=_cursor)

    return conn, curs


class HstoreAdapter(object):
    """Adapt a Python dict to the hstore syntax."""
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def prepare(self, conn):
        self.conn = conn

        # use an old-style getquoted implementation if required
        if conn.server_version < 90000:
            self.getquoted = self._getquoted_8

    def _getquoted_8(self):
        """Use the operators available in PG pre-9.0."""
        if not self.wrapped:
            return b"''::hstore"

        adapt = _ext.adapt
        rv = []
        for k, v in self.wrapped.items():
            k = adapt(k)
            k.prepare(self.conn)
            k = k.getquoted()

            if v is not None:
                v = adapt(v)
                v.prepare(self.conn)
                v = v.getquoted()
            else:
                v = b'NULL'

            # XXX this b'ing is painfully inefficient!
            rv.append(b"(" + k + b" => " + v + b")")

        return b"(" + b'||'.join(rv) + b")"

    def _getquoted_9(self):
        """Use the hstore(text[], text[]) function."""
        if not self.wrapped:
            return b"''::hstore"

        k = _ext.adapt(list(self.wrapped.keys()))
        k.prepare(self.conn)
        v = _ext.adapt(list(self.wrapped.values()))
        v.prepare(self.conn)
        return b"hstore(" + k.getquoted() + b", " + v.getquoted() + b")"

    getquoted = _getquoted_9

    _re_hstore = _re.compile(r"""
        # hstore key:
        # a string of normal or escaped chars
        "((?: [^"\\] | \\. )*)"
        \s*=>\s* # hstore value
        (?:
            NULL # the value can be null - not catched
            # or a quoted string like the key
            | "((?: [^"\\] | \\. )*)"
        )
        (?:\s*,\s*|$) # pairs separated by comma or end of string.
    """, _re.VERBOSE)

    @classmethod
    def parse(self, s, cur, _bsdec=_re.compile(r"\\(.)")):
        """Parse an hstore representation in a Python string.

        The hstore is represented as something like::

            "a"=>"1", "b"=>"2"

        with backslash-escaped strings.
        """
        if s is None:
            return None

        rv = {}
        start = 0
        for m in self._re_hstore.finditer(s):
            if m is None or m.start() != start:
                raise psycopg2.InterfaceError(
                    "error parsing hstore pair at char %d" % start)
            k = _bsdec.sub(r'\1', m.group(1))
            v = m.group(2)
            if v is not None:
                v = _bsdec.sub(r'\1', v)

            rv[k] = v
            start = m.end()

        if start < len(s):
            raise psycopg2.InterfaceError(
                "error parsing hstore: unparsed data after char %d" % start)

        return rv

    @classmethod
    def parse_unicode(self, s, cur):
        """Parse an hstore returning unicode keys and values."""
        if s is None:
            return None

        s = s.decode(_ext.encodings[cur.connection.encoding])
        return self.parse(s, cur)

    @classmethod
    def get_oids(self, conn_or_curs):
        """Return the lists of OID of the hstore and hstore[] types.
        """
        conn, curs = _solve_conn_curs(conn_or_curs)

        # Store the transaction status of the connection to revert it after use
        conn_status = conn.status

        # column typarray not available before PG 8.3
        typarray = conn.server_version >= 80300 and "typarray" or "NULL"

        rv0, rv1 = [], []

        # get the oid for the hstore
        curs.execute("""\
SELECT t.oid, %s
FROM pg_type t JOIN pg_namespace ns
    ON typnamespace = ns.oid
WHERE typname = 'hstore';
""" % typarray)
        for oids in curs:
            rv0.append(oids[0])
            rv1.append(oids[1])

        # revert the status of the connection as before the command
        if (conn_status != _ext.STATUS_IN_TRANSACTION
        and not conn.autocommit):
            conn.rollback()

        return tuple(rv0), tuple(rv1)


def register_hstore(conn_or_curs, globally=False, str=False,
                    oid=None, array_oid=None):
    r"""Register adapter and typecaster for `!dict`\-\ |hstore| conversions.

    :param conn_or_curs: a connection or cursor: the typecaster will be
        registered only on this object unless *globally* is set to `!True`
    :param globally: register the adapter globally, not only on *conn_or_curs*
    :param unicode: if `!True`, keys and values returned from the database
        will be `!unicode` instead of `!str`. The option is not available on
        Python 3
    :param oid: the OID of the |hstore| type if known. If not, it will be
        queried on *conn_or_curs*.
    :param array_oid: the OID of the |hstore| array type if known. If not, it
        will be queried on *conn_or_curs*.

    The connection or cursor passed to the function will be used to query the
    database and look for the OID of the |hstore| type (which may be different
    across databases). If querying is not desirable (e.g. with
    :ref:`asynchronous connections <async-support>`) you may specify it in the
    *oid* parameter, which can be found using a query such as :sql:`SELECT
    'hstore'::regtype::oid`. Analogously you can obtain a value for *array_oid*
    using a query such as :sql:`SELECT 'hstore[]'::regtype::oid`.

    Note that, when passing a dictionary from Python to the database, both
    strings and unicode keys and values are supported. Dictionaries returned
    from the database have keys/values according to the *unicode* parameter.

    The |hstore| contrib module must be already installed in the database
    (executing the ``hstore.sql`` script in your ``contrib`` directory).
    Raise `~psycopg2.ProgrammingError` if the type is not found.
    """
    if oid is None:
        oid = HstoreAdapter.get_oids(conn_or_curs)
        if oid is None or not oid[0]:
            raise psycopg2.ProgrammingError(
                "hstore type not found in the database. "
                "please install it from your 'contrib/hstore.sql' file")
        else:
            array_oid = oid[1]
            oid = oid[0]

    if isinstance(oid, int):
        oid = (oid,)

    if array_oid is not None:
        if isinstance(array_oid, int):
            array_oid = (array_oid,)
        else:
            array_oid = tuple([x for x in array_oid if x])

    # create and register the typecaster
    if _sys.version_info[0] < 3 and str:
        cast = HstoreAdapter.parse_unicode
    else:
        cast = HstoreAdapter.parse

    HSTORE = _ext.new_type(oid, "HSTORE", cast)
    _ext.register_type(HSTORE, not globally and conn_or_curs or None)
    _ext.register_adapter(dict, HstoreAdapter)

    if array_oid:
        HSTOREARRAY = _ext.new_array_type(array_oid, "HSTOREARRAY", HSTORE)
        _ext.register_type(HSTOREARRAY, not globally and conn_or_curs or None)


class CompositeCaster(object):
    """Helps conversion of a PostgreSQL composite type into a Python object.

    The class is usually created by the `register_composite()` function.
    You may want to create and register manually instances of the class if
    querying the database at registration time is not desirable (such as when
    using an :ref:`asynchronous connections <async-support>`).

    """
    def __init__(self, name, oid, attrs, array_oid=None, schema=None):
        self.name = name
        self.schema = schema
        self.oid = oid
        self.array_oid = array_oid

        self.attnames = [a[0] for a in attrs]
        self.atttypes = [a[1] for a in attrs]
        self._create_type(name, self.attnames)
        self.typecaster = _ext.new_type((oid,), name, self.parse)
        if array_oid:
            self.array_typecaster = _ext.new_array_type(
                (array_oid,), "%sARRAY" % name, self.typecaster)
        else:
            self.array_typecaster = None

    def parse(self, s, curs):
        if s is None:
            return None

        tokens = self.tokenize(s)
        if len(tokens) != len(self.atttypes):
            raise psycopg2.DataError(
                "expecting %d components for the type %s, %d found instead" %
                (len(self.atttypes), self.name, len(tokens)))

        values = [curs.cast(oid, token)
            for oid, token in zip(self.atttypes, tokens)]

        return self.make(values)

    def make(self, values):
        """Return a new Python object representing the data being casted.

        *values* is the list of attributes, already casted into their Python
        representation.

        You can subclass this method to :ref:`customize the composite cast
        <custom-composite>`.
        """

        return self._ctor(values)

    _re_tokenize = _re.compile(r"""
  \(? ([,)])                        # an empty token, representing NULL
| \(? " ((?: [^"] | "")*) " [,)]    # or a quoted string
| \(? ([^",)]+) [,)]                # or an unquoted string
    """, _re.VERBOSE)

    _re_undouble = _re.compile(r'(["\\])\1')

    @classmethod
    def tokenize(self, s):
        rv = []
        for m in self._re_tokenize.finditer(s):
            if m is None:
                raise psycopg2.InterfaceError("can't parse type: %r" % s)
            if m.group(1) is not None:
                rv.append(None)
            elif m.group(2) is not None:
                rv.append(self._re_undouble.sub(r"\1", m.group(2)))
            else:
                rv.append(m.group(3))

        return rv

    def _create_type(self, name, attnames):
        try:
            from collections import namedtuple
        except ImportError:
            self.type = tuple
            self._ctor = self.type
        else:
            self.type = namedtuple(name, attnames)
            self._ctor = self.type._make

    @classmethod
    def _from_db(self, name, conn_or_curs):
        """Return a `CompositeCaster` instance for the type *name*.

        Raise `ProgrammingError` if the type is not found.
        """
        conn, curs = _solve_conn_curs(conn_or_curs)

        # Store the transaction status of the connection to revert it after use
        conn_status = conn.status

        # Use the correct schema
        if '.' in name:
            schema, tname = name.split('.', 1)
        else:
            tname = name
            schema = 'public'

        # column typarray not available before PG 8.3
        typarray = conn.server_version >= 80300 and "typarray" or "NULL"

        # get the type oid and attributes
        curs.execute("""\
SELECT t.oid, %s, attname, atttypid
FROM pg_type t
JOIN pg_namespace ns ON typnamespace = ns.oid
JOIN pg_attribute a ON attrelid = typrelid
WHERE typname = %%s AND nspname = %%s
    AND attnum > 0 AND NOT attisdropped
ORDER BY attnum;
""" % typarray, (tname, schema))

        recs = curs.fetchall()

        # revert the status of the connection as before the command
        if (conn_status != _ext.STATUS_IN_TRANSACTION
        and not conn.autocommit):
            conn.rollback()

        if not recs:
            raise psycopg2.ProgrammingError(
                "PostgreSQL type '%s' not found" % name)

        type_oid = recs[0][0]
        array_oid = recs[0][1]
        type_attrs = [(r[2], r[3]) for r in recs]

        return self(tname, type_oid, type_attrs,
            array_oid=array_oid, schema=schema)


def register_composite(name, conn_or_curs, globally=False, factory=None):
    """Register a typecaster to convert a composite type into a tuple.

    :param name: the name of a PostgreSQL composite type, e.g. created using
        the |CREATE TYPE|_ command
    :param conn_or_curs: a connection or cursor used to find the type oid and
        components; the typecaster is registered in a scope limited to this
        object, unless *globally* is set to `!True`
    :param globally: if `!False` (default) register the typecaster only on
        *conn_or_curs*, otherwise register it globally
    :param factory: if specified it should be a `CompositeCaster` subclass: use
        it to :ref:`customize how to cast composite types <custom-composite>`
    :return: the registered `CompositeCaster` or *factory* instance
        responsible for the conversion
    """
    if factory is None:
        factory = CompositeCaster

    caster = factory._from_db(name, conn_or_curs)
    _ext.register_type(caster.typecaster, not globally and conn_or_curs or None)

    if caster.array_typecaster is not None:
        _ext.register_type(
            caster.array_typecaster, not globally and conn_or_curs or None)

    return caster


def _paginate(seq, page_size):
    """Consume an iterable and return it in chunks.

    Every chunk is at most `page_size`. Never return an empty chunk.
    """
    page = []
    it = iter(seq)
    while 1:
        try:
            for i in range(page_size):
                page.append(next(it))
            yield page
            page = []
        except StopIteration:
            if page:
                yield page
            return


def execute_batch(cur, sql, argslist, page_size=100):
    r"""Execute groups of statements in fewer server roundtrips.

    Execute *sql* several times, against all parameters set (sequences or
    mappings) found in *argslist*.

    The function is semantically similar to

    .. parsed-literal::

        *cur*\.\ `~cursor.executemany`\ (\ *sql*\ , *argslist*\ )

    but has a different implementation: Psycopg will join the statements into
    fewer multi-statement commands, each one containing at most *page_size*
    statements, resulting in a reduced number of server roundtrips.

    After the execution of the function the `cursor.rowcount` property will
    **not** contain a total result.

    """
    for page in _paginate(argslist, page_size=page_size):
        sqls = [cur.mogrify(sql, args) for args in page]
        cur.execute(b";".join(sqls))


def execute_values(cur, sql, argslist, template=None, page_size=100):
    '''Execute a statement using :sql:`VALUES` with a sequence of parameters.

    :param cur: the cursor to use to execute the query.

    :param sql: the query to execute. It must contain a single ``%s``
        placeholder, which will be replaced by a `VALUES list`__.
        Example: ``"INSERT INTO mytable (id, f1, f2) VALUES %s"``.

    :param argslist: sequence of sequences or dictionaries with the arguments
        to send to the query. The type and content must be consistent with
        *template*.

    :param template: the snippet to merge to every item in *argslist* to
        compose the query.

        - If the *argslist* items are sequences it should contain positional
          placeholders (e.g. ``"(%s, %s, %s)"``, or ``"(%s, %s, 42)``" if there
          are constants value...).

        - If the *argslist* items are mappings it should contain named
          placeholders (e.g. ``"(%(id)s, %(f1)s, 42)"``).

        If not specified, assume the arguments are sequence and use a simple
        positional template (i.e.  ``(%s, %s, ...)``), with the number of
        placeholders sniffed by the first element in *argslist*.

    :param page_size: maximum number of *argslist* items to include in every
        statement. If there are more items the function will execute more than
        one statement.

    .. __: https://www.postgresql.org/docs/current/static/queries-values.html

    After the execution of the function the `cursor.rowcount` property will
    **not** contain a total result.

    While :sql:`INSERT` is an obvious candidate for this function it is
    possible to use it with other statements, for example::

        >>> cur.execute(
        ... "create table test (id int primary key, v1 int, v2 int)")

        >>> execute_values(cur,
        ... "INSERT INTO test (id, v1, v2) VALUES %s",
        ... [(1, 2, 3), (4, 5, 6), (7, 8, 9)])

        >>> execute_values(cur,
        ... """UPDATE test SET v1 = data.v1 FROM (VALUES %s) AS data (id, v1)
        ... WHERE test.id = data.id""",
        ... [(1, 20), (4, 50)])

        >>> cur.execute("select * from test order by id")
        >>> cur.fetchall()
        [(1, 20, 3), (4, 50, 6), (7, 8, 9)])

    '''
    # we can't just use sql % vals because vals is bytes: if sql is bytes
    # there will be some decoding error because of stupid codec used, and Py3
    # doesn't implement % on bytes.
    if not isinstance(sql, bytes):
        sql = sql.encode(_ext.encodings[cur.connection.encoding])
    pre, post = _split_sql(sql)

    for page in _paginate(argslist, page_size=page_size):
        if template is None:
            template = b'(' + b','.join([b'%s'] * len(page[0])) + b')'
        parts = pre[:]
        for args in page:
            parts.append(cur.mogrify(template, args))
            parts.append(b',')
        parts[-1:] = post
        cur.execute(b''.join(parts))


def _split_sql(sql):
    """Split *sql* on a single ``%s`` placeholder.

    Split on the %s, perform %% replacement and return pre, post lists of
    snippets.
    """
    curr = pre = []
    post = []
    tokens = _re.split(br'(%.)', sql)
    for token in tokens:
        if len(token) != 2 or token[:1] != b'%':
            curr.append(token)
            continue

        if token[1:] == b's':
            if curr is pre:
                curr = post
            else:
                raise ValueError(
                    "the query contains more than one '%s' placeholder")
        elif token[1:] == b'%':
            curr.append(b'%')
        else:
            raise ValueError("unsupported format character: '%s'"
                % token[1:].decode('ascii', 'replace'))

    if curr is pre:
        raise ValueError("the query doesn't contain any '%s' placeholder")

    return pre, post

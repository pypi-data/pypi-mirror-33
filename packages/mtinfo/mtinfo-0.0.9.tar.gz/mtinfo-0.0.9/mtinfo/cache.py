import copy, threading, json, os
import sqlite3

from stat import (
    S_IRUSR,
    S_IWUSR
)

from unnamed.logging import (
    Logger
)

logger = Logger(__name__)

STORAGE_SCHEMA = {
    'tvmaze': [
        { 'k' : 'id', 't': 'integer', 'f': 'index'},
        { 'k' : 'name', 't': 'text', 'f': 'text'},
        { 'k' : 'country', 't': 'text', 'f': 'text'},
        { 'k' : 'language', 't': 'text', 'f': 'text'},
    ],
}


class IStorException(Exception):
    pass


class IStor:

    def __init__(self, path, schema):

        self._path = path
        
        conn = self.connect()

        try:
            c = conn.cursor()

            for k, v in self._schema.items():
                s = ''
                for i, d in enumerate(v):
                    if i > 0:
                        s += ','
                    s += '{} {} {} NOT NULL DEFAULT \'{}\''.format(
                        d['k'],
                        d['t'],
                        'PRIMARY KEY' if d['f'] == 'index' else '',
                        '{}' if d['f'] == 'json' else ''
                    )

                c.execute('CREATE TABLE IF NOT EXISTS {} ({})'.format(k, s))

            for k, v in self._schema.items():
                t = c.execute('PRAGMA table_info({})'.format(k))

                _d = {}
                for r in t:
                    _d[r[1]] = True

                for i, d in enumerate(v):
                    if not d['k'] in _d:

                        if d['f'] == 'index':
                            raise IStorException('Cannot add index column to table')

                        s = 'ALTER TABLE {} ADD COLUMN {} {} NOT NULL DEFAULT \'{}\''.format(
                            k,
                            d['k'],
                            d['t'],
                            '{}' if d['f'] == 'json' else ''
                        )

                        c.execute(s)

        finally:
            conn.close()

        os.chmod(self._path, S_IRUSR | S_IWUSR)

        self._data = {}
        self._lock = threading.RLock()

        self.loadall()

    def connect(self):
        return sqlite3.connect(self._path)

    def loadall(self):

        with self._lock:
            conn = self.connect()
            try:
                c = conn.cursor()

                for k in self._schema:
                    self.load(c, k)
            finally:
                conn.close()

        # print(self._data)

    def load(self, cursor, table):

        with self._lock:
            schema = self._schema[table]

            r = {}

            cnt = 0

            for row in cursor.execute('SELECT * FROM {}'.format(table)):
                out = {}
                index = None

                cnt += 1

                # logger.debug(str(self), 'ROW: {}'.format(row))

                for i, v in enumerate(list(row)):

                    # logger.debug(str(self), 'ROW: {}'.format(i))

                    c = schema[i]
                    if c['f'] == 'index':
                        if index:
                            raise IStorException('Bad storage schema: {} (multiple indexes defined)'.format(table))
                        index = v
                    elif c['f'] == 'json':
                        v = json.loads(v)

                    out[c['k']] = v

                if not index:
                    raise IStorException('Bad storage schema: {} (no index defined)'.format(table))

                r[index] = out

            logger.debug(str(self), 'Loaded {} items from {}'.format(cnt, table))

            self._data[table] = r

        # print(self._data)

    def savetable(self, table):
        with self._lock:
            conn = self.connect()
            try:
                c = conn.cursor()

                for k in self._data[table]:
                    self.save(c, table, k)

                conn.commit()
            finally:
                conn.close()

    def save(self, cursor, table, key):

        with self._lock:
            schema = self._schema[table]

            r = self._data[table][key]

            c = ''
            v = ''

            out = []

            for i, d in enumerate(schema):

                if i > 0:
                    c += ','
                    v += ','

                k = d['k']
                c += k

                if d['f'] == 'json':
                    out.append(json.dumps(r[k], ensure_ascii = False))
                else:
                    out.append(str(r[k]))

                v += '?'

            outstr = 'INSERT OR REPLACE INTO {} ({}) VALUES({})'.format(
                        table, c, v
                    )

            cursor.execute (
                outstr,
                tuple(out)
            )

    def schema_find_item(self, table, k):
        schema = self._schema[table]

        for i in schema:
            if i['k'] == k:
                return i

    def schema_find_f(self, table, f):
        schema = self._schema[table]

        for i in schema:
            if i['f'] == f:
                return i

    def batch_add(self, table, data):
        with self._lock:
            conn = self.connect()
            try:
                for v in data:
                    key = self._add(table, **v)
                    self.save(conn.cursor(), table, key)

                conn.commit()
            finally:
                conn.close()

    def _add(self, table, **kwargs):
        schema = self._schema[table]

        key = None
        out = {}

        for i in schema:
            k = i['k']

            if not k in kwargs:
                raise IStorException('Schema validation failed: missing item \'{}\''.format(k))

            f = i['f']
            v = kwargs[k]

            if f == 'index':
                key = v

            out[k] = v

        if key == None:
            raise IStorException('chema validation failed: missing index')

        self._data[table][key] = out

        return key

    def add(self, table, **kwargs):
        with self._lock:
            key = self._add(table, **kwargs)

            conn = self.connect()
            try:
                self.save(conn.cursor(), table, key)
                conn.commit()
            finally:
                conn.close()

    def rem(self, table, key):
        with self._lock:
            index = self.schema_find_f(table, 'index')['k']

            del self._data[table][key]

            conn = self.connect()
            try:
                c = conn.cursor()

                outstr = 'DELETE FROM {} WHERE {} = ?'.format(
                            table,
                            index
                        )

                c.execute (
                    outstr,
                    tuple([key])
                )

                conn.commit()
            finally:
                conn.close()

    def set(self, table, key, **kwargs):

        with self._lock:

            self.cache_set(table, key, **kwargs)

            conn = self.connect()
            try:
                self.save(conn.cursor(), table, key)
                conn.commit()
            finally:
                conn.close()

    def cache_set(self, table, key, **kwargs):
        with self._lock:
            r = self._data[table]

            if not key in r:
                raise IStorException('Entry \'{}\' doesn\'t exist'.format(key))

            r = r[key]

            for k, v in kwargs.items():
                i = self.schema_find_item(table, k)

                if not i:
                    raise IStorException('Schema has no item \'{}\' defined'.format(k))

                if i['f'] == 'index':
                    raise IStorException('May not set value of an index \'{}\''.format(k))

                r[k] = v

    def gettable(self, table):
        with self._lock:
            return copy.deepcopy(self._data[table])

    def getkey(self, table, key):
        with self._lock:
            r = self._data[table]

            if not key in r:
                return None

            return copy.deepcopy(r[key])

    def get(self, table, key, column):
        with self._lock:
            r = self._data[table]

            if not key in r:
                return None

            r = r[key]

            if not column in r:
                return None

            return r[column]

    def key_exists(self, table, key):
        with self._lock:
            return key in self._data[table]

    def enum(self, table, f):
        with self._lock:
            r = self._data[table]

            for k, v in r.items():
                f(k, v)

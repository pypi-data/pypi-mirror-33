# -*- coding: UTF-8 -*
'''
Created on 2018-06-15

@author: trb
'''

from pymongo import ASCENDING, DESCENDING
import six


class Manager(object):
    def __init__(self, db=None, model=None):
        self.db = db
        self.model = model

    def find(self, *args, **kwargs):
        query = QuerySet(self)
        if kwargs:
            query = query.find(*args, **kwargs)
        return query

    @property
    def colname(self):
        '''collection name'''
        return getattr(self.model, '__table__', self.model.__name__).lower()

    def all(self):
        return self.find().all()

    def get(self, *args, **kwargs):
        return self.find().get(*args, **kwargs)

    def save(self, obj, db=None):
        data = obj.data
        if '_id' in data:
            (db or self.db)[self.colname].save(data)
        else:
            docid = (db or self.db)[self.colname].insert(data)
            data['_id'] = docid

    def unset(self, filter, fields, db=None):
        (db or self.db)[self.colname].update(filter, {'$unset': {k: "" for k in fields}})

    def __repr__(self):
        return '%s@%s#%s' % (self.__class__.__name__, self.db, self.model)

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__str__()

    def _wrap_query(self, q):
        return q


class QuerySet(object):
    def __init__(self, manager=None):
        self.manager = manager
        self.chain = []
        self.sort = None

    def __copy__(self):
        query = type(self)(self.manager)
        query.chain = [r for r in self.chain]
        query.sort = self.sort
        return query

    def _wrap_query(self, q):
        return self.manager._wrap_query(q)

    def find(self, *args, **kwargs):
        query = self.__copy__()
        if args:
            query.chain.append(self._wrap_query(args[0]))
        if kwargs:
            query.chain.append(self._wrap_query(kwargs))
        return query

    def first(self):
        return self.new_obj(data=self.col.find_one(self.query))

    def delete(self):
        return self.col.remove(self.query)

    def exists(self):
        return True if self.count() else False

    def count(self):
        return self.col.find(self.query).count()

    def all(self):
        return list(self)

    def get(self, *args, **kwargs):
        return self.find(_id=(args[0])).first() if args else self.find(**kwargs).first()

    def update(self, *args, **kwargs):
        pass

    @property
    def col(self):
        return self.manager.db[self.manager.colname]

    @property
    def query(self):
        from bson import ObjectId
        q = {}
        for c in self.chain:
            if c.get('_id') and isinstance(c['_id'], basestring):
                q.update(c)
                q['_id'] = ObjectId(c['_id'])
            else:
                q.update(c)
        return q

    def to_json(self):
        return list(self)

    def new_obj(self, data=None):
        return self.manager.model(data) if data != None else None

    def get_cursor(self):
        cursor = self.col.find(self.query)
        if self.sort:
            sorts = [(f[1:], DESCENDING) if f[0] == '-' else (f, ASCENDING) for f in self.sort]
            if len(sorts):
                cursor = cursor.sort(sorts)
            else:
                cursor = cursor.sort(*sorts[0])
        return cursor

    def __iter__(self):
        for data in self.get_cursor():
            yield self.new_obj(data=data)

    def __getitem__(self, item):
        if type(item) == slice:
            return map(self.new_obj, self.get_cursor()[item])
        else:
            return self.new_obj(self.get_cursor()[item])

    def order_by(self, *args):
        query = self.__copy__()
        query.sort = args
        return query


class BaseDocument(type):
    def __new__(cls, name, parents, attrs):
        ntype = type.__new__(cls, name, parents, attrs)
        ntype.objects = type(ntype.objects)(getattr(ntype, 'db', None), ntype)
        return ntype

    objects = Manager(None, None)


class Document(six.with_metaclass(BaseDocument)):
    def __init__(self, *args, **kwargs):
        if args:
            self.data = args[0]
        else:
            self.data = kwargs

    def __getitem__(self, key):
        # return self.data.get(key)
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, item):
        return self.data.__contains__(item)

    def get(self, key, d=None):
        return self.data.get(key, d)

    def __repr__(self):
        return '%s[%s]' % (self.__class__.__name__, self.data)

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__str__()

    def to_json(self):
        return self.data

    def save(self, db=None):
        self.objects.save(self)

    def update(self, d):
        self.data.update(d)

    @property
    def id(self):
        return self.data['_id'] if self.data and '_id' in self.data else None

    @id.setter
    def id(self, val):
        if self.data and '_id' in self.data:
            del self.data['_id']

    def unset(self, keys, db=None):
        print 'un', keys
        if keys and self.id:
            from bson import ObjectId
            self.objects.unset({'_id': ObjectId(self.id) if isinstance(self.id, basestring) else self.id}, keys, db=db)

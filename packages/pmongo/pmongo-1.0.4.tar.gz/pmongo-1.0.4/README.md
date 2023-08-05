PMongo
===============
A small Python MongoDB Document-Based access engine.

Install
===============
```
 pip install pmongo
```

Useage
===============
```python
# base use

# import
from pmongo.document import Document
from pmongo.utils import get_mongo_db

db = get_mongo_db(dbname='test')


# define document class
class Data(Document):
    db = db


# new a instance
d1 = Data()

# set data and save
d1['grade'] = 2
d1['name'] = 'Tom'
d1['age'] = 8
d1.save()

d2 = Data()
d2['grade'] = 2
d2['name'] = 'Lucy'
d2['age'] = 7
d2.save()

# display document ObjectId
print 'd1.id:', d1.id

# query
print 'grade=2:', Data.objects.find(grade=2).all()

# query count
print 'count of grade=2:', Data.objects.find(grade=2).count()

# change
d2['grade'] = 1
d2.save()

print 'count of grade=2:', Data.objects.find(grade=2).count()

# delete document
Data.objects.find(grade=2).delete()


print '-------'

# django like query
from pmongo.query import QueryManger


class Data2(Document):
    db = db
    objects = QueryManger()


Data2(age=10, name='Jone').save()
Data2(age=15, name='Jack').save()

print 'age>=10:', Data2.objects.find(age__gte=10).count()
print 'age>11:', Data2.objects.find(age__gt=11).count()

Data2.objects.find().delete()

```

Output:

```
d1.id: 5b2bad8b2801ca156e7aa9d8
grade=2: [Data[{u'grade': 2, u'age': 8, u'_id': ObjectId('5b2bad8b2801ca156e7aa9d8'), u'name': u'Tom'}], Data[{u'grade': 2, u'age': 7, u'_id': ObjectId('5b2bad8b2801ca156e7aa9d9'), u'name': u'Lucy'}]]
count of grade=2: 2
count of grade=2: 1
-------
age>=10: 2
age>11: 1
```
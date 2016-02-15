"""
Just to test database functions,
outside of Flask.

We want to open our MongoDB database,
insert some memos, and read them back
"""
import arrow

import sys

# Mongo database
from pymongo import MongoClient
import CONFIG

try: 
    #dbclient = MongoClient(CONFIG.MONGO_URL)
    #db = dbclient.memos
    client = MongoClient(CONFIG.MONGO_URI)
    db = client.get_default_database( )
    collection = db['dated']

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)
'''
#
# Insertions:  I commented these out after the first
# run successfuly inserted them
# 

record = { "type": "dated_memo", 
           "date":  arrow.utcnow().naive,
           "text": "This is a sample memo"
          }
collection.insert(record)

record = { "type": "dated_memo", 
           "date":  arrow.utcnow().replace(days=+1).naive,
           "text": "Sample one day later"
          }
collection.insert(record)

#
# Read database --- May be useful to see what is in there,
# even after you have a working 'insert' operation in the flask app,
# but they aren't very readable.  If you have more than a couple records,
# you'll want a loop for printing them in a nicer format. 
#

record = { "type": "dated_memo", 
           "date":  arrow.utcnow().replace(days=+2).naive,
           "text": "test"
          }
collection.insert(record)

collection.delete_one({'text':'test'})
#Test deletion

records = [ ] 
for record in collection.find( { "type": "dated_memo" } ):
   records.append(
        { "type": record['type'],
          "date": arrow.get(record['date']).to('local').isoformat(),
           "text": record['text']
    })

print(records)

collection.delete_one({'text':'test'})

records = [ ] 
for record in collection.find( { "type": "dated_memo" } ):
   records.append(
        { "type": record['type'],
          "date": arrow.get(record['date']).to('local').isoformat(),
           "text": record['text']
    })

print(records)
'''
#Test deletion

'''
d = arrow.utcnow().replace(days=+2)
print(d.naive)
print(d)
print(d.to('local').isoformat())
print(d.to('local').to('local'))
e = arrow.get('2016-02-14','YYYY-MM-DD')
print(e)
print(e.isoformat())
print(e.naive)
print(arrow.get(e.naive).to('local'))
print(arrow.get('2016-02-14T00:00:00+00:00').to('local').isoformat())

# Used for testing various cases in arrow, to understand
# how formatting and timezones
'''
for record in collection.find( { "type": "dated_memo" } ):
    print(record['_id'])
import logging, os, math, re
from os import getenv
from sqlalchemy import create_engine
from pymongo import MongoClient, UpdateOne
from sqlalchemy.exc import OperationalError
from time import sleep
from datetime import datetime
from itertools import islice, takewhile, count

logging.basicConfig(level = logging.DEBUG)

class FutureException(Exception):
    pass

def chunk(n, it):
    src = iter(it)
    return takewhile(bool, (list(islice(src, n)) for _ in count(0)))

def write_results(coll, results):
    chunked = chunk(500, results)
    checked_keys = ['Sender_Phone_Number',
                    'Patient_Phone_Number',
                    'Patient_Name',
                    'Report_Date',
                    'Service_Code']
    i = 0
    for c in chunked:
        requests = [ UpdateOne({ k: obj[k] for k in checked_keys},
                               { '$setOnInsert': obj },
                               upsert=True) for obj in c]
        i += len(requests)
        coll.bulk_write(requests, ordered=False)
    return i


mysql_deets = {
    'pass': getenv('MYSQL_PASS'),
    'user': getenv('MYSQL_USER'),
    'db': getenv('MYSQL_DB'),
    'table': getenv('MYSQL_TABLE'),
    'host': getenv('MYSQL_HOST')
}

url = 'mysql+pymysql://{user}:{pass}@{host}:3306/{db}'.format(**mysql_deets)

def get_from(coll):
    try:
        latest = coll.find().sort('Report_Date', -1).limit(1)[0]
        return latest['Report_Date'].isoformat()
    except BaseException as e:
        logging.error(e)
        return datetime(1970,1,1).isoformat()

def write(i=2):
    engine = create_engine(url)
    try:
        engine.connect()
    except OperationalError:
        sleep(math.exp(i)) # exponential backoff
        write(i+1)

    client = MongoClient(
        getenv('MONGO_HOST'),
        username = getenv('MONGO_USER') or None,
        password = getenv('MONGO_PASS') or None,
        ssl = bool(getenv('MONGO_SSL'))
    )

    collection = client['healthworkers'].rawmessages
    table = mysql_deets['table']

    # Get date of the latest message in our DB
    fr = get_from(collection)

    # Get messages from Orange DB
    logging.debug('RETRIEVER: Getting messages since {}'.format(fr))
    query = 'SELECT * FROM {table} WHERE Report_Date > "{fr}"'.format(table=table, fr=fr)
    results = engine.execute(query)
    results = (dict(zip(r.keys(), r.values())) for r in results)

    # Write it all to Mongo
    num = write_results(collection, results)
    logging.debug('RETRIEVER: finished writing {} messages'.format(num))

if __name__ == '__main__':
    write()

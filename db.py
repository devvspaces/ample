import sqlite3
from flask import g
import logging
import json
import requests

DATABASE = 'database.db'
url = "http://www.bonspiels.net/home/fb_page"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def upsert_db(query, args=()):
    try:
        cur = get_db().execute(query, args)
        get_db().commit()
        cur.close()
        return True
    except Exception as e:
        print(e)
        logging.warning(str(e))
        return False

def page_db():
    result = requests.get(url, headers=headers)
    js = result.content.decode().strip()
    y = json.loads(js)
    return y

     
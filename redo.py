from db import get_db, query_db, upsert_db, page_db

def reload_db(a=''):
	q = query_db("SELECT * FROM events")
	print(q)

reload_db()
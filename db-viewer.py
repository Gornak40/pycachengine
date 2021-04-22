#!venv/bin/python
from unqlite import UnQLite


db_path = 'pycachengine.db'
db = UnQLite(db_path)
#for key, value in db.items():
#	print(f'{key}: {eval(value.decode("utf-8"))}')
print(len(db))
db.close()
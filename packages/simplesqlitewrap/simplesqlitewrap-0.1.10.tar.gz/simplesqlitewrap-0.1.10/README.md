Simple class that wraps around the `sqlite3.conn().cursor().execute()` method

```py
from simplesqlitewrap import Database

class DbWrapper(Database):
    def create_tables(self):
    	self._execute('CREATE TABLE IF NOT EXISTS Users (user_id INTEGER PRIMARY KEY, first_name NVARCHAR);')

    def insert_users(self, users):
    	# returns the number of inserted rows
    	return self._execute('INSERT OR IGNORE INTO Users (user_id, first_name) VALUES (?, ?)', users, rowcount=True, many=True)

    def select_users(self, **kwargs):
    	# returns the list of all the recors in 'Users' as classes
    	return self._execute('SELECT * FROM Users', **kwargs)

db = DbWrapper('database.sqlite')
print(db)

db.create_tables()

params = [(1, 'Bob'), (2, 'Charlie')]
rows_inserted = db.insert_users(params)
print('Rows inserted:', rows_inserted)

users = db.select_users(as_namedtuple=True)
for user in users:
	print('ID:', user.id, 'first name:', user.first_name)
```

### Disclaimer

If you stumbled upon this package, please remember that this is just a small utility I made for myself - breaking changes may be introduced without notice
from store.postgres.dictionary import DictionaryStore
from store.postgres.postgres import PostgresStore

try:
    from storebeatconfig import db_name, db_user, db_password, db_host
except Exception as e:
    db_name = 'store_beat'
    db_user = 'dameng'
    db_password = 'hello'
    db_host = '127.0.0.1'

def pg_store(table):
    return DictionaryStore({'table': table, 'name': db_name,
                          'user': db_user,
                          'password': db_password,
                          'host': db_host
                          })

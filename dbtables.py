import psycopg2
from database import SQL

db = SQL()

db.drop_tables()
db.create_tables()

db.close()

from decouple import config

import psycopg2
from psycopg2.errors import SerializationFailure
import psycopg2.extras

USER     = 'peter'
PASSWORD = config('DB_PASS')
URL = f'postgresql://{USER}:{PASSWORD}@quantdome-12092.5xj.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full'

def connect_database():
    try:
        conn =  psycopg2.connect(URL,
                            cursor_factory=psycopg2.extras.RealDictCursor)
        print('database connection successful')
        return conn
    except Exception as e:
        print('database connection failed')
        print(e)
        return


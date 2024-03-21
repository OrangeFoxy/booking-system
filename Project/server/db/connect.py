import psycopg2
from . import params as p
from . import sql_db as s

DROP_TABLES = False

def connect():
    # Строка подключения
    conn_string = "host={host} dbname={database} user={user} password={password} port={port}".format(**p.DB_PARAMS)

    # Попытка подключения к базе данных
    try:
        # Устанавливаем соединение
        conn = psycopg2.connect(conn_string)
        with conn.cursor() as cur:
            if DROP_TABLES:
                cur.execute(s.drop)
                conn.commit()
            cur.execute(s.SCHEMA_DB)
            conn.commit()
        return conn

    except psycopg2.Error as e:
        print("Ошибка при подключении к базе данных:", e)
        exit(0)

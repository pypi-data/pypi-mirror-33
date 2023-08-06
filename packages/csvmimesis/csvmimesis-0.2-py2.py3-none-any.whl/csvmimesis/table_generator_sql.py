import sqlite3

from csvmimesis.table_generator import create_table, write_table
from sqlalchemy import create_engine


import pandas as pd


def create_tables(tab_profile, sql_queries):
    table = create_table(tab_profile)

    df = pd.DataFrame(table)

    con = create_engine('sqlite://', echo=True)
    #con = sqlite3.connect(":memory:")
    df.to_sql('df', con=con)

    tables={}
    for id,sql in sql_queries.items():
        #res = engine.execute(sql).fetchall()
        df = pd.read_sql_query(sql, con=con)
        tables[id]=df

    return tables
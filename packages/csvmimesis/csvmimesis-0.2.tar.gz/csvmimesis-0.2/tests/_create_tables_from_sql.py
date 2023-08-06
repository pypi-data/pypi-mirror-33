from csvmimesis.table_generator import write_table
from csvmimesis.table_generator_sql import create_tables



tab_profile={
  "local":"en",
  "rows": 10,
  "columns": [
    ["address.city", 1],
    "address.country"
  ]
}

sql_queries={
    't1':"SELECT * FROM df;"
}

tables = create_tables(tab_profile, sql_queries)

dir="sql_tabs"
for id, df in tables.items():
    write_table(df, dir=dir, file=None, prefix=id, encoding='utf-8', gzipped=False)
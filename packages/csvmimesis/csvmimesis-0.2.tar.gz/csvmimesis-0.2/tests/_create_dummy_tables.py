

import inspect

from csvmimesis.mimesis_data_providers import list_providers, list_methods, list_locals
from csvmimesis.table_generator import create_table, write_table, create_random_table
from mimesis import Generic
import os



def create_per_provider(min_columns=5, dir="/Users/jumbrich/data/mimesis_csvs/dummy"):
    for p,ms in list_methods().items():
        if len(ms)<min_columns:
            continue

        for l in list_locals():

            for size in [20, 100]:
                try:
                    tab_profile = {
                        "prefix": None,
                        "local": l,
                        "rows": size,
                        "columns": ["{}.{}".format(p,m) for m in ms]
                    }
                    _tab= create_table(tab_profile)
                    file=os.path.join(dir, "{}_{}_r{}xc{}.csv".format(l, p, size, len(ms)))
                    write_table(_tab, file=file)
                except Exception as e:
                    print ("Exception {} for {}_{}_r{}xc{}.csv".format(e,l, p, size, len(ms)))



def create_dummy(dir="/Users/jumbrich/data/mimesis_csvs/encoding"):

    rows=300
    columns=10
    encoding='utf-8'
    local='el'
    _tab = create_random_table(rows, columns, seed=None, local=local, encoding=encoding)
    file = os.path.join(dir, "{}_{}_r{}xc{}.csv".format(encoding, local, rows, columns))
    write_table(_tab, file=file, encoding=encoding, gzipped=False)


create_dummy()

data=b"UTF-8 data@"
data=data.decode("latin-1","ignore")
print(data)
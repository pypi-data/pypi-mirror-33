
# -*- coding: utf-8 -*-
from csvmimesis.table_generator import create_table, write_table, create_table_pair



table = {
        "seed":"1232",
        "prefix": None,
        "local": 'de',
        "rows": 1000,
        "columns": ['address.address', 'address.city']
    }

table1 = {
        "seed":"1231",
        "prefix": None,
        "local": 'de',
        "rows": 20,
        "columns": ['address.address', ['address.city',0.5], ["address.longitude",.5],["address.latitude",.5],["address.postal_code",.5]]
    }

def create_dummy_table(csv, table=table1):


    _tab = create_table(table)
    write_table(_tab, file=csv)


table_pair={
        "local":"de",
        "seed": "1232",
        "shared_providers":None,
        "add_providers":[ [ ["address.postal_code",1],["address.street_name",1], ["address.street_number",1]],
                          [ ["address.latitude",1], ["address.longitude",1],["address.country",1]]
                        ],
        "join_providers":[["address.city",1]],
        "rows":[20,20]
    }

table_pair1={
        "local":"en",
        "seed": "1232",
        "shared_providers":None,
        "add_providers":[ [ ["person.last_name",1],["person.name",1] ],
                          [ ["person.username",1], ["person.email",1],["address.country",1] ]
                        ],
        "join_providers":[["person.identifier",1]],
        "rows":[20,20],

    }

table_pair2={
        "local":"en",
        'seed':"2323",
        "shared_providers":[ ["address.city",1],["address.country",1],["address.postal_code",1]],
        "add_providers":None,
        "join_providers":None,
        "rows":[20,20]}


def create_dummy_table_pair(csv1, csv2, table_pair=table_pair):


    _tables = create_table_pair(**table_pair)
    write_table(_tables[0], file=csv1)
    write_table(_tables[1], file=csv2)




#!/usr/bin/env python

import csv
from models import ItemType, Element

# get the oral history type
oh = ItemType.get(id=4)

# get the column names
col_names = set(['Identifier', 'Files', 'Tags'])
for item in oh.items:
    col_names.update(item.elements.keys()) 
col_names = list(col_names)
col_names.sort()

# now write out the csv

output = csv.DictWriter(open('oralhistories.csv', 'w'), col_names) 
output.writeheader()

for item in oh.items:
    row = {
        "Identifier": item.id,
        "Tags": '|'.join(item.tags),
        "Files": '|'.join([f.original_filename for f in item.files])
    }
    for key, value in item.elements.items():
        row[key] = '|'.join(value)
    output.writerow(row)


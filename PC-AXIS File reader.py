import pandas as pd

import csv
from io import StringIO
import itertools


# Custom rules for csv reader
class PxFieldDialect(csv.Dialect):
    strict = True
    skipinitialspace = True
    quoting = csv.QUOTE_ALL
    delimiter = ','
    quotechar = '"'
    lineterminator = '\n'

class PxDataDialect(csv.Dialect):
    strict = True
    skipinitialspace = True
    quoting = csv.QUOTE_ALL
    delimiter = ' '
    quotechar = '"'
    lineterminator = '\n'

    
# Parse csv-like string
def parse_px_field(field, _type=None):
    # _type: "field", "data"
    dialects = {
        "field": PxFieldDialect,
        "data": PxDataDialect,
    }
    
    r = csv.reader(StringIO(field), dialects.get(_type, dialects["field"])())
    
    out = []
    for line in r:
        for item in line:
            # Skip empty strings caused by linebreaks
            if item:
                out.append(item)
        
    return out


# Reads a .px file into a pandas DataFrame
def read_px(filename):
    with open(filename) as f:
        data = f.read()


    # ## Separate fields


    lines = data.split(";")
    fields = [l.strip().split("=", 1) for l in lines if l.strip()]
    field_dict = dict(fields)


    # ## Parse Headings


    head = field_dict["HEADING"].strip("\"")
    headers = parse_px_field(field_dict["VALUES(\"{}\")".format(head)], _type="field")


    # ## Find & Parse MultiIndex levels
    # * Find headers


    levels = parse_px_field(field_dict["STUB"], _type="field")


    # * Parse values


    level_values = [parse_px_field(field_dict["VALUES(\"{}\")".format(lev)], _type="field") for lev in levels]
    levels_dict = dict(zip(levels, level_values))


    # ## Parse Data
    # * Split into stream of cells

    data = parse_px_field(field_dict["DATA"], _type="data")


    # * Convert into table

    lines = [data[i:i+len(headers)] for i in range(0, len(data), len(headers))]



    # * Create MutliIndex from levels

    ind = pd.MultiIndex.from_product(list(levels_dict.values()), names=levels_dict.keys())


    # * Construct DataFrame

    df = pd.DataFrame(lines, columns=headers, index=ind)


    # * Flatten MultiIndex
    # * Convert all cell dtypes

    df2 = df.reset_index().convert_objects()

    return df2

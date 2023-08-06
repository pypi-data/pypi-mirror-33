##
# Mail Merge Mode for j2static
##

import os
import pathlib

import csv
import json
import pickle

from j2static.build import get_builder

def load_csv(fp):
    """Read a CSV file and put in into a list"""
    reader = csv.DictReader(fp)
    return [x for x in reader]

_decoders = {
    '.json': json.load,
    '.pkl': pickle.load,
    '.csv': load_csv
}

def load_data(filename):
    """Load a file as something we can pass to jinja"""
    filename = pathlib.Path(filename)
    decoder = _decoders[filename.suffix]
    with open(filename) as f:
        return decoder(f)

def merge_csv(csv_file, callback=None, key=lambda x: x['id']):
    """Process a single file containing multiple records"""

    data = dict()

    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:

            # give the user a chance to do some processing
            if callback:
                row = callback(row)

            data[key(row)] = {'row': row }

    return data


def merge_dir(pattern, root_path='.', callback=None, key=lambda x: x['id']):
    """Process multiple files in a directory, with one file containing one record"""

    data_dict = dict()
    
    path = pathlib.Path(root_path)
    for item in path.glob(pattern):
        suffix = item.suffix
        
        if suffix not in _decoders:
            print("sorry, don't know how to decode {} ...", suffix)
            continue
        row = _decoders[suffix](item)

        if 'id' not in row:
            row['id'] = item

        # give the user a chance to do some processing
        if callback:
            row = callback(row)

        data_dict[key(row)] = row

    return data_dict


def write_dict(data_dict, template="base.html", context=dict(), out_type=None, out_dir='./out/'):
    
    # try to get the builder...
    if out_type == None:
        name, out_type = os.path.splitext(template)
        out_type = out_type[1:]
    builder = get_builder(out_type, '.')

    # iterate though the data
    for (fname, data) in data_dict.items():
        data.update(context)

        path = pathlib.Path(out_dir) / "{}.{}".format(fname, out_type)
        builder.generate(template, path, data)

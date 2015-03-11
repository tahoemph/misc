"""
The point of this script is to take an input CSV and create an output CSV of
roughly the same shape but containing random data.  This can be useful
for generating tests.
"""
import argparse
from csv import DictReader, DictWriter
from itertools import chain, count, takewhile, izip
import random
import uuid

parser = argparse.ArgumentParser()
parser.add_argument('filenames', nargs="+")
parser.add_argument('-F', dest='forced', default=None)
parser.add_argument('-I', dest='left', default=None)
args = parser.parse_args()

forced_columns = {}
if args.forced:
    forced_columns = dict(forced.split(',') for forced in args.forced.split(';'))
left_columns = set(args.left.split(',')) if args.left else set()


mapped_types = forced_columns
mapped_values = { x: {} for x in forced_columns }
for input_file in args.filenames:
    # Sniff the first bit of the input figuring out the columns and possible
    # types.
    with open(input_file) as f:
        reader = DictReader(f)
        # Humph.  Couldn't figure out how to do this with list comprehension
        # without dropping a row.
        rows = []
        count = 0
        for row in reader:
            rows.append(row)
            count += 1
            if count > 10:
                break
        for field in reader.fieldnames:
            if field in mapped_types:
                continue
            if field in left_columns:
                continue
            not_int = False
            not_float = False
            for row in rows:
                try:
                    int(row[field])
                except ValueError:
                    not_int = True
                try:
                    float(row[field])
                except ValueError:
                    not_float = True
                if not_int and not_float:
                    break
            mapped_values[field] = {}
            if not not_float:
                mapped_types[field] = 'float'
            elif not not_int:
                mapped_types[field] = 'int'
            else:
                mapped_types[field] = 'uuid'

        output_file = input_file + ".fake"
        with open(output_file, "w") as n:
            rdr = chain(rows, reader)
            wrtr = DictWriter(n, fieldnames=reader.fieldnames)
            wrtr.writeheader()
            for row in rdr:
                for colname, value in row.items():
                    if colname in mapped_types:
                        if value not in mapped_values[colname]:
                            mapped_values[colname][value] = {
                                'uuid': uuid.uuid4(),
                                'float': random.uniform(-1, 1),
                                'int': random.randint(-100, 100),
                                'str': uuid.uuid4(),
                            }[mapped_types[colname]]
                        row[colname] = mapped_values[colname][value]

                wrtr.writerow(row)

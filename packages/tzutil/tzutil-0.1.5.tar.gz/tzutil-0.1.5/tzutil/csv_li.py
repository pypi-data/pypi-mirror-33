import io
import csv

def csv_li(txt, verify=None):
    f = io.StringIO(txt)
    reader = csv.reader(f, delimiter=',')
    li = []
    for pos, row in enumerate(reader):
        if not row:
            continue

        row = verify(row)
        if row:
            li.append(row)
    return li

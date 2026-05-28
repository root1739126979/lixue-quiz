import csv
from io import StringIO


def rows_to_csv(headers: list[str], rows: list[list[object]]) -> str:
    output = StringIO()
    output.write("\ufeff")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return output.getvalue()

#!python

import csv
import sys

import jsonlines


def main():
    reader = csv.DictReader(sys.stdin)
    writer = jsonlines.Writer(sys.stdout.buffer)
    try:
        writer.write_all(reader)
    except BrokenPipeError:
        pass

    return 0


if __name__ == '__main__':
    sys.exit(main())

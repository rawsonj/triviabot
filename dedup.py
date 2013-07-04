#!/usr/bin/env python

# Short deduplication script. Runs over every file in the target directory and
# spits out duplicate lines and files which contained them.

from collections import defaultdict
import os
import sys


def collate(d, path):
    with open(path, "rU") as handle:
        for line in handle:
            d[line].append(path)


def readdir(directory):
    d = defaultdict(list)
    for root, dirs, files in os.walk(directory):
        for name in files:
            path = os.path.join(root, name)
            collate(d, path)
    return d


if len(sys.argv) < 2:
    print "No directory specified!"
    sys.exit()

directory = sys.argv[1]

print "Reading", directory, "..."

d = readdir(directory)

print "Done. Duplicates:"

for line, paths in d.iteritems():
    if len(paths) > 1:
        print ">", line
        print ">", ", ".join(paths)

#!/usr/bin/env python

# Short deduplication script. Runs over every file in the target directory and
# spits out duplicate lines and files which contained them.

from collections import defaultdict
import logging
import os
import optparse
import subprocess
import sys


logging.basicConfig(format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s')
logger = logging.getLogger('dedup')
logger.setLevel(logging.INFO)


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


op = optparse.OptionParser()
op.add_option('-p', '--path', dest='path', type=str,
              default='questions', help='Directory with files to scan')
op.add_option('-l', '--log-level', dest='log_level', type=str,
              default='warning', help='Logging output level')
op.add_option('-d', '--destructive', dest='delete', action="store_true",
              default=False, help='Setting this will delete all but one copy')
options, args = op.parse_args()

if options.log_level.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR',
                                 'CRITICAL']:
    logger.setLevel(getattr(logging, options.log_level.upper()))


logger.info('Reading {0} ...'.format(options.path))
d = readdir(options.path)

logger.info("Done. Duplicates:")

for line, paths in d.iteritems():
    if len(paths) > 1:
        logger.info(line)
        logger.info(", ".join(paths))
        purge = paths[:-1]  # keep the copy in the last file
        cmd = [ 'sed', '-i', "{/" + line.strip() + "/d}", ] + purge
        logger.warning(' '.join(cmd)) 
        if options.delete:
            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,)
            (out, err) = proc.communicate()
            if out:
                logger.info(out)
            if err:
                logger.error(err)

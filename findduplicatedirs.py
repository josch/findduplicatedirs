#!/usr/bin/env python3
#
# Copyright (c) 2014 Johannes Schauer <j.schauer@email.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

import os
import sys
import hashlib
from collections import defaultdict

if len(sys.argv) != 2:
    print("usage: %s directory"%sys.argv[0])
    exit(1)

dirhashes=dict()
duplicates=defaultdict(list)
diskusage=dict()
subtreesize=dict()

root=os.path.abspath(sys.argv[1])

directorywalk = list(os.walk(root, topdown=False))

total = len(directorywalk)

for (i, (dirpath, dirnames, filenames)) in enumerate(directorywalk):
    print("%.02f\r"%((100.0*(i+1))/total), file=sys.stderr, end='')
    h = hashlib.sha256()
    # initialize disk usage to the size of this directory
    du = os.path.getsize(dirpath)
    # initialize the subtreesize to the number of files in this directory plus
    # one for this directory itself
    sts = len(filenames)+1
    # process all files
    for filename in sorted(filenames):
        h.update(filename.encode('utf8', 'surrogateescape'))
        filename = os.path.join(dirpath, filename)
        # we ignore the content of everything that is not a regular file or symlink
        # the content of a symlink is its destination
        if os.path.islink(filename):
            h.update(os.readlink(filename).encode('utf8', 'surrogateescape'))
        elif os.path.isfile(filename):
            du += os.path.getsize(filename)
            with open(filename, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    h.update(chunk)
    # process all directories
    for dirname in sorted(dirnames):
        h.update(dirname.encode('utf8', 'surrogateescape'))
        dirname = os.path.join(dirpath, dirname)
        if os.path.islink(dirname):
            h.update(os.readlink(dirname).encode('utf8', 'surrogateescape'))
        else:
            sha = dirhashes[dirname]
            du += diskusage[sha]
            sts += subtreesize[sha]
            h.update(sha)
    # update information
    sha = h.digest()
    dirhashes[dirpath] = sha
    subtreesize[sha] = sts
    diskusage[sha] = du
    duplicates[sha].append(dirpath)

# filter the list of hashes such that only hashes where the directories
# belonging to the hash have direct parent directories with a different hash
# remain
nondups = list()
for k,v in duplicates.items():
    # if a hash only has one directory, there is no duplicate
    if len(v) == 1:
        continue
    # if all directories have the same parent, then it's a duplicate
    if len(set([os.path.dirname(p) for p in v])) == 1:
        nondups.append(k)
        continue
    # if all parents have the same hash, do not append because parent will be
    # added
    if len(set([dirhashes[os.path.dirname(p)] for p in v])) != 1:
        nondups.append(k)
        continue

for sha in nondups:
    du = diskusage[sha]
    sts = subtreesize[sha]
    dirs = [os.path.relpath(p) for p in duplicates[sha]]
    print("%d\t%d\t%s"%(du, sts, "\t".join(dirs)))

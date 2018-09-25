#!/usr/bin/env python2
# -"- coding: utf-8 -"-

from __future__ import print_function
from __future__ import unicode_literals

from argparse import ArgumentParser
import codecs
import pandas as pd


def main(in_files, out_mrs, out_refs):
    data = []
    for in_file in in_files:
        data.append(pd.read_csv(in_file, encoding='UTF-8'))
    data = pd.concat(data)

    with codecs.open(out_mrs, 'w', 'UTF-8') as fh:
        fh.write("\n".join(list(data['mr'])))

    with codecs.open(out_refs, 'w', 'UTF-8') as fh:
        fh.write("\n".join([ref.replace('\r\n', ' ') for ref in list(data['ref'])]))


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('in_files', nargs='+', help='Input E2E data (all files)')
    ap.add_argument('out_mrs', help='Output DAs')
    ap.add_argument('out_refs', help='Output texts')

    args = ap.parse_args()
    main(args.in_files, args.out_mrs, args.out_refs)

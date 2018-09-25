#!/usr/bin/env python2
# -"- coding: utf-8 -"-

from __future__ import print_function
from __future__ import unicode_literals

from argparse import ArgumentParser
from tgen.data import DA
import codecs
import re


def main(in_file, out_mrs, out_refs):

    abst_das = []
    conc_das = []
    conc_da_texts = []
    abst_texts = []
    with codecs.open(in_file, 'r', 'UTF-8') as fh:
        for line in fh:
            line = line.strip()

            if line.startswith('FULL_DA'):
                line = re.sub('^FULL_DA = ', '', line)
                conc_das.append(DA.parse_cambridge_da(line))
                conc_da_texts.append(line)
            elif line.startswith('ABSTRACT_DA'):
                line = re.sub('^ABSTRACT_DA = ', '', line)
                abst_das.append(DA.parse_cambridge_da(line))
            elif line.startswith('->'):
                line = re.sub('^-> "', '', line)
                line = re.sub('";\s*$', '', line)
                line = re.sub(r'\[([a-z]+)\+X\]X', r'X-\1', line)
                line = re.sub(r'\[[^\]]*\]', '', line)
                abst_texts.append(line)

    conc_texts = []
    for abst_da, conc_da, abst_text in zip(abst_das, conc_das, abst_texts):
        text = abst_text
        for abst_dai, conc_dai in zip(abst_da.dais, conc_da.dais):
            assert abst_dai.slot == conc_dai.slot
            if abst_dai.value.startswith('X'):
                text = text.replace('X-' + abst_dai.slot, conc_dai.value, 1)
        text = re.sub(r'the The', 'The', text)
        conc_texts.append(text)

    with codecs.open(out_mrs, 'w', 'UTF-8') as fh:
        fh.write("\n".join(conc_da_texts))

    with codecs.open(out_refs, 'w', 'UTF-8') as fh:
        fh.write("\n".join(conc_texts))


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('in_file', help='Input BAGEL data')
    ap.add_argument('out_mrs', help='Output DAs')
    ap.add_argument('out_refs', help='Output texts')

    args = ap.parse_args()
    main(args.in_file, args.out_mrs, args.out_refs)

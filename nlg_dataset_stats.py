#!/usr/bin/env python2

from __future__ import print_function

import pandas as pd
import re
import numpy as np
import math
import codecs
from tgen.data import DA


def read_e2e_data():
    with codecs.open('data/e2e-refs.txt', 'r', 'UTF-8') as fh:
        refs = [inst.strip() for inst in fh.readlines()]
    with codecs.open('data/e2e-mrs.txt', 'r', 'UTF-8') as fh:
        mrs = [DA.parse_diligent_da(mr) for mr in fh.readlines()]
    return mrs, refs

def read_sfx_data():
    with codecs.open('data/sfrest-refs.txt', 'r', 'UTF-8') as fh:
        refs = [inst.strip() for inst in fh.readlines()]
    with codecs.open('data/sfrest-mrs.txt', 'r', 'UTF-8') as fh:
        mrs = [DA.parse(mr) for mr in fh.readlines()]
    return mrs, refs

def read_bagel_data():
    with codecs.open('data/bagel-refs.txt', 'r', 'UTF-8') as fh:
        refs = [inst.strip() for inst in fh.readlines()]
    with codecs.open('data/bagel-mrs.txt', 'r', 'UTF-8') as fh:
        mrs = [DA.parse_cambridge_da(mr) for mr in fh.readlines()]
    return mrs, refs


def data_stats(mrs, refs, delex_slots):
    assert len(refs) == len(mrs)
    print('Insts:', len(refs))
    print('MRs:', len(set(mrs)))

    delex_mrs = [da.get_delexicalized(set(delex_slots)) for da in mrs]
    print('Delex MRs:', len(set(delex_mrs)))

    mr_to_refs = {}
    for mr, ref in zip(mrs, refs):
        refs_for_mr = mr_to_refs.get(mr, [])
        if ref not in refs_for_mr:
            refs_for_mr.append(ref)
        mr_to_refs[mr] = refs_for_mr
    print('Refs/MR min: %d' % min([len(refs_) for refs_ in mr_to_refs.values()]),
          ' max: %d' % max([len(refs_) for refs_ in mr_to_refs.values()]),
          ' mean: %.2f' % np.mean([len(refs_) for refs_ in mr_to_refs.values()]))

    # TODO ref len should discount empty slots (eg. "goodbye()")
    print('MR mean len: %.2f' % np.mean([len(mr) for mr in set(mrs)]))
    print('Ref mean len: %.2f' % np.mean([len(re.split(' +', ref)) for ref in refs]))
    print('Ref mean sentence len: %.2f' %
          np.mean([len(re.split(' +', sent.strip()))
                   for ref in refs
                   for sent in re.split('[.?!]+(?![0-9])', ref) if sent.strip()]))
    sent_nums = [len([sent for sent in re.split('[.?!]+(?![0-9])', ref) if sent.strip()]) for ref in refs]
    print('Ref sentences min: %d  max: %d  mean: %.2f' %
          (np.mean(sent_nums), np.max(sent_nums), np.mean(sent_nums)))


if __name__ == '__main__':
    print('\nE2E stats:\n=========')
    mrs, refs = read_e2e_data()
    data_stats(mrs, refs, ['name', 'near'])

    print('\nSFREST stats:\n=========')
    mrs, refs = read_sfx_data()
    data_stats(mrs, refs, ['name', 'near'])

    print('\nBAGEL stats:\n=========')
    mrs, refs = read_bagel_data()
    data_stats(mrs, refs, ['name', 'near'])

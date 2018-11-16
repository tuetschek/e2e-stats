#!/usr/bin/env python2

from __future__ import print_function
from __future__ import unicode_literals
from argparse import ArgumentParser

import pandas as pd
import re
from tgen.data import DA

from tag_datasets import MorphoTagger, write_output
from nlg_dataset_stats import data_stats


def process_file(tagger_model, input_file):
    df = pd.read_csv(input_file, sep="\t", encoding="UTF-8")
    raw_mrs = list(df['MR'])
    raw_refs = list(df['output'])
    mrs = [DA.parse_diligent_da(mr) for mr in raw_mrs]
    tagger = MorphoTagger(tagger_model)
    tagged_refs = [tagger.tag(line) for line in raw_refs]

    for ff in ['ngram', 'lca', 'collins']:
        write_output(tagged_refs, ff, re.sub(r'\.tsv', '.tag.%s.txt' % ff, input_file))

    stats = data_stats(mrs, tagged_refs, {'name': [], 'near': []}, re.sub(r'\.tsv', '', input_file))
    return stats


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('-t', '--tagger', '--tagger-model', type=str, help='Path to tagger',
                    default='morphodita/english-morphium-wsj-140407/english-morphium-wsj-140407.tagger')
    ap.add_argument('-o', '--output', type=str, help='Output CSV file')
    ap.add_argument('input_files', type=str, nargs='+')
    args = ap.parse_args()

    all_stats = {}
    for input_file in args.input_files:
        stats = process_file(args.tagger, input_file)
        all_stats[input_file] = [stats[key] for key in sorted(stats.keys())]
        keys = sorted(list(stats.keys()))
    if args.output:
        df = pd.DataFrame.from_dict(all_stats)
        df = df.rename(index={num: key for num, key in enumerate(keys)})
        df.to_csv(args.output, encoding='UTF-8')

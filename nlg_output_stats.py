#!/usr/bin/env python2
# -"- coding: utf-8 -"-

from __future__ import print_function
from __future__ import unicode_literals
from argparse import ArgumentParser

import pandas as pd
import regex as re
from tgen.data import DA

from tag_datasets import MorphoTagger, write_output
from nlg_dataset_stats import data_stats


class Detokenizer(object):
    """Adapted detokenizer from TGen (for E2E data)."""

    def __init__(self):
        """\
        Constructor (pre-compile all needed regexes).
        """
        # compile regexes
        self._currency_or_init_punct = re.compile(r' ([\p{Sc}\(\[\{\¿\¡]+) ', flags=re.U)
        self._noprespace_punct = re.compile(r' ([\,\.\?\!\:\;\\\%\}\]\)]+) ', flags=re.U)
        self._contract = re.compile(r" (\p{Alpha}+) ' (ll|ve|re|[dsmt])(?= )", flags=re.U | re.I)
        self._dash_fixes = re.compile(r" (\p{Alpha}+|£ *[0-9]+) - (priced|star|friendly|(?:£ )?[0-9]+) ", flags=re.U | re.I)
        self._dash_fixes2 = re.compile(r" (non) - ([\p{Alpha}-]+) ", flags=re.U | re.I)
        self._dash_fixes3 = re.compile(r" (mid|medium|low|high|light) - (price|cost|range) ", flags=re.U | re.I)
        self._dash_fixes4 = re.compile(r" (take) - (away) ", flags=re.U | re.I)

    def detokenize(self, text):
        """\
        Detokenize the given text.
        """
        text = ' ' + text + ' '
        text = self._dash_fixes.sub(r' \1-\2 ', text)
        text = self._dash_fixes2.sub(r' \1-\2 ', text)
        text = self._dash_fixes3.sub(r' \1-\2 ', text)
        text = self._dash_fixes4.sub(r' \1-\2 ', text)
        text = self._currency_or_init_punct.sub(r' \1', text)
        text = self._noprespace_punct.sub(r'\1 ', text)
        text = self._contract.sub(r" \1'\2", text)
        text = text.strip()
        if not text:
            return ''
        # capitalize (we assume no abbreviations since there are none in the data)
        # this ensures proper sentence splitting
        text = text[0].upper() + text[1:]
        text = re.sub('(\p{Alpha})\. (\p{Ll})', lambda m: m.group(1) + '. ' + m.group(2).upper(), text)
        return text


def process_file(tagger_model, input_file):
    detok = Detokenizer()
    df = pd.read_csv(input_file, sep="\t", encoding="UTF-8")
    raw_mrs = list(df['MR'])
    raw_refs = [detok.detokenize(text) for text in list(df['output'])]
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

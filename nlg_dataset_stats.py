#!/usr/bin/env python2

from __future__ import print_function
from __future__ import unicode_literals

import pandas as pd
import re
import sys
import numpy as np
import math
import codecs
from tgen.data import DA
from tgen.delex import delex_sent
from tag_datasets import write_output


def split_tags(text):
    """Return list of word, tag tuples"""
    return [[tok.split('/') if tok != '////:' else ('/', '/', ':') for tok in sent.split(' ')]
            for sent in text.split("\t")]


def read_e2e_data():
    with codecs.open('data/e2e-refs.tag.ngram.txt', 'r', 'UTF-8') as fh:
        refs = [split_tags(inst.strip()) for inst in fh.readlines()]
    with codecs.open('data/e2e-mrs.txt', 'r', 'UTF-8') as fh:
        mrs = [DA.parse_diligent_da(mr) for mr in fh.readlines()]
    return mrs, refs


def read_sfx_data():
    with codecs.open('data/sfrest-refs.tag.ngram.txt', 'r', 'UTF-8') as fh:
        refs = [split_tags(inst.strip()) for inst in fh.readlines()]
    with codecs.open('data/sfrest-mrs.txt', 'r', 'UTF-8') as fh:
        mrs = [DA.parse(mr.strip()) for mr in fh.readlines()]
    return mrs, refs


def filter_inform(mrs, refs):
    filt_mrs, filt_refs = [], []
    for mr, ref in zip(mrs, refs):
        if any([dai.da_type.startswith('inform') for dai in mr]):
            filt_mrs.append(mr)
            filt_refs.append(ref)
    write_output(filt_refs, 'ngram', 'data/sfrest_inform-refs.tag.ngram.txt')
    write_output(filt_refs, 'lca', 'data/sfrest_inform-refs.tag.lca.txt')
    write_output(filt_refs, 'collins', 'data/sfrest_inform-refs.tag.collins.txt')

    return filt_mrs, filt_refs


def read_bagel_data():
    with codecs.open('data/bagel-refs.tag.ngram.txt', 'r', 'UTF-8') as fh:
        refs = [split_tags(inst.strip()) for inst in fh.readlines()]
    with codecs.open('data/bagel-mrs.txt', 'r', 'UTF-8') as fh:
        mrs = [DA.parse_cambridge_da(mr) for mr in fh.readlines()]
    return mrs, refs


def ngram_stats(refs, n):
    ngrams = {}
    for ref in refs:
        tok_ngrams = [[tok[0] for sent in ref for tok in sent][i:] for i in xrange(n)]
        for ngram in zip(*tok_ngrams):
            ngrams[ngram] = ngrams.get(ngram, 0) + 1
    uniq_ngrams = len([val for val in ngrams.values() if val == 1])
    return ngrams, uniq_ngrams


def delexicalize_refs(mrs, refs, delex_slots, delex_output_file):
    delex_refs = []
    print('Delexicalizing...', end=' ', file=sys.stderr)
    for pos, (mr, ref) in enumerate(zip(mrs, refs)):
        delex_ref = []
        print(pos, end=' ', file=sys.stderr)
        sys.stderr.flush()
        for sent in ref:
            delex, _, absts = delex_sent(mr, [tok[0] for tok in sent], delex_slots, repeated=True)
            off = 0
            shift = 0
            delex_tagged = []
            for abst in absts:
                if abst.start == -1:  # skip delex instances not actually occurring in this sentence
                    continue
                delex_tagged.extend(sent[off + shift:abst.start + shift])
                # POS tag for all delex'd slots is usually NNP, except for phone numbers and counts
                delex_pos = {'count': 'CD', 'phone': 'CD'}.get(abst.slot, 'NNP')
                delex_tagged.append([delex[abst.start], delex[abst.start], delex_pos])
                off = abst.end
                shift += abst.surface_form.count(' ')
            delex_tagged.extend(sent[off + shift:])
            delex_ref.append(delex_tagged)
        delex_refs.append(delex_ref)

    with codecs.open(delex_output_file + '.delex.txt', 'w', 'UTF-8') as fh:
        fh.write('\n'.join([' '.join([tok[0] for sent in ref for tok in sent]) for ref in delex_refs]))

    write_output(delex_refs, 'lca', delex_output_file + '.delex.tag.lca.txt')
    write_output(delex_refs, 'collins', delex_output_file + '.delex.tag.collins.txt')

    return delex_refs


def entropy(ngrams):
    """Shannon entropy"""
    total_freq = sum(ngrams.values())
    return - sum([float(freq)/total_freq * math.log(float(freq)/total_freq, 2) for freq in ngrams.values()])


def cond_entropy(joint, ctx):
    """Conditional/next-word entropy (language model style)"""
    total_joint = sum(joint.values())
    total_ctx = sum(ctx.values())
    # H(y|x) = - sum_{x,y} p(x,y) log_2 p(y|x)
    # p(y|x) = p(x,y) / p(x)
    return - sum([float(freq)/total_joint *
                  math.log((float(freq)/total_joint) / (float(ctx[ngram[:-1]])/total_ctx), 2)
                  for ngram, freq in joint.items()])


def data_stats(mrs, refs, delex_slots, delex_output_file):

    stats = {}
    def sprnt(*args):
        """Print out and store the statistic."""
        print(*args)
        text = ' '.join([unicode(arg) for arg in args])
        if "\n" in text:
            common_header, rest = text.split("\n", 1)
            common_header = common_header.strip(':')
            data = [["%s-%02d" % (common_header, num), it.strip()]  for num, it in enumerate(rest.split("\n"), start=1)]
        elif '  ' in text:
            data = [it.split(':', 1) for it in text.split('  ')]
            common_header = re.sub(' [^ ]*$', '', data[0][0])
            data = [data[0]] + [[common_header + ' ' + it[0], it[1]] for it in data[1:]]
        else:
            data = [text.split(':', 1)]
        for it_key, it_val in data:
            stats[it_key] = it_val.strip()

    assert len(refs) == len(mrs)
    sprnt('Insts:', len(refs))
    sprnt('Lex MRs:', len(set(mrs)))

    delex_mrs = [da.get_delexicalized(delex_slots) for da in mrs]
    sprnt('Delex MRs:', len(set(delex_mrs)))

    mr_to_refs = {}
    for mr, ref in zip(mrs, refs):
        refs_for_mr = mr_to_refs.get(mr, [])
        if ref not in refs_for_mr:
            refs_for_mr.append(ref)
        mr_to_refs[mr] = refs_for_mr
    sprnt('Refs/MR min: %d' % min([len(refs_) for refs_ in mr_to_refs.values()]),
          ' max: %d' % max([len(refs_) for refs_ in mr_to_refs.values()]),
          ' mean: %.2f' % np.mean([len(refs_) for refs_ in mr_to_refs.values()]))

    # TODO MR len should discount empty slots (eg. "goodbye()")
    sprnt('MR mean len: %.2f' % np.mean([len(mr) for mr in set(mrs)]))

    lex_refs = refs
    delex_refs = delexicalize_refs(mrs, refs, delex_slots, delex_output_file)

    for refs_type, refs in [('Lex ', lex_refs), ('Delex ', delex_refs)]:
        sprnt(refs_type + 'Total tokens: %d' % sum([len([tok for sent in ref for tok in sent]) for ref in refs]))
        sprnt(refs_type + 'Ref mean len: %.2f' % np.mean([len([tok for sent in ref for tok in sent]) for ref in refs]))
        sprnt(refs_type + 'Ref mean words: %.2f' % np.mean([len([tok for sent in ref for tok in sent
                                                   if tok[-1] not in ['.', ':', '(', ')', ',']]) for ref in refs]))
        sprnt(refs_type + 'Ref mean sentence len: %.2f' %
              np.mean([len(sent) for ref in refs for sent in ref]))
        sprnt(refs_type + 'Ref mean sentence words: %.2f' %
              np.mean([len([tok for tok in sent if tok[-1] not in ['.', ':', '(', ')', ',']])
                       for ref in refs for sent in ref]))
        sent_nums = [len(ref) for ref in refs]
        sprnt(refs_type + 'Ref sentences min: %d  max: %d  mean: %.2f' %
              (np.mean(sent_nums), np.max(sent_nums), np.mean(sent_nums)))

        # ngram stats
        unigrams, uniq_unigrams = ngram_stats(refs, 1)
        sprnt(refs_type + 'Uniq unigrams: %d / %d = %.2f' % (uniq_unigrams, len(unigrams), uniq_unigrams / float(len(unigrams))))
        sprnt(refs_type + 'Top unigrams:\n' +
              '\n'.join(['  %-15s -- %5d' % (' '.join(ngram), freq)
                         for ngram, freq in sorted(unigrams.items(), key=lambda x: x[1], reverse=True)[:25]]))
        sprnt(refs_type + 'Entropy unigrams: %.4f' % entropy(unigrams))
        bigrams, uniq_bigrams = ngram_stats(refs, 2)
        sprnt(refs_type + 'Uniq bigrams: %d / %d = %.2f' % (uniq_bigrams, len(bigrams), uniq_bigrams / float(len(bigrams))))
        sprnt(refs_type + 'Top bigrams:\n' +
              '\n'.join(['  %-20s -- %5d' % (' '.join(ngram), freq)
                         for ngram, freq in sorted(bigrams.items(), key=lambda x: x[1], reverse=True)[:25]]))
        sprnt(refs_type + 'Entropy bigrams: %.4f' % entropy(bigrams))
        sprnt(refs_type + 'LM Entropy bigram: %.4f' % cond_entropy(bigrams, unigrams))
        trigrams, uniq_trigrams = ngram_stats(refs, 3)
        sprnt(refs_type + 'Uniq trigrams: %d / %d = %.2f' % (uniq_trigrams, len(trigrams), uniq_trigrams / float(len(trigrams))))
        sprnt(refs_type + 'Top trigrams:\n' +
              '\n'.join(['  %-25s -- %5d' % (' '.join(ngram), freq)
                         for ngram, freq in sorted(trigrams.items(), key=lambda x: x[1], reverse=True)[:25]]))
        sprnt(refs_type + 'Entropy trigrams: %.4f' % entropy(trigrams))
        sprnt(refs_type + 'LM Entropy trigram: %.4f' % cond_entropy(trigrams, bigrams))

    return stats



if __name__ == '__main__':
    print('\nE2E stats:\n=========')
    mrs, refs = read_e2e_data()
    data_stats(mrs, refs, {'name': [], 'near': []},
               'data/e2e-refs')

    print('\nSFREST stats:\n=========')
    mrs, refs = read_sfx_data()
    data_stats(mrs, refs, {'name': [], 'near': [], 'phone': [], 'address': [], 'postcode': [], 'count': [], 'area': []},
               'data/sfrest-refs')

    print('\nSFREST-inform stats:\n=========')
    mrs, refs = filter_inform(mrs, refs)
    data_stats(mrs, refs,
               {'name': [], 'near': [], 'phone': [], 'address': [], 'postcode': [], 'count': [], 'area': []},
               'data/sfrest_inform-refs')

    print('\nBAGEL stats:\n=========')
    mrs, refs = read_bagel_data()
    data_stats(mrs, refs,
               {'name': [], 'near': [], 'addr': [], 'phone': [], 'postcode': [], 'area': ['riverside', 'citycentre']},
               'data/bagel-refs')

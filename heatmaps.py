#!/usr/bin/env python2
# -"- coding: utf-8 -"-

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from argparse import ArgumentParser


SYS_SORT = ['testset-all', 'testset-rand',
            'TGen', 'Adapt', 'Chen', 'Gong',
            'Harv', 'NLE', 'Sheff2', 'Slug', 'Slug-alt', 'TNT1', 'TNT2', 'TR1', 'Zhang',
            'ZHAW1', 'ZHAW2', 'Sheff1', 'DANGNT',
            'FORGe1', 'FORGe3', 'TR2', 'TUDA', ]


def main(input_matrix, heatmap_prefix):

    data = pd.read_csv(input_matrix, sep='\t')
    # proper capitalization of the columns
    caps = {sys_label.lower() + '.delex.txt': sys_label for sys_label in SYS_SORT}
    data = data.replace(caps)

    # create the normalized mean
    norm_bleu = np.array(data.BLEU)
    norm_nist = np.array(data.NIST)
    norm_nist = np.min(np.stack((norm_nist / 10, np.ones(norm_nist.shape))), axis=0)
    norm_meteor = np.array(data.METEOR)
    norm_cider = np.array(data.CIDEr) / 10
    norm_rouge = np.array(data['ROUGE-L'])
    norm_mean = np.mean(np.stack((norm_bleu, norm_nist, norm_meteor, norm_rouge, norm_cider)), axis=0)
    data['MEAN'] = norm_mean

    # create the 2D matrixes & resort
    matrixes = []
    matrixes.append(data.pivot('Sys1', 'Sys2', 'MEAN'))
    matrixes.append(data.pivot('Sys1', 'Sys2', 'BLEU'))
    matrixes.append(data.pivot('Sys1', 'Sys2', 'NIST'))
    matrixes.append(data.pivot('Sys1', 'Sys2', 'METEOR'))
    matrixes.append(data.pivot('Sys1', 'Sys2', 'ROUGE-L'))
    matrixes.append(data.pivot('Sys1', 'Sys2', 'CIDEr'))
    matrixes = [matrix.reindex(SYS_SORT)[SYS_SORT[1:]] for matrix in matrixes]

    # print out the per-line averages for each column of the mean matrix
    means_of_means = matrixes[0].drop(matrixes[0].index[0]).mean(axis=1).sort_values(ascending=False)
    means_of_means.to_csv(heatmap_prefix + '-means.tsv', sep='\t')


    # draw & save the figures
    matplotlib.rcParams.update({'font.size': 10})
    plt.figure(figsize=(12, 9))
    for matrix, label in zip(matrixes, ['mean', 'bleu', 'nist', 'meteor', 'rouge', 'cider']):
        sns.heatmap(matrix, annot=True, cmap='magma')
        plt.savefig(heatmap_prefix + '-' + label + '.png')
        plt.savefig(heatmap_prefix + '-' + label + '.svg')
        plt.clf()


if __name__ == '__main__':
    ap = ArgumentParser(description='Build heatmaps')
    ap.add_argument('input_matrix', type=str, help='Input TSV file with scores')
    ap.add_argument('heatmap_prefix', type=str, help='Path prefix for output files')
    args = ap.parse_args()
    main(args.input_matrix, args.heatmap_prefix)

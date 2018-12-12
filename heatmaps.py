#!/usr/bin/env python2
# -"- coding: utf-8 -"-

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

resort = ['testset-all', 'testset-random1',
          'TGen', 'Slug', 'Slug-alt', 'TNT1', 'TNT2', 'Adapt', 'Chen', 'Gong',
          'Harv', 'NLE', 'Sheff2', 'TR1', 'Zhang', 'ZHAW1', 'ZHAW2', 'Sheff1', 'DANGNT',
          'FORGe1', 'FORGe3', 'TR2', 'TUDA',]

data = pd.read_csv('matrix-scores_noanon.tsv', sep='\t')

norm_bleu = np.array(data.BLEU)
x = np.array(data.NIST); norm_nist = np.min(np.stack((x / 10, np.ones(x.shape))), axis=0)
norm_meteor = np.array(data.METEOR)
norm_cider = np.array(data.CIDEr) / 10
norm_rouge = np.array(data['ROUGE-L'])
norm_mean = np.mean(np.stack((norm_bleu, norm_nist, norm_meteor, norm_rouge, norm_cider)), axis=0)
data['MEAN'] = norm_mean

mean = data.pivot('Sys1', 'Sys2', 'MEAN'); mean = mean.reindex(resort)[resort[1:]]
bleu = data.pivot('Sys1', 'Sys2', 'BLEU'); bleu = bleu.reindex(resort)[resort[1:]]
nist = data.pivot('Sys1', 'Sys2', 'NIST'); nist = nist.reindex(resort)[resort[1:]]
meteor = data.pivot('Sys1', 'Sys2', 'METEOR'); meteor = meteor.reindex(resort)[resort[1:]]
rouge = data.pivot('Sys1', 'Sys2', 'ROUGE-L'); rouge = rouge.reindex(resort)[resort[1:]]
cider = data.pivot('Sys1', 'Sys2', 'CIDEr'); cider = cider.reindex(resort)[resort[1:]]

matplotlib.rcParams.update({'font.size': 10})
plt.figure(figsize=(12,9))
ax = sns.heatmap(mean, annot=True, cmap='magma'); plt.savefig('mean.png'); plt.clf()
ax = sns.heatmap(mean, annot=True, cmap='magma'); plt.savefig('mean.svg'); plt.clf()
ax = sns.heatmap(bleu, annot=True, cmap='magma'); plt.savefig('bleu.png'); plt.clf()
ax = sns.heatmap(bleu, annot=True, cmap='magma'); plt.savefig('bleu.svg'); plt.clf()
ax = sns.heatmap(nist, annot=True, cmap='magma'); plt.savefig('nist.png'); plt.clf()
ax = sns.heatmap(nist, annot=True, cmap='magma'); plt.savefig('nist.svg'); plt.clf()
ax = sns.heatmap(meteor, annot=True, cmap='magma'); plt.savefig('meteor.png'); plt.clf()
ax = sns.heatmap(meteor, annot=True, cmap='magma'); plt.savefig('meteor.svg'); plt.clf()
ax = sns.heatmap(rouge, annot=True, cmap='magma'); plt.savefig('rouge.png'); plt.clf()
ax = sns.heatmap(rouge, annot=True, cmap='magma'); plt.savefig('rouge.svg'); plt.clf()
ax = sns.heatmap(cider, annot=True, cmap='magma'); plt.savefig('cider.png'); plt.clf()
ax = sns.heatmap(cider, annot=True, cmap='magma'); plt.savefig('cider.svg'); plt.clf()


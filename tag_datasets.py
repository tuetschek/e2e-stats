#!/usr/bin/env python3

from ufal.morphodita import Tagger, Forms, TaggedLemmas, TokenRanges
import os.path
from argparse import ArgumentParser


class MorphoTagger(object):
    """Morphodita analyzer/tagger wrapper."""

    def __init__(self, tagger_model):
        if not os.path.isfile(tagger_model):
            raise IOError('File %s does not exist' % tagger_model)
        self._tagger = Tagger.load(tagger_model)
        self._tokenizer = self._tagger.newTokenizer()
        self._forms_buf = Forms()
        self._tokens_buf = TokenRanges()
        self._tags_buf = TaggedLemmas()

    def tag(self, text):
        self._tokenizer.setText(text)
        out_buf = []
        while self._tokenizer.nextSentence(self._forms_buf, self._tokens_buf):
            self._tagger.tag(self._forms_buf, self._tags_buf)
            out_buf.append([(form, lemma.lemma, lemma.tag)
                            for (form, lemma) in zip(self._forms_buf, self._tags_buf)])
        return out_buf


def tag(tagger_model, in_file, out_file, output_format):
    with open(in_file, encoding='UTF-8') as fh:
        data = [l.strip() for l in fh.readlines()]
    tagger = MorphoTagger(tagger_model)

    # lemma_tag, one sentence per line (regardless of instances)
    if output_format == 'lca':
        tagged = ["\n".join([" ".join(['%s_%s' % (lemma, tag) for _, lemma, tag in sent])
                             for sent in tagger.tag(line)])
                  for line in data]
        tagged = "\n".join(tagged)
    # lowercase word/tag, one instance per line
    elif output_format == 'R':
        tagged = [" ".join(['%s/%s' % (word.lower(), tag)
                            for sent in tagger.tag(line)
                            for word, _, tag in sent])
                  for line in data]
        tagged = '"x"\n"' + "\n".join(['"' + line.replace('"', '""') + '"' for line in tagged])

    # word/lemma/tag (for the stats script)
    elif output_format == 'ngram':
        tagged = ["\t".join([" ".join(['%s/%s/%s' % (word.lower(), lemma, tag) for word, lemma, tag in sent])
                            for sent in tagger.tag(line)])
                  for line in data]
        tagged = "\n".join(tagged)

    # TODO
    elif output_format == 'collins':
        pass

    with open(out_file, mode='w', encoding='UTF-8') as fh:
        fh.write(tagged)


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('-t', '--tagger', '--tagger-model', type=str, help='Path to tagger',
                    default='morphodita/english-morphium-wsj-140407/english-morphium-wsj-140407.tagger')
    ap.add_argument('-f', '--format', '--output-format', type=str, choices=['lca', 'R', 'collins', 'ngram'],
                    required=True, help='Output format: for R (as OpenNLP), for ngram stats, ' +
                    'for LCA, for Collins\' parser?')
    ap.add_argument('input_file', type=str, help='Path to input text file')
    ap.add_argument('output_file', type=str, help='Path to output lemma_tag file (as required by LCA)')
    args = ap.parse_args()
    tag(args.tagger, args.input_file, args.output_file, args.format)


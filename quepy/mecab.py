#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from natto import MeCab

#from tagutil import str2tuple
from quepy import settings
from quepy.tagger import Word
from quepy.encodingpolicy import encoding_flexible_conversion as decode

class MecabTagger(object):
    """docstring, MecabTagger"""
    # TAGSET = set("""NNG NNP NNB NNBC NR NP VV VA VX VCP VCN MM MAG MAJ IC
    #                 JKS JKC JKG JKO JKB JKV JKQ JX JC EP EF EC ETN ETM
    #                 XPN XSN XSV XSA XR SF SE SSO SSC SC SY SL SH SN
    #                 UNKNOWN EOS""".split())

    def __init__(self, **kwargs):
        self.tagger = MeCab(kwargs)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        del self.tagger

    @staticmethod
    def tagged_tuple(node):
        surface = node.surface
        features = node.feature.split(',')
        first_pos = features[0].partition('+')[0]
        lemma = (features[7].partition('/')[0]
                    if features[4].startswith('Inflect')
                    else surface.lower())
        return Word(decode(surface, True), decode(lemma, True),
                    first_pos.decode('ascii'), node.cost)

    def parse(self, text):  # follow NLTK naming
        return [MecabTagger.tagged_tuple(node)
                    for node in self.tagger.parse(text.encode(settings.DEFAULT_ENCODING), as_nodes=True)
                        if not node.is_eos()]

    # def pos_tag_lines(self, lines)
    #     return (self.pos_tag(line) for line in lines)

# @click.command()
# @click.argument('input_file', type=click.File('rb'))
# @click.argument('output_file', type=click.File('wb'))
# def main(input_file, output_file):
#     with MecabTagger() as nm:
#         for line in input_file:
#             print(' '.join(nm.morphs(line)), file=output_file)
#             #print(' '.join(tuple2str(token) for token in nm.pos_tag(line)), file=output_file)


# if __name__ == '__main__':
#     main()

# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

from __future__ import unicode_literals

import logging

from quepy import settings
from quepy.encodingpolicy import assert_valid_encoding

logger = logging.getLogger("quepy.tagger")

class TaggingError(Exception):
    """
    Error parsing tagger's output.
    """
    pass


class Word(object):
    """
    Representation of a tagged word.
    Contains *token*, *lemma*, *pos tag* and optionally a *probability* of
    that tag.
    """
    _encoding_attrs = u"token lemma pos".split()
    _attrs = _encoding_attrs + [u"prob"]

    def __init__(self, token, lemma=None, pos=None, prob=None):
        self.pos = pos
        self.prob = prob
        self.lemma = lemma
        self.token = token

    def __setattr__(self, name, value):
        if name in self._encoding_attrs and value is not None:
            assert_valid_encoding(value)
        object.__setattr__(self, name, value)

    def __unicode__(self):
        attrs = (getattr(self, name, u"-") for name in self._attrs)
        return u"|".join(str(x) for x in attrs)

    def __repr__(self):
        return unicode(self)


def get_tagger():
    """
    Return a tagging function given some app settings.
    `Settings` is the settings module of an app.
    The returned value is a function that receives a unicode string and returns
    a list of `Word` instances.
    """
    from mecab import MecabTagger
    Tagger = MecabTagger

    def wrapper(string):
        assert_valid_encoding(string)
        with Tagger() as tagger:
            words = tagger.parse(string)
        # for word in words:
        #     if word.pos not in Tagger.TAGSET:
        #         logger.warning("Tagger emmited a non-mecab "
        #                        "POS tag {!r}".format(word.pos))
        return words
    return wrapper

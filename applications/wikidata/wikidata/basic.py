# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Basic questions for DBpedia.
"""
from __future__ import unicode_literals

from refo import Group, Plus, Question
from quepy.parsing import Lemma, Pos, QuestionTemplate, Token, Particle, \
                          Lemmas, Tokens
from quepy.dsl import HasKeyword, IsRelatedTo, HasType
from dsl import DefinitionOf, LabelOf, UTCof, LocationOf #, SameAs, IsPlace

compound = lambda s: s.replace(' ', '')

# NNG: 일반 명사, NNP: 고유 명사, SL: 외국어
noun = Pos("NNG") | Pos("NNP") | Pos("SL")
nouns = Plus(noun)
be = (Pos("JKS") | Pos("JX"))

class Thing(Particle):
    # MM: 관형사
    #regex = Question(Pos("MM")) + nouns
    regex = nouns

    def interpret(self, match):
        return HasKeyword(compound(match.words.tokens))


class WhatIs(QuestionTemplate):
    """
    Regex for questions like "온톨로지는 뭐야?"
    """
    # JKS: 주격 조사(이/가), JX: 보조사(은/는), VCP: 긍정 지정사(이다), SF: 마침표, 물음표, 느낌표
    regex = (Thing() + be +
             (Lemma("무엇") | Lemma("뭣")) + Question(Pos("VCP")) + Question(Pos("SF")))

    def interpret(self, match):
        label = DefinitionOf(match.thing)

        return label, "define"


class ListEntity(QuestionTemplate):
    """
    Regex for questions like "IBM 소프트웨어의 목록은?" "IBM 소프트웨어를 나열해"
    """
    # JKG: 관형격 조사(의), JKO: 목적격 조사(을/를), XSV: 동사 파생 접미사, VX: 보조 용언
    closing = (((Question(Pos("JKG")) + Lemma("목록") + Question(be)) |
               (Question(Pos("JKO")) + Lemma("나열") + Pos("XSV") + Question(Pos("VX"))))
               + Question(Pos("SF")))

    entity = Group(Pos("NNP") | Pos("NNG") | Pos("SL"), "entity")
    target = Group(Pos("NNG"), "target")
    regex = entity + Question(Pos("JKG")) + target + closing

    def interpret(self, match):
        entity = HasKeyword(match.entity.tokens)
        target_type = HasKeyword(match.target.lemmas)
        target = HasType(target_type) + IsRelatedTo(entity)
        label = LabelOf(target)

        return label, "enum"


class WhatTimeIs(QuestionTemplate):
    """
    Regex for questions about the time
    Ex: "(지금) 베네치아는 (지금) 몇 시지?", "베네치아의 (현재|지금) 시간은?"
    """

    place = Group(nouns, "place")
    regex1 = (Question(Token("지금")) + place + Question(be) + Question(Token("지금")) + Tokens("몇 시") + Question(Pos("VCP")))  # VCP: 긍정 지정사
    regex2 = (place + Question(Pos("JKG")) + (Token("현재") | Token("지금")) + (Token("시간") | Token("시각")) + Question(be))     # JKG: 관형격 조사
    regex = (regex1 | regex2) + Question(Pos("SF"))

    def interpret(self, match):
        print match.place.lemmas.title()
        place = HasKeyword(match.place.lemmas.title()) #+ IsPlace()
        utc_offset = UTCof(place)

        return utc_offset, "time"


class WhereIsQuestion(QuestionTemplate):
    """
    Ex: "분당구는 어디지?", "분당구의 위치는?"
    """

    place = Group(nouns, "place")
    regex = (place + ((be + Lemma("어디") + Question(Pos("VCP"))) |
                      (Question(Pos("JKG")) + Lemma("위치") + Question(be)))
             + Question(Pos("SF")))


    def interpret(self, match):
        place = HasKeyword(compound(match.place.tokens))
        location = LocationOf(place)

        return location, "location"

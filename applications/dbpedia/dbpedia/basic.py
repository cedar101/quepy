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

from refo import Group, Plus, Question, Any
from quepy.parsing import Lemma, Pos, QuestionTemplate, Token, \
                          Lemmas, Tokens, Poss, WordList, Particle
from quepy.dsl import IsRelatedTo
from dsl import HasKeyword, DefinitionOf, LabelOf, IsPlace, UTCof, LocationOf, PrimaryTopicOf, SameAs, HasType

#HasType.dataset = 'SERVICE <http://dbpedia.org>' #DATASETS['ko']

#combine = lambda s: s.replace(' ', '')

# NNG: 일반 명사, NNP: 고유 명사, SL: 외국어
noun = Pos("NNG") | Pos("NNP") | Pos("SL") | Pos('UNKNOWN')
nouns = Plus(noun)
be = (Pos("JKS") | Pos("JX"))
# quoted = Group((Token("'") + Plus(Any()) + Token("'")) |    # 따옴표를 사용하면
#                (Token('"') + Plus(Any()) + Token('"')),     # 어떤 품사든 사용 가능
#                "quoted")

# class Particle(quepy.parsing.Particle):
#     def __init__(self, name=None):
#         self.regex = self.regex | quoted
#         super(Particle, self).__init__(name)


class Thing(Particle):
    regex = nouns

    def interpret(self, match):
        keyword = HasKeyword(match.words.tokens, match.words[0].pos != 'UNKNOWN')
        return keyword


class WhatIs(QuestionTemplate):
    """
    Regex for questions like "아프리카TV가 뭐야?", "온톨로지의 정의는?"
    """
    # JKS: 주격 조사(이/가), JX: 보조사(은/는), VCP: 긍정 지정사(이다), SF: 마침표, 물음표, 느낌표
    regex = (Thing() + Question(Pos('JKG')) + Question(Token('정의')) + Question(be) +
             Question(((Lemma('뭣') | Lemma('뭐')) + Pos('VCP')) | Lemma('무엇') + Poss('VCP EF')) +
             Question(Pos("SF")))

    def interpret(self, match):
        label = DefinitionOf(match.thing)

        return label, "define"


class ListEntity(QuestionTemplate):
    """
    XXX: No answer of SPARQL found.

    Regex for questions like "구글 소프트웨어의 목록은?" "구글의 소프트웨어를 나열해"
    """
    # JKG: 관형격 조사(의), JKO: 목적격 조사(을/를), XSV: 동사 파생 접미사, VX: 보조 용언
    closing = (((Question(Pos("JKG")) + Lemma("목록") + Question(be)) |
               (Question(Pos("JKO")) + Lemma("나열") + Pos("XSV") + Question(Pos("VX"))))
               + Question(Pos("SF")))

    entity = Group(noun, "entity")
    target = Group(Pos("NNG"), "target")
    regex = entity + Question(Pos("JKG")) + target + closing

    def interpret(self, match):
        entity = SameAs(HasKeyword(match.entity.tokens))
        target_type = SameAs(HasKeyword(match.target.lemmas))
        # entity = HasKeyword(match.entity.tokens)
        # target_type = HasKeyword(match.target.lemmas)
        #import pdb; pdb.set_trace()

        target = HasType(target_type) + IsRelatedTo(entity)
        label = LabelOf(target)

        return label, "enum"


class Place(Particle):
    regex = nouns

    def interpret(self, match):
        place_ko = HasKeyword(match.words.tokens)
        place_en = SameAs(place_ko) + IsPlace()
        return place_en


class WhatTimeIs(QuestionTemplate):
    """
    Regex for questions about the time
    Ex: "(지금) 뉴욕은 (지금) 몇 시지?", "뉴욕의 (현재|지금) 시간은?"
    """

    regex1 = (Question(Token("지금")) + Place() + Question(be) +
              Question(Token("지금")) + Tokens("몇 시") + Question(Pos("VCP")))  # VCP: 긍정 지정사
    regex2 = (Question(Token("현재") | Token("지금")) + Place() + Question(Pos("JKG"))
              + Question(Token("현재") | Token("지금")) + (Token("시간") | Token("시각"))
              + Question(be))     # JKG: 관형격 조사
    regex = (regex1 | regex2) + Question(Pos("SF"))

    def interpret(self, match):
        utc_offset = UTCof(match.place)

        return utc_offset, "time"


class WhereIsQuestion(QuestionTemplate):
    """
    Ex: "분당구는 어디지?", "분당구의 위치는?", "분당구는 어디 있어?"
    """

    regex = (Place() +
             ((Question(be) + Lemma("어디") + Question(Pos("VCP") | Poss('VA EF'))) |
              (Question(Pos("JKG")) + Lemma("위치") + Question(be)))
             + Question(Pos("SF")))


    def interpret(self, match):
        location = LocationOf(match.place)

        return location, "location"

# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
People related regex
"""
from __future__ import unicode_literals

from refo import Star, Plus, Question, Any
#from quepy.dsl import HasKeyword
from quepy.parsing import Lemma, Lemmas, Pos, QuestionTemplate, Particle
from dsl import HasKeyword, IsPerson, LabelOf, DefinitionOf, BirthDateOf, BirthPlaceOf, SameAs, PrimaryTopicOf

from .basic import nouns, be

class Person(Particle):
    regex = nouns

    def interpret(self, match):
        name = match.words.tokens
        person = HasKeyword(name)
        return person
        # wikipedia = About(person)
        # dbpedia = PrimaryTopicOf(wikipedia) + IsPerson()
        # return dbpedia


class WhoIs(QuestionTemplate):
    """
    Regex for questions like "원빈이 누구지?"
    """
    regex = (Person() + be +
             Lemma("누구") + Question(Pos("VCP")) + Question(Pos("SF")))


    def interpret(self, match):
        definition = DefinitionOf(match.person)
        return definition, "define"


class HowOldIsQuestion(QuestionTemplate):
    """
    Ex:  "원빈은 몇 살이지?", "원빈의 나이는?"
    """

    regex = (Person()   # EF: 종결 어미, JKG: 관형격 조사
            + ((Question(be) + Lemmas("몇 살") + Question(Pos("VCP")) + Question(Pos("EF"))) |
               (Question(Pos("JKG")) + Lemma("나이") + Question(be)))
            + Question(Pos("SF")))

    def interpret(self, match):
        birth_date = BirthDateOf(match.person)
        return birth_date, "age"


class WhereIsFromQuestion(QuestionTemplate):
    """
    Ex: "원빈의 출신지는 (어디야)?", "원빈은 어디 출신이야?"
    """

    regex = (Person()
             + ((Question(Pos("JKG")) + Lemma("출신")) |
                (Question(be) + Lemmas("어디 출신")))
             + Star(Any()))

    def interpret(self, match):
        birth_place = BirthPlaceOf(match.person)
        label = LabelOf(birth_place)

        return label, "enum"

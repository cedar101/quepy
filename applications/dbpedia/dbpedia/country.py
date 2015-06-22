# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Coutry related regex
"""
from __future__ import unicode_literals

from refo import Star, Plus, Question, Any
#from quepy.dsl import HasKeyword
from quepy.parsing import Lemma, Lemmas, Pos, QuestionTemplate, Token, Particle
from dsl import HasKeyword, IsCountry, IncumbentOf, CapitalOf, \
    LabelOf, LanguageOf, PopulationOf, PresidentOf, PrimaryTopicOf

from .basic import nouns, be

class Country(Particle):
    regex = nouns

    def interpret(self, match):
        name = match.words.tokens.title()
        country = HasKeyword(name) + IsCountry()
        return country
        # wikipedia = About(country)
        # dbpedia = PrimaryTopicOf(wikipedia) + IsCountry()
        # return dbpedia


class PresidentOfQuestion(QuestionTemplate):
    """
    Regex for questions about the president of a country.
    Ex: "아르헨티나의 대통령은 (누구지)?"
    """

    regex = (Country() + Question(Pos("JKG")) + Lemma("대통령") + Question(be) +
             Question(Lemma("누구")) + Question(Pos("VCP")) + Question(Pos("SF")))

    def interpret(self, match):
        president = PresidentOf(match.country)
        incumbent = IncumbentOf(president)
        label = LabelOf(incumbent)

        return label, "enum"


class CapitalOfQuestion(QuestionTemplate):
    """
    Regex for questions about the capital of a country.
    Ex: "볼리비아의 수도는 (어디지)?"
    """

    regex = (Country() + Question(Pos("JKG")) + Lemma("수도") + Question(be) +
             Question(Lemma("어디")) + Question(Pos("VCP")) + Question(Pos("SF")))

    def interpret(self, match):
        capital = CapitalOf(match.country)
        label = LabelOf(capital)
        return label, "enum"


# FIXME: the generated query needs FILTER isLiteral() to the head
# because dbpedia sometimes returns different things
class LanguageOfQuestion(QuestionTemplate):
    """
    Regex for questions about the language spoken in a country.
    Ex: "아르헨티나의 (언어|공용어|공용언어)는 (뭐지?)
        "아르헨티나는 (어떤|무슨) (말|언어|공용어|공용언어)를 (말하지|하지|쓰지)?
    """

    openings = (Lemma("what") + Token("is") + Pos("DT") +
                Question(Lemma("official")) + Lemma("language")) | \
               (Lemma("what") + Lemma("language") + Token("is") +
                Lemma("speak"))

    language = Lemma("언어") | Lemma("공용어") | Lemmas("공용 언어") | Lemma("말")
    regex = (Country()
             + ((Question(Pos("JKG")) + language + Question(be)
                + Question(Lemma("뭣") | Lemma("무엇"))
                + Question(Pos("VCP")) + Question(Pos("SF"))) |
                (Question(be) + (Lemma("어떤") | Lemma("무슨"))
                + language + Question(Pos("JKO")) + Star(Any()))))  # JKO: 목적격 조사

    def interpret(self, match):
        language = LanguageOf(match.country)
        return language, "enum"


class PopulationOfQuestion(QuestionTemplate):
    """
    Regex for questions about the population of a country.
    Ex: "인도의 인구(수)는?
        "인도는 얼마나 많은 사람이 살지?" "인도는 얼마나 많이 살지?"
    """

    regex = (Country()
             + ((Question(Pos("JKG"))
                + (Lemma("인구") | Lemma("인구수")) + Question(Lemma("수"))
                + Question(be)) |
                (Question(be) + Lemma("얼마나")
                 + (Lemmas("많 은 사람 이") | Lemma("많이")) + Lemma("살")
                 + Question(Pos("VCP"))))
             + Question(Pos("SF")))

    def interpret(self, match):
        population = PopulationOf(match.country)
        return population, ("literal", lambda p: "{:,} 명".format(int(p)))

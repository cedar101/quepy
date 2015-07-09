# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Movie related regex.
"""
from __future__ import unicode_literals

from refo import Plus, Question, Star, Any
#from quepy.dsl import HasKeyword
from quepy.parsing import Lemma, Lemmas, Pos, Poss, Token, Tokens, QuestionTemplate, WordList, Particle
from dsl import HasKeyword, IsMovie, NameOf, IsPerson, \
    DirectedBy, LabelOf, DurationOf, HasActor, HasName, ReleaseDateOf, \
    DirectorOf, StarsIn, DefinitionOf, SameAs, DATASETS

from .basic import nouns, be

class Movie(Particle):
    # 명사, 영어, 숫쟈로만 이루어진 제목은 따옴표 불필요
    regex = (Plus(Pos("NNP") | Pos('NNG') | Pos("SL")) + Question(Pos("SN"))) | Pos('UNKNOWN')

    def interpret(self, match):
        return HasKeyword(match.words.tokens) + IsMovie(dataset=DATASETS['ko'])


class Actor(Particle):
    regex = Plus(Pos("NNP") | Pos("SL"))

    def interpret(self, match):
        name = match.words.tokens
        return SameAs(HasKeyword(name)) + IsPerson()


class Director(Particle):
    regex = Plus(Pos("NNP") | Pos("SL"))

    def interpret(self, match):
        name = match.words.tokens
        return SameAs(HasKeyword(name)) + IsPerson()


class ListMoviesQuestion(QuestionTemplate):
    """
    Ex: "list movies"
    """

    regex = Lemma("list") + (Lemma("movie") | Lemma("film"))

    def interpret(self, match):
        movie = IsMovie()
        name = NameOf(movie)
        return name, "enum"


class MoviesByDirectorQuestion(QuestionTemplate):
    """
    Ex: "쿠엔틴 타란티노가 감독한 영화(의 목록(은)?|을 나열해.)"
        "마틴 스코세지가 감독한 영화"
        "멜 깁슨이 감독한 영화는 뭐(가 있)지?"
    """

    regex = (Director() + Question(Pos('JKS')) + Token("감독") +
             Question(Pos('JKG') | ((Pos('XSA') | Pos('XSV')) + Question(Pos('ETM')))) +
             Token('영화') + Star(Any(), greedy=False))

    def interpret(self, match):

        movie = DirectedBy(match.director) + IsMovie()
        movie_name = LabelOf.to_korean(movie)
        #LabelOf(SameAs(movie, DATASETS['en']), DATASETS['ko'])

        return movie_name, "enum"


class MovieDurationQuestion(QuestionTemplate):
    """
    Ex: "펄프 픽션은 얼마나 길지?"
        "벤허의 러닝 타임은 얼마나 (하지|해|되지|돼)?"
    """

    regex = (Movie() + Question(Pos('JKG')) + Question(Lemmas('러닝 타임') | Lemma('런타임'))
             + Question(be) + Question(Lemma('얼마나'))
             + Question(Pos('VV') | Pos('VA')) + Question(Pos('EF'))
             + Question(Pos('SF')))

    def interpret(self, match):
        duration = DurationOf(SameAs(match.movie))
        return duration, ("literal", "{:n} 분")


class ActedOnQuestion(QuestionTemplate):
    """
    Ex: "멜 깁슨이 나온(나오는|출연한) 영화(의 목록|를 나열해)"
        "어떤 영화에 제니퍼 애니스톤이 나왔지(출연했지)?"
    """

    acted_on = (Lemma("appear") | Lemma("act") | Lemma("star"))
    movie = (Lemma("movie") | Lemma("movies") | Lemma("film"))
    regex = (Question(Lemma("list")) + movie + Lemma("with") + Actor()) | \
            (Question(Pos("IN")) + (Lemma("what") | Lemma("which")) +
             movie + Lemma("do") + Actor() + acted_on + Question(Pos("."))) | \
            (Question(Pos("IN")) + Lemma("which") + movie + Lemma("do") +
             Actor() + acted_on) | \
            (Question(Lemma("list")) + movie + Lemma("star") + Actor())

    def interpret(self, match):
        movie = IsMovie() + HasActor(match.actor)
        movie_name = NameOf(movie)
        return movie_name, "enum"


class MovieReleaseDateQuestion(QuestionTemplate):
    """
    Ex: "When was The Red Thin Line released?"
        "Release date of The Empire Strikes Back"
    """

    regex = ((Lemmas("when be") + Movie() + Lemma("release")) |
            (Lemma("release") + Question(Lemma("date")) +
             Pos("IN") + Movie())) + \
            Question(Pos("."))

    def interpret(self, match):
        release_date = ReleaseDateOf(match.movie)
        return release_date, "literal"


class DirectorOfQuestion(QuestionTemplate):
    """
    Ex: "'빅 피쉬'의 감독은 (누구지?)"
        "포카혼타스는(를) 누가 감독했지?"
    """

    regex = (Movie() +
             ((Question(Pos('JKG')) + Token('감독') + Question(be) +
               Question(Token("누구")) + Question(Pos("VCP"))) |
              (Question(Pos('JX') | Pos('JKO')) +
               Tokens('누가 감독') + Question(Poss('XSV EF'))))
             + Question(Pos("SF")))

    def interpret(self, match):
        director = DirectorOf(SameAs(match.movie)) + IsPerson()
        director_name = NameOf.to_korean(director)
        return director_name, "literal"


class ActorsOfQuestion(QuestionTemplate):
    """
    Ex: "'파이트 클럽'의(에 출연한) 배우(들) (목록)"
        "배트맨2의 배우는 누구누구지?"
        "배트맨2(에|는) 누가 출연했지?"
        "프레데터2(에|는) 누가 연기했지?"
    """

    regex1 = (Movie() +
              Question(Pos('JKG') |
                       (Pos('JKB') + Lemma('출연') + (Pos('XSA') | Pos('XSV ETM')))) +
              (Token('배우') | Token('연기자')) + Star(Any()))
    regex2 = (Movie() + Question(Pos('JKB')) + Question(Pos('JX')) +
              (Token('누가') | Tokens('누구 누구')) +
              (((Token('출연') | Token('연기')) + Question(Poss('XSV EF'))) |
               ((Token('나왔') | Token('나오')) + Pos('EF')) |
               Token('나와')) + Question(Pos('SF'))
             )
    regex = regex1 | regex2

    def interpret(self, match):
        actor = NameOf(StarsIn(SameAs(match.movie)) + IsPerson())
        return actor, "enum"


class PlotOfQuestion(QuestionTemplate):
    """
    Ex: "'파이트 클럽'은 어떤(뭐에 대한) 내용이지?"
        "터미네이터의 플롯"
        "터미네이터2의 내용"
    """

    regex1 = (Movie() + Question(Pos('JKG')) +
              (Token('플롯') | Token('내용') | Token('줄거리') | Token('영')) + Star(Any()))
    regex2 = (Movie() + Question(be) +
              (Lemma('어떤') | Lemmas('어떠 한') | Lemma('무슨') |
               ((Lemma('뭐') | Lemma('무엇')) + Lemmas('에 대한'))) +
              (Token('내용') | Token('영화')) +
              Question(Pos('VCP')) + Question(Pos('EF')) + Question(Pos('SF')))
    regex = regex1 | regex2

    def interpret(self, match):
        definition = DefinitionOf(match.movie)
        return definition, "define"

# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Music related regex
"""

from refo import Plus, Question, Star, Any
#from quepy.dsl import HasKeyword
from quepy.parsing import Token, Tokens, Lemma, Lemmas, Pos, Poss, QuestionTemplate
from dsl import HasKeyword, IsBand, LabelOf, IsMemberOf, ActiveYears, MusicGenreOf, \
    NameOf, IsAlbum, ProducedBy, SameAs

from .basic import nouns, be, Particle

class MusicalArtist(Particle):
    ''' dbpedia-owl: MusicalArtist'''
    regex = nouns

    def interpret(self, match):
        name = match.words.tokens
        return SameAs(HasKeyword(name))


class Band(Particle):
    regex = nouns

    def interpret(self, match):
        name = match.words.tokens.title()
        return SameAs(HasKeyword(name)) + IsBand()


class BandMembersQuestion(QuestionTemplate):
    """
    Regex for questions about band member.

    Ex: "라디오헤드 멤버"
        "메탈리카의 멤버는?"
    """
    who = (Lemma('누구') | Lemma('누가'))

    regex = (Question(who) + Band() + Question(Pos('JKG')) +
             Lemma("멤버") + Question(Pos('XSN')) + # 명사 파생 접미사
             Question(be) + Question(who) + Star(Any()))

    def interpret(self, match):
        member = IsMemberOf(match.band)
        label = LabelOf(member)
        return label, "enum"


class FoundationQuestion(QuestionTemplate):
    """
    Regex for questions about the creation of a band.

    Ex: "핑크 플로이드는 언제 결성했어?"
        "언제 콘이 활동을 시작했지?"
        "라디오헤드는 언제 나왔지?"
    """

    regex1 = (Question(Lemma('언제')) + Band() + Question(be) + Question(Lemma('언제'))
              + (((Lemma("결성") | (Lemma("활동") + Question(Pos('JKO')) + Lemma("시작"))) + Question(Pos('XSV')))
                 | Lemma('나오'))
              + Question(Pos('EF') | Pos('EC')) + Question(Pos("SF")))
    regex2 = (Band() + Question(Pos('JKG')) + (Lemmas('결성 연도') | Lemmas('활동 시작 연도'))
              + Question(be)
              + Question(Lemma('언제')) + Question(Pos("VCF")) + Question(Pos("SF")))
    regex = regex1 | regex2

    def interpret(self, match):
        active_years = ActiveYears(match.band)
        return active_years, ("literal", "{}년")


class GenreQuestion(QuestionTemplate):
    """
    Regex for questions about the genre of a band.
    Ex: "고릴라즈의 장르는 뭐지?"
        "라디오헤드의 (음악) 장르"
    """

    regex = (Band() + Question(Pos('JKG')) +
             Question(Token('음악')) + Token('장르') + Question(be) +
             Question((Lemma('뭣') + Pos('VCP')) | Lemma('무엇') + Poss('VCP EF')) +
             Question(Pos('SF')))

    def interpret(self, match):
        genre = MusicGenreOf(match.band)
        label = LabelOf.to_korean(genre)
        return label, "enum"


class AlbumsOfQuestion(QuestionTemplate):
    """
    Ex: "핑크 플로이드의 앨범을 나열해봐."
        "펄 잼이 만든 앨범이 뭐지?"
        "메탈리카의 앨범 (목록)"
    """

    regex = (MusicalArtist() +
             Question(Pos('JKG') | (Pos('JKS') + (Token('만든') | Tokens('레코딩 한') | Tokens('제작 한')))) +
             Token('앨범') +
             ((Question(Pos('JKG')) + Question(Token('목록'))) |
              (Question(be) + Question((Lemma('뭣') + Pos('VCP')) | Lemma('무엇') + Poss('VCP EF'))) |
              (Question(Pos('JKO')) + Question(Token('나열')) + Question(Pos('XSV')) + Question(Pos('VX')))) + # 보조 용언
              Question(Pos('SF')))

    def interpret(self, match):
        album = IsAlbum() + ProducedBy(match.musicalartist)
        name = NameOf(album)
        return name, "enum"

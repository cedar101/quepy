# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
DBpedia quepy.
"""
# from refo import Group, Plus, Question
# from quepy.parsing import Lemma, Pos, QuestionTemplate, Token, Particle, \
#                           Lemmas, Tokens

# # NNG: 일반 명사, NNP: 고유 명사, SL: 외국어
# noun = Pos("NNG") | Pos("NNP") | Pos("SL")
# nouns = Plus(noun)
# be = (Pos("JKS") | Pos("JX"))

from basic import *
from music import *
from movies import *
from people import *
from country import *
from tvshows import *
from writers import *

# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Domain specific language for DBpedia quepy.
"""
from __future__ import unicode_literals

from quepy.expression import Expression

ENDPOINTS = {
    'en': 'http://dbpedia.org/sparql',
    'ko': '', #'http://127.0.0.1:3030/dbpedia-ko/sparql', #, 'http://ko.dbpedia.org/sparql',
    'wd': 'http://milenio.dcc.uchile.cl/sparql'
}

Expression.endpoint = ENDPOINTS['en']

import quepy.dsl
reload(quepy.dsl)
from quepy.dsl import FixedType, FixedRelation, FixedDataRelation, predicate

# Setup the Keywords for this application
# HasKeyword.language = "ko"
# HasKeyword.endpoint = ENDPOINTS['ko']
# HasKeyword.constraint = 'FILTER(STRSTARTS(STR({}), "http://dbpedia.org"))'
# HasKeyword.sanitize = staticmethod(lambda s: s.replace(' ', ''))
# HasKeyword = predicate(relation="rdfs:label")(HasKeyword)

@predicate(relation=u"rdfs:label")
class HasKeyword(quepy.dsl.HasKeyword):
    language = "ko"
    endpoint = ENDPOINTS['ko']
    constraint = 'FILTER(STRSTARTS(STR({}), "http://dbpedia.org"))'

    @staticmethod
    def sanitize(text):
        return text.replace(' ', '')


class IsPerson(FixedType):
    fixedtype = "foaf:Person"

class IsPlace(FixedType):
    fixedtype = "dbpedia-owl:Place"

class IsCountry(FixedType):
    fixedtype = "dbpedia-owl:Country"

class IsBand(FixedType):
    fixedtype = "dbpedia-owl:Band"

class IsAlbum(FixedType):
    fixedtype="dbpedia-owl:Album"

class IsTvShow(FixedType):
    fixedtype="dbpedia-owl:TelevisionShow"

class IsMovie(FixedType):
    fixedtype="dbpedia-owl:Film"

class IsBook(FixedType):
    fixedtype="dbpedia-owl:Book"


@predicate(relation="dbpprop:showName")
class HasShowName(FixedDataRelation):
    language = "en"

@predicate(relation="dbpprop:name")
class HasName(FixedDataRelation):
    language = "en"

@predicate(relation="rdfs:comment")
class DefinitionOf(FixedRelation):
    reverse = True

@predicate(relation="rdfs:label")
class LabelOf(FixedRelation):
    reverse = True

@predicate(relation="dbpprop:utcOffset")
class UTCof(FixedRelation):
    reverse = True

@predicate(relation="dbpprop:leaderTitle")
class PresidentOf(FixedRelation):
    reverse = True

@predicate(relation="dbpprop:incumbent")
class IncumbentOf(FixedRelation):
    reverse = True

@predicate(relation="dbpedia-owl:capital")
class CapitalOf(FixedRelation):
    reverse = True

@predicate(relation="dbpprop:officialLanguages")
class LanguageOf(FixedRelation):
    reverse = True

@predicate(relation="dbpprop:populationCensus")
class PopulationOf(FixedRelation):
    reverse = True

@predicate(relation="dbpedia-owl:bandMember")
class IsMemberOf(FixedRelation):
    reverse = True

@predicate(relation="dbpprop:yearsActive")
class ActiveYears(FixedRelation):
    reverse = True

@predicate(relation="dbpedia-owl:genre")
class MusicGenreOf(FixedRelation):
    reverse = True

@predicate(relation="dbpedia-owl:producer")
class ProducedBy(FixedRelation):
    pass

@predicate(relation="dbpprop:birthDate")
class BirthDateOf(FixedRelation):
    reverse = True

@predicate(relation="dbpedia-owl:birthPlace")
class BirthPlaceOf(FixedRelation):
    reverse = True

@predicate(relation="dbpedia-owl:releaseDate")
class ReleaseDateOf(FixedRelation):
    reverse = True

@predicate(relation="dbpprop:starring")
class StarsIn(FixedRelation):
    reverse = True

@predicate(relation="dbpedia-owl:numberOfEpisodes")
class NumberOfEpisodesIn(FixedRelation):
    reverse = True

@predicate(relation="dbpprop:showName")
class ShowNameOf(FixedRelation):
    reverse = True

@predicate(relation="dbpprop:starring")
class HasActor(FixedRelation):
    pass

@predicate(relation="dbpprop:creator")
class CreatorOf(FixedRelation):
    reverse = True

@predicate(relation="foaf:name")        # relation = "dbpprop:name"
class NameOf(FixedRelation):
    reverse = True

@predicate(relation="dbpedia-owl:director")
class DirectedBy(FixedRelation):
    pass

@predicate(relation="dbpedia-owl:director")
class DirectorOf(FixedRelation):
    reverse = True

# DBpedia throws an error if the relation it's
# dbpedia-owl:Work/runtime so we expand the prefix
# by giving the whole URL.
@predicate(relation="<http://dbpedia.org/ontology/Work/runtime>")
class DurationOf(FixedRelation):
    reverse = True

@predicate(relation="dbpedia-owl:author")
class HasAuthor(FixedRelation):
    pass

@predicate(relation="dbpedia-owl:author")
class AuthorOf(FixedRelation):
    reverse = True

@predicate(relation="grs:point")    # "dbpedia-owl:location"
class LocationOf(FixedRelation):
    reverse = True

@predicate(relation="owl:sameAs")
class SameAs(FixedRelation):
    reverse = True

@predicate(relation='schema:about')
class About(FixedRelation):
    endpoint=ENDPOINTS['wd']
    constraint='FILTER(STRSTARTS(STR({}), "http://en.wikipedia.org"))'

@predicate(relation="foaf:isPrimaryTopicOf")
class PrimaryTopicOf(FixedRelation):
    pass
    #reverse = True

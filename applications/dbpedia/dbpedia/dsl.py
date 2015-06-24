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

DATASETS = {
    'en': 'GRAPH <http://dbpedia.org>',
    'ko': 'GRAPH <http://ko.dbpedia.org>',
}

Expression.dataset = DATASETS['en'] # default

import quepy.dsl
reload(quepy.dsl)
from quepy.dsl import FixedType, FixedRelation, FixedDataRelation, HasType, relation

@relation(u"(^(dbpedia-owl:wikiPageRedirects|dbpedia-owl:wikiPageDisambiguates)*)/rdfs:label")
class HasKeyword(quepy.dsl.HasKeyword):
    '''Setup the Keywords for this application'''
    language = 'ko'
    dataset = DATASETS[language]
    constraint = 'FILTER NOT EXISTS {{ {} rdf:type skos:Concept. }}'

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
    fixedtype = "dbpedia-owl:Album"

class IsTvShow(FixedType):
    fixedtype = "dbpedia-owl:TelevisionShow"

class IsMovie(FixedType):
    fixedtype = "dbpedia-owl:Film"

class IsBook(FixedType):
    fixedtype = "dbpedia-owl:Book"


@relation("dbpprop:showName")
class HasShowName(FixedDataRelation):
    language = "en"

@relation("dbpprop:name")
class HasName(FixedDataRelation):
    language = "en"


@relation("owl:sameAs")
class SameAs(FixedRelation):
    reverse = True
    dataset = DATASETS['ko']

@relation("rdfs:comment")
class DefinitionOf(FixedRelation):
    reverse = True
    dataset = DATASETS['ko']

@relation("rdfs:label")
class LabelOf(FixedRelation):
    reverse = True

#@relation("dbpprop:utcOffset")
@relation("dbpedia-owl:utcOffset")
class UTCof(FixedRelation):
    reverse = True

@relation("dbpprop:leaderTitle")
class PresidentOf(FixedRelation):
    reverse = True

@relation("dbpprop:incumbent")
class IncumbentOf(FixedRelation):
    reverse = True

@relation("dbpedia-owl:capital")
class CapitalOf(FixedRelation):
    reverse = True

@relation("dbpprop:officialLanguages")
class LanguageOf(FixedRelation):
    reverse = True

@relation("dbpprop:populationCensus")
class PopulationOf(FixedRelation):
    reverse = True

@relation("dbpedia-owl:bandMember")
class IsMemberOf(FixedRelation):
    reverse = True

@relation("dbpprop:yearsActive")
class ActiveYears(FixedRelation):
    reverse = True

@relation("dbpedia-owl:genre")
class MusicGenreOf(FixedRelation):
    reverse = True

@relation("dbpedia-owl:producer")
class ProducedBy(FixedRelation):
    pass

@relation("dbpprop:birthDate")
class BirthDateOf(FixedRelation):
    reverse = True

@relation("dbpedia-owl:birthPlace")
class BirthPlaceOf(FixedRelation):
    reverse = True

@relation("dbpedia-owl:releaseDate")
class ReleaseDateOf(FixedRelation):
    reverse = True

@relation("dbpprop:starring")
class StarsIn(FixedRelation):
    reverse = True

@relation("dbpedia-owl:numberOfEpisodes")
class NumberOfEpisodesIn(FixedRelation):
    reverse = True

@relation("dbpprop:showName")
class ShowNameOf(FixedRelation):
    reverse = True

@relation("dbpprop:starring")
class HasActor(FixedRelation):
    pass

@relation("dbpprop:creator")
class CreatorOf(FixedRelation):
    reverse = True

@relation("foaf:name")        # relation = "dbpprop:name"
class NameOf(FixedRelation):
    reverse = True

@relation("dbpedia-owl:director")
class DirectedBy(FixedRelation):
    pass

@relation("dbpedia-owl:director")
class DirectorOf(FixedRelation):
    reverse = True

# DBpedia throws an error if the relation it's
# dbpedia-owl:Work/runtime so we expand the prefix
# by giving the whole URL.
@relation("<http://dbpedia.org/ontology/Work/runtime>")
class DurationOf(FixedRelation):
    reverse = True

@relation("dbpedia-owl:author")
class HasAuthor(FixedRelation):
    pass

@relation("dbpedia-owl:author")
class AuthorOf(FixedRelation):
    reverse = True

@relation("grs:point")    # "dbpedia-owl:location"
class LocationOf(FixedRelation):
    reverse = True

@relation("foaf:isPrimaryTopicOf")
class PrimaryTopicOf(FixedRelation):
    pass
    #reverse = True

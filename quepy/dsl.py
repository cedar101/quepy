# coding: utf-8
# pylint: disable=C0111

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Domain specific language definitions.
"""
from collections import namedtuple
from copy import copy

from quepy.expression import Expression
from quepy.encodingpolicy import encoding_flexible_conversion

Relation = namedtuple('Relation', 'iri dataset constraint')

def relation(iri):
    def decorate(cls):
        cls.iri = iri
        cls.relation = property(lambda self: Relation(self.iri, self.dataset, self.constraint))
        #cls.relation = Relation(iri, cls.dataset, cls.constraint)
        return cls
    return decorate

class FixedRelation(Expression):
    """
    Expression for a fixed relation. It states that "A is related to B"
    through the relation defined in `relation`.
    """

    relation = None
    reverse = False

    def __init__(self, destination, dataset=None, reverse=None):
        if reverse is None:
            reverse = self.reverse

        Expression.__init__(self)

        if self.relation is None:
            raise ValueError("You *must* define the `relation` "
                             "class attribute to use this class.")
        if dataset is not None:
            self.dataset = dataset

        self.nodes = copy(destination.nodes)
        self.head = destination.head
        self.destination = destination
        self.decapitate(self.relation, reverse)


@relation(u"rdf:type")   # FIXME: sparql specific
class FixedType(Expression):
    """
    Expression for a fixed type.
    This captures the idea of something having an specific type.
    """

    fixedtype = None

    def __init__(self, dataset=None):
        super(FixedType, self).__init__()
        if self.fixedtype is None:
            raise ValueError("You *must* define the `fixedtype` "
                             "class attribute to use this class.")
        if dataset is not None:
            self.dataset = dataset

        self.add_data(self.relation, self.fixedtype)


class FixedDataRelation(Expression):
    """
    Expression for a fixed relation. This is
    "A is related to Data" through the relation defined in `relation`.
    """

    relation = None
    language = None

    def __init__(self, data):
        super(FixedDataRelation, self).__init__()
        if self.relation is None:
            raise ValueError("You *must* define the `relation` "
                             "class attribute to use this class.")
        #self.relation = Expression.relation
        if self.language is not None:
            self.language = encoding_flexible_conversion(self.language)
            data = u"\"{0}\"@{1}".format(data, self.language)
        self.add_data(self.relation, data)


@relation(u"quepy:Keyword")
class HasKeyword(FixedDataRelation):
    """
    Abstraction of an information retrieval key, something standarized used
    to look up things in the database.
    """
    def __init__(self, data):
        data = self.sanitize(data)
        #super(self.__class__, self).__init__(data)
        super(HasKeyword, self).__init__(data)
        #FixedDataRelation.__init__(self, data)

    @staticmethod
    def sanitize(text):
        # User can redefine this method if needed
        return text


@relation("rdf:type")
class HasType(FixedRelation):
    pass

#@relation(u"quepy:IsRelatedTo")
class IsRelatedTo(FixedRelation):
    pass
# Looks weird, yes, here I am using `IsRelatedTo` as a unique identifier.
IsRelatedTo.relation = IsRelatedTo


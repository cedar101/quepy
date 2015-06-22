# -*- coding: utf-8 -*-

"""
Sparql generation code.
"""

from collections import namedtuple
from itertools import groupby

from quepy import settings
from quepy.dsl import IsRelatedTo
from quepy.expression import isnode
from quepy.encodingpolicy import assert_valid_encoding

_indent = u"  "


def escape(string):
    string = unicode(string)
    string = string.replace("\n", "")
    string = string.replace("\r", "")
    string = string.replace("\t", "")
    string = string.replace("\x0b", "")
    if not string or any(x for x in string if 0 < ord(x) < 31) or \
            string.startswith(":") or string.endswith(":"):
        message = "Unable to generate sparql: invalid nodes or relation"
        raise ValueError(message)
    return string


def adapt(x):
    if isnode(x):
        x = u"?x{}".format(x)
        return x
    if isinstance(x, basestring):
        assert_valid_encoding(x)
        if x.startswith(u"\"") or ":" in x:
            return x
        return u'"{}"'.format(x)
    return unicode(x)


def expression_to_tuples(e):
    y = 0
    for node in e.iter_nodes():
        for relation, dest in e.iter_edges(node):
            if relation is IsRelatedTo:
                relation = e.Predicate(u"?y{}".format(y),
                                       e.dataset, e.constraint)
                y += 1
            yield (adapt(node), relation, adapt(dest))


def expression_to_sparql(e, full=False):
    template = u"{preamble}\n" +\
               u"SELECT DISTINCT {select} WHERE {{\n" +\
               u"{where}\n" +\
               u"}}\n"
    head = adapt(e.get_head())
    if full:
        select = u"*"
    else:
        select = head

    indentation = 1
    indent = _indent * indentation
    xs = []

    for dataset, triples in groupby(expression_to_tuples(e),
                                    key=lambda t: t[1].dataset):
        if dataset:
            xs.append(dataset + " {")
        xs.append(u"\n{}".format(indent).join(triple(*t,
                                                     indentation=(indentation if dataset else 0))
                                                for t in triples))
        if dataset:
            xs.append(u"}")


    sparql = template.format(preamble=settings.SPARQL_PREAMBLE,
                             select=select,
                             where=u"\n".join(indent+line for line in xs))
    return select, sparql


def triple(a, p, b, indentation=0):
    indent = _indent * indentation
    a = escape(a)
    b = escape(b)

    template = indent + u"{0} {1} {2}."
    result = template.format(a, p.iri, b)

    if p.constraint:
        result += u'\n' + indent + _indent + p.constraint.format(a)

    return result


def sparql_string(s, indentation=0):
    return _indent * indentation + s

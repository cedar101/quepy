# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Code generation from an expression to a database language.

The currently supported languages are:
    * MQL
    * Sparql
    * Dot: generation of graph images mainly for debugging.
"""

from quepy.mql_generation import generate_mql
from quepy.dot_generation import expression_to_dot
from quepy.sparql_generation import expression_to_sparql

def get_code(expression, language):
    """
    Given an expression and a supported language, it
    returns the query for that expression on that language.
    """
    def get_node_data(expression):
        for node in expression.nodes:
            for relation, value in node:
                if isinstance(value, basestring):
                    return value, relation.iri

    if language == "sparql":
        return expression_to_sparql(expression)
    elif language == "dot":
        return expression_to_dot(expression)
    elif language == "mql":
        return generate_mql(expression)
    elif language == "dummy":
        return get_node_data(expression)
    else:
        message = u"Language '{}' is not supported"
        raise ValueError(message.format(language))

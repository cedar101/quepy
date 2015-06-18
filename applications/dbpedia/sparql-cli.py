#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import json
import re
import itertools

from prompt_toolkit.contrib.shortcuts import get_input
from prompt_toolkit.history import FileHistory
from prompt_toolkit.contrib.completers import WordCompleter
from pygments import highlight
from pygments.lexers.data import JsonLexer
from pygments.lexers.rdf import SparqlLexer
from pygments.token import Token
from pygments.style import Style
from pygments.styles.native import NativeStyle
from pygments.formatters import Terminal256Formatter
from SPARQLWrapper import SPARQLWrapper, JSON

PREFIXES = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX quepy: <http://www.machinalis.com/quepy#>
PREFIX dbpedia: <http://dbpedia.org/ontology/>
PREFIX dbpedia-ko: <http://ko.dbpedia.org/resource/>
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
PREFIX dbpprop: <http://dbpedia.org/property/>
PREFIX prop-ko: <http://ko.dbpedia.org/property/>
PREFIX grs: <http://www.georss.org/georss/>
"""

class DocumentStyle(Style):
    styles = {
        Token.Menu.Completions.Completion.Current: 'bg:#00aaaa #000000',
        Token.Menu.Completions.Completion: 'bg:#008888 #ffffff',
        Token.Menu.Completions.ProgressButton: 'bg:#003333',
        Token.Menu.Completions.ProgressBar: 'bg:#00aaaa',
    }
    styles.update(NativeStyle.styles)


# def get_bottom_toolbar_tokens(cli):
#     return [(Token.Toolbar, ' This is a toolbar. ')]

_name_re = re.compile(r"[a-zA-Z_][a-zA-Z0-9_ ]*$")

def is_identifiers(s):
    return bool(_name_re.match(s))

def main():
    sparql = SPARQLWrapper("http://dbpedia.org/sparql") #"http://localhost:3030/dbpedia/sparql")

    history = FileHistory('.history.sparql')

    sparql_completer = WordCompleter(
                        (token.replace('\\s+', ' ').upper()
                            for token in itertools.chain.from_iterable(
                                rule[0][1:].partition(')')[0].split('|')
                                    for rule in SparqlLexer.tokens['root']
                                        if rule[0].startswith('('))
                                if is_identifiers(token)), ignore_case=False)

    print('Press [Meta+Enter] or [Esc] followed by [Enter] to accept query.\n')

    for query in iter(lambda: get_input('Input SPARQL query:\n',
                                        multiline=True,
                                        history_filename='.history.sparql',
                                        lexer=SparqlLexer,
                                        completer=sparql_completer,
                                        #get_bottom_toolbar_tokens=get_bottom_toolbar_tokens,
                                        style=DocumentStyle).strip(),
                      ''):

        sparql.setQuery(PREFIXES + query)
        sparql.setReturnFormat(JSON)
        print "\nPlease wait..."
        results = sparql.query().convert()

        print "\nResult:"
        for result in results["results"]["bindings"]:
            print highlight(json.dumps(result, indent=4, ensure_ascii=False),
                            JsonLexer(), Terminal256Formatter())

    print 'GoodBye!'

if __name__ == '__main__':
    main()

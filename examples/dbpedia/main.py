#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Main script for DBpedia quepy.
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import random
import datetime
import logging.config
import os
from os.path import abspath, dirname, join
from types import FunctionType

import yaml
from SPARQLWrapper import SPARQLWrapper, JSON

sys.path.insert(0, join(abspath(dirname('__file__')), os.pardir, os.pardir))
import quepy

dbpedia = quepy.install("dbpedia")

#sparql = SPARQLWrapper("http://54.64.13.23:3030/dbpedia/sparql")
#sparql = SPARQLWrapper("http://175.123.88.38:3030/dbpedia/sparql")
sparql = SPARQLWrapper("http://127.0.0.1:3030/dbpedia-ko/query")

def print_define(results, target, metadata=None):
    for result in results["results"]["bindings"]:
        if result[target]["xml:lang"] == "en":
            print result[target]["value"]
            print

def print_enum(results, target, metadata=None):
    used_labels = []

    for result in results["results"]["bindings"]:
        if result[target]["type"] == u"literal":
            if result[target]["xml:lang"] == "en":
                label = result[target]["value"]
                if label not in used_labels:
                    used_labels.append(label)
                    print label

def print_literal(results, target, metadata=None):
    for result in results["results"]["bindings"]:
        literal = result[target]["value"]
        if metadata is None:
            print literal
        else:
            if isinstance(metadata, basestring):
                print metadata.format(literal)
            elif isinstance(metadata, FunctionType):
                print metadata(literal)

def print_location(results, target, metadata=None):
    zoom = 12
    for result in results["results"]["bindings"]:
        latitude, longitude = result[target]["value"].split()
        url = join("https://www.google.co.uk/maps/place",
                   "{latitude}+{longitude}",
                   "@{latitude},{longitude},{zoom}z").format(**locals())
        print 'open ' + url
        os.system('open ' + url)

def print_time(results, target, metadata=None):
    gmt = time.mktime(time.gmtime())
    gmt = datetime.datetime.fromtimestamp(gmt)

    for result in results["results"]["bindings"]:
        offset = result[target]["value"].replace(u"−", u"-")

        if ("to" in offset) or ("and" in offset):
            if "to" in offset:
                connector = "and"
                from_offset, to_offset = offset.split("to")
            else:
                connector = "or"
                from_offset, to_offset = offset.split("and")

            from_offset, to_offset = int(from_offset), int(to_offset)

            if from_offset > to_offset:
                from_offset, to_offset = to_offset, from_offset

            from_delta = datetime.timedelta(hours=from_offset)
            to_delta = datetime.timedelta(hours=to_offset)

            from_time = gmt + from_delta
            to_time = gmt + to_delta

            location_string = random.choice(["where you are",
                                             "your location"])

            print "Between %s %s %s, depending on %s" % \
                  (from_time.strftime("%H:%M"),
                   connector,
                   to_time.strftime("%H:%M on %A"),
                   location_string)

        else:
            offset = int(offset)

            delta = datetime.timedelta(hours=offset)
            the_time = gmt + delta

            print the_time.strftime("%H:%M on %A")


def print_age(results, target, metadata=None):
    assert len(results["results"]["bindings"]) == 1

    birth_date = results["results"]["bindings"][0][target]["value"]
    year, month, days = birth_date.split("-")

    birth_date = datetime.date(int(year), int(month), int(days.partition('+')[0]))

    now = datetime.datetime.utcnow()
    now = now.date()

    age = now - birth_date
    print "만 {}세".format(age.days / 365)

print_handlers = {
    "define": print_define,
    "enum": print_enum,
    "time": print_time,
    "literal": print_literal,
    "age": print_age,
    "location": print_location
}

def wikipedia2dbpedia(wikipedia_url):
    """
    Given a wikipedia URL returns the dbpedia resource
    of that page.
    """

    query = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT * WHERE {
        ?url foaf:isPrimaryTopicOf <%s>.
    }
    """ % wikipedia_url

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    if not results["results"]["bindings"]:
        print "Snorql URL not found"
        sys.exit(1)
    else:
        return results["results"]["bindings"][0]["url"]["value"]


if __name__ == "__main__":
    default_questions = [
        "아프리카TV가 뭐야?",
        "원빈이 누구야?",
        "분당구가 어디야?",
        "뉴욕은 몇 시지?",
        "원빈은 몇 살이지?",
        "원빈의 나이는?",
        "원빈의 출신지는 어디야?",
        "아르헨티나의 대통령은 누구지?",
        "볼리비아의 수도는 어디지?",
        "아르헨티나의 공용어는 뭐지?",
        "아르헨티나는 어떤 언어를 쓰지?",
        "인도의 인구수는?"
        # "List Microsoft software",
        # "Name Fiat cars",
        # "time in argentina",
        # "what time is it in Chile?",
        # "List movies directed by Martin Scorsese",
        # "How long is Pulp Fiction",
        # "which movies did Mel Gibson starred?",
        # "When was Gladiator released?",
        # "who directed Pocahontas?",
        # "actors of Fight Club",
    ]

    with open('logging.conf.yaml') as logfile:
        logging.config.dictConfig(yaml.load(logfile))

    if "-d" in sys.argv:
        quepy.set_loglevel("DEBUG")
        sys.argv.remove("-d")

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])

        if question.count("wikipedia.org"):
            print wikipedia2dbpedia(sys.argv[1])
            sys.exit(0)
        else:
            questions = [question]
    else:
        questions = default_questions

    for question in questions:
        print question
        print "-" * len(question)

        target, query, metadata = dbpedia.get_query(question)

        if isinstance(metadata, tuple):
            query_type = metadata[0]
            metadata = metadata[1]
        else:
            query_type = metadata
            metadata = None

        #print '\n', query_type, metadata

        if query is None:
            print "Query not generated :(\n"
            continue

        #print query

        if target.startswith("?"):
            target = target[1:]
        if query:
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            print "Please wait...\n"
            results = sparql.query().convert()
            #import pdb; pdb.set_trace()
            if not results["results"]["bindings"]:
                print "No answer found :("
                continue

        print "Result:"
        print_handlers[query_type](results, target, metadata)
        print

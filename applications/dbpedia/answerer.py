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
import os.path
import ast
from types import FunctionType

import yaml
from SPARQLWrapper import SPARQLWrapper, JSON

sys.path.insert(0, os.path.join(os.getcwd(), os.pardir, os.pardir))
import quepy

dbpedia = quepy.install("dbpedia")

sparql = SPARQLWrapper("http://aflxscketcdev1:8890/sparql")

class ParseError(ValueError):
    def __init__(self, question):
        ValueError.__init__(self)
        self.question = question

    def __str__(self):
        return "Parse error -- Query not generated: " + self.question


def autocast(s):
    try:
        return ast.literal_eval(s)
    except ValueError:
        return s

def process_define(results, target, metadata=None):
    for result in results["results"]["bindings"]:
        if result[target]["xml:lang"] == "ko":
            yield result[target]["value"]

def process_enum(results, target, metadata=None):
    #used_labels = []

    for result in results["results"]["bindings"]:
        if result[target]["type"] == u"literal":
            if result[target]["xml:lang"] in ("en", "ko"):
                yield result[target]["value"]
                # label = result[target]["value"]
                # if label not in used_labels:
                #     used_labels.append(label)

    #return '\n'.join(used_labels)

def process_literal(results, target, metadata=None):
    for result in results["results"]["bindings"]:
        literal = result[target]["value"]

        if metadata:
            yield metadata.format(autocast(literal))
        else:
            yield literal

def process_location(results, target, metadata=None):
    zoom = 12
    for result in results["results"]["bindings"]:
        latitude, longitude = result[target]["value"].split()
        url = os.path.join("https://www.google.co.kr/maps/place",
                           "{latitude}+{longitude}",
                           "@{latitude},{longitude},{zoom}z").format(**locals())
        yield url
        #os.system('open ' + url)

def process_time(results, target, metadata=None):
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

            yield "Between %s %s %s, depending on %s" % \
                  (from_time.strftime("%H:%M"),
                   connector,
                   to_time.strftime("%H:%M on %A"),
                   location_string)

        else:
            offset = int(offset)

            delta = datetime.timedelta(hours=offset)
            the_time = gmt + delta

            yield the_time.strftime("%H:%M") # on %A")

def process_age(results, target, metadata=None):
    assert len(results["results"]["bindings"]) == 1

    birth_date = results["results"]["bindings"][0][target]["value"]
    year, month, days = birth_date.split("-")

    birth_date = datetime.date(int(year), int(month), int(days.partition('+')[0]))

    now = datetime.datetime.utcnow()
    now = now.date()

    age = now - birth_date
    yield "만 {}세".format(age.days / 365)

process_handlers = {
    "define": process_define,
    "enum": process_enum,
    "time": process_time,
    "literal": process_literal,
    "age": process_age,
    "location": process_location
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

def get_query(question):
    # print question
    # print "-" * len(question)

    target, query, metadata, rule_used = dbpedia.get_query(question)

    if query is None:
        raise ParseError(question)
        #return "Query not generated", None, None, None, None

    if isinstance(metadata, tuple):
        query_type = metadata[0]
        metadata = metadata[1]
    else:
        query_type = metadata
        metadata = None

    if target.startswith("?"):
        target = target[1:]

    return query, target, query_type, metadata, rule_used


def query_sparql(query, target, query_type, metadata):
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    print "Please wait...\n"
    results = sparql.query().convert()
    #import pdb; pdb.set_trace()
    # if not results["results"]["bindings"]:
    #     return "No answer found"

    return process_handlers[query_type](results, target, metadata) #, query

def main():
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
        for result in query_sparql(*get_query(question)[0:4]):
            print result

if __name__ == "__main__":
    main()

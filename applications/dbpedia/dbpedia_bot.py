import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import answerer

outputs = []
crontabs = []

def process_message(data):
    channel = data["channel"]
    question = data["text"]

    output = '\n'.join(answerer.query_sparql(*answerer.get_query(question)[0:4]))

    outputs.append([channel, output])

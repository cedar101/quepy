#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from functools import wraps
from copy import deepcopy

from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions

import requests
import ujson

from redis import Redis
from rq import Queue, Connection
from rq.decorators import job
import rq_dashboard

import answerer

app = FlaskAPI(__name__)
# app.config.from_object(rq_dashboard.default_settings)
# app.register_blueprint(rq_dashboard.blueprint)

result_struct = {
    "type": "SPARQL",
    "data": {
        "intention": None,
        "param": {
            "match": None,
            "result_type": None,
            "query_string": None,
            "answer_string": None,
            "metadata": None
        }
    }
}

dummy_common = {
  "common" :
  {
    "logname" : "CHAT-MESSAGE",
    "tm" : "123456789",
    "userid" : "ssanaii",
    "usernick" : "사나이",
    "bjid" : "afreecaai04",
    "bno" : "xxxxxxxx",
    "score" : "0.0123"
  }
}

middleware_url = 'http://tsuzie.afreeca.com/udp-middle.php?eQueueType=QUEUE&name='

def json2data(func):
    @wraps(func)
    def wrapper(url, data=None, json=None, **kwargs):
        if data is None:
            kwargs.setdefault('headers', {})['Content-Type'] = 'application/json'
            try:
                data = ujson.dumps(json, ensure_ascii=False)
            except (TypeError, OverflowError):
                data = None
            json=None
        return func(url, data, json, **kwargs)
    return wrapper

requests.post = json2data(requests.post)

def send_middleware(queue_name, resp, url=middleware_url):
    if 'common' not in resp:
        resp['common'] = dummy_common

    r = requests.post(url + queue_name, json=resp)
                      #data=json.dumps(resp, ensure_ascii=False))
    resp = r.text
    if int(resp) < 1:
        raise requests.exceptions.RequestException
    return resp


# @app.route('/question', methods=['GET', 'POST'])
# def process_question():
#     req_body = request.data

#     chat_text = req_body['extension']['chat_text']

#     query, target, query_type, metadata, rule_used = answerer.get_query(chat_text)

#     result = deepcopy(result_struct)

#     result_data = result["data"]
#     result_data["intention"] = rule_used
#     param = result_data["param"]
#     param["match"] = target
#     param["result_type"] = query_type
#     param["query_string"] = query
#     param["metadata"] = metadata

#     resp = dict(req_body, result=result)

#     resp_middle = send_middleware('AF.AI_USER.CHAT-MESSAGE.NLP.RET', resp)

#     return resp

# conn = Redis('localhost', 6379)
# q = Queue('low', connection=conn)

# #@job('low', connection=conn, timeout=30)
# def sparql_job(request, answerer, middleware_url):
#     req_body = request.data

#     result = req_body['result']
#     result_data = result['data']
#     param = result_data['param']
#     query = param['query_string']
#     target = param['match']
#     query_type = param['result_type']
#     metadata = param.get('metadata')

#     answer_string = answerer.query_sparql(query, target, query_type, metadata)

#     param['answer_string'] = answer_string

#     resp = dict(req_body, result=result)
#     resp_middle = send_middleware('AF.AI_USER.CHAT-MESSAGE.NLP.SPARQL.RET', resp, middleware_url)

#     return resp

# @app.route('/sparql', methods=['GET', 'POST'])
# def process_sparql():
#     #job = q.enqueue_call(func=sparql_job, args=(request, answerer, middleware_url), result_ttl=5000)
#     #sparql_job.delay(request, answerer)

#     req_body = request.data

#     result = req_body['result']
#     result_data = result['data']
#     param = result_data['param']
#     query = param['query_string']
#     target = param['match']
#     query_type = param['result_type']
#     metadata = param.get('metadata')

#     answer_string = answerer.query_sparql(query, target, query_type, metadata)

#     param['answer_string'] = answer_string

#     #result_data.update()

#     resp = dict(req_body, result=result)

#     resp_middle = send_middleware('AF.AI_USER.CHAT-MESSAGE.NLP.SPARQL.RET', resp)

#     return resp

#     #return job.get_id()

# #@job('low', connection=conn, timeout=30)
# def answer_job(request, answerer, middleware_url, result_struct):
#     req_body = request.data
#     chat_text = req_body['extension']['chat_text']

#     query, target, query_type, metadata, rule_used = answerer.get_query(chat_text)

#     result = deepcopy(result_struct)

#     result_data = result["data"]
#     result_data["intention"] = rule_used
#     param = result_data["param"]
#     param["match"] = target
#     param["result_type"] = query_type
#     param["query_string"] = query
#     param["metadata"] = metadata

#     answer_string = answerer.query_sparql(query, target, query_type, metadata)

#     param['answer_string'] = answer_string

#     resp = dict(req_body, result=result)

#     resp_middle = send_middleware('AF.AI_USER.CHAT-MESSAGE.NLP.SPARQL.RET', resp)

#     return resp


@app.route('/answer', methods=['GET', 'POST'])
def process_answer():
    #answer_job.delay(request, answerer)
    # job = q.enqueue_call(func=answer_job,
    #                      args=(request, answerer, middleware_url, result_struct),
    #                      result_ttl=5000)

    req_body = request.data
    chat_text = req_body['extension']['chat_text']

    try:
        query, target, query_type, metadata, rule_used = answerer.get_query(chat_text)
    except answerer.QueryNotGenerated, e:
        query = str(e)
        target, query_type, metadata = None, None, None
        rule_used = e.__class__.__name__

    result = deepcopy(result_struct)

    result_data = result["data"]
    result_data["intention"] = rule_used
    param = result_data["param"]
    param["match"] = target
    param["result_type"] = query_type
    param["query_string"] = query
    param["metadata"] = metadata

    answer_string = ('\n'.join(answerer.query_sparql(query, target, query_type, metadata))
                     if target else query)

    param['answer_string'] = answer_string

    resp = dict(req_body, result=result)

    resp_middle = send_middleware('AF.AI_USER.CHAT-MESSAGE.NLP.SPARQL.RET', resp)

    return resp

    #return job.get_id()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=13085)

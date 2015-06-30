# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from functools import wraps
from copy import deepcopy

from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions
from flask.ext.api.response import APIResponse
from flask.ext.api.exceptions import ParseError
from flask.ext.rq import RQ, job
from flask.ext.log import Logging

import requests
import ujson

from config import config
import answerer

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

class MyFlaskAPI(FlaskAPI):
    def handle_api_exception(self, exc):
        #resp_middle = send_middleware(exc.detail)
        send_middleware(exc.detail)
        return APIResponse(exc.detail, status=exc.status_code)

rq = RQ()
log = Logging()

def create_app(config_name):
    app = MyFlaskAPI(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    rq.init_app(app)
    log.init_app(app)
    return app

app = create_app(os.getenv('QUEPY_CONFIG') or 'default')

#@job('default')
def send_middleware(resp,
                    queue_name=app.config['MIDDLEWARE_QUEUE_NAME'],
                    url=app.config['MIDDLEWARE_URL']):
    resp.setdefault('common', app.config['DUMMY_COMMON'])

    r = requests.post(url + queue_name, json=resp)
                      #data=json.dumps(resp, ensure_ascii=False))
    resp = r.text
    if int(resp) < 1:
        raise requests.exceptions.RequestException

    return resp

@job('default')
def process_query_sparql(req_body, result, query, target, query_type, metadata):
    answers = list(answerer.query_sparql(query, target, query_type, metadata))

    result['data']['param']['answers'] = answers

    resp = dict(req_body, result=result)

    send_middleware(resp)
    send_middleware(resp, 'test.AF.AI_USER.CHAT-MESSAGE.NLP.SPARQL.RET')
    app.logger.debug(resp)

    return answers

@app.route('/answer', methods=['GET', 'POST'])
def answer():
    #answer_job.delay(request, answerer)
    # job = q.enqueue_call(func=answer_job,
    #                      args=(request, answerer, middleware_url, result_struct),
    #                      result_ttl=5000)

    req_body = request.data
    chat_text = req_body['extension']['chat_text']

    result = deepcopy(app.config['RESULT_STRUCT'])
    result_data = result["data"]

    try:
        query, target, query_type, metadata, rule_used = answerer.get_query(chat_text)
    except answerer.ParseError, e:
        result_data["status"] = {"code": str(ParseError.status_code),
                                 "error_type": e.__class__.__name__,
                                 "error_detail": str(e)}
        resp = dict(req_body, result=result)
        raise ParseError(resp)

    result_data["intention"] = rule_used
    param = result_data["param"]
    param["match"] = target
    param["result_type"] = query_type
    param["query_string"] = query
    param["metadata"] = metadata

    if app.config['RQ_DEFAULT_HOST'] is None:
        answers = list(answerer.query_sparql(query, target, query_type, metadata))

        param['answers'] = answers

        resp = dict(req_body, result=result)

        resp_middle = send_middleware(resp)

        return resp
    else:
        return process_query_sparql.delay(req_body, result,
                                          query, target, query_type, metadata).key


    #return job.get_id()



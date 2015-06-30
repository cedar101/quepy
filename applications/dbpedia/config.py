# -*- coding: utf-8 -*-
from flask.ext.api import status

class Config:
    MIDDLEWARE_URL = 'http://tsuzie.afreeca.com/udp-middle.php?eQueueType=QUEUE&name='
    MIDDLEWARE_QUEUE_NAME = 'AF.AI_USER.CHAT-MESSAGE.NLP.SPARQL.RET'
    DUMMY_COMMON = {
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
    RESULT_STRUCT = {
        "type": "SPARQL",
        "data": {
            "intention": None,
            "param": {
                "match": None,
                "result_type": None,
                "query_string": None,
                "answers": None,
                "metadata": None
            },
            "status": {
                "code": str(status.HTTP_200_OK),
                "error_type": None,
                "error_detail": None
            }
        },
    }
    FLASK_LOG_LEVEL = 'DEBUG'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    RQ_DEFAULT_HOST = 'localhost'
    RQ_DEFAULT_PORT = 6379

class StagingConfig(Config):
    RQ_DEFAULT_HOST = 'localhost'
    RQ_DEFAULT_PORT = 63790

class NoQueueConfig(Config):
    RQ_DEFAULT_HOST = None
    RQ_DEFAULT_PORT = None

config = {
    'development' : DevelopmentConfig,
    'staging' : StagingConfig,
    'noqueue' : NoQueueConfig,
    'default' : DevelopmentConfig
}

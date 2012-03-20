#! coding: utf-8
# pylint: disable-msg=W0311

""" Lấy log đẩy vào ElasticSearch """

from cPickle import loads
from hotqueue import HotQueue
from pyelasticsearch import ElasticSearch
import settings

host, port, db = settings.QUEUE.split(':')
QUEUE = HotQueue("queue", host=host, port=int(port), db=int(db))
INDEX = ElasticSearch('http://' + settings.ES_SERVER)

@QUEUE.worker
def build_index(info):
  info = loads(info)
  INDEX.index(info, "log", "fields")
  INDEX.refresh(["log"])
  print info
  
if __name__ == '__main__':
  build_index()
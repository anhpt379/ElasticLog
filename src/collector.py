#! coding: utf-8
# pylint: disable-msg=W0311

""" Lấy log đẩy vào ElasticSearch """

from cPickle import loads
from hotqueue import HotQueue
#from pyelasticsearch import ElasticSearch
import pyes
import settings

host, port, db = settings.QUEUE.split(':')
QUEUE = HotQueue("queue", host=host, port=int(port), db=int(db))
#INDEX = ElasticSearch('http://' + settings.ES_SERVER)
INDEX = pyes.ES(settings.ES_SERVERS)

@QUEUE.worker
def build_index(info):
  try:
    info = loads(info)
#    INDEX.index(info, "log", "fields")
#    INDEX.refresh(["log"])
    INDEX.index(info, 'log', 'fields', bulk=True)
  except Exception:
    print info
  
if __name__ == '__main__':
  build_index()
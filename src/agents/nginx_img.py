#! coding: utf-8
# pylint: disable-msg=W0311
"""
$ (while [ 1 ]; do sleep 1; done) | python test.py

http://stackoverflow.com/questions/5374255/how-to-write-data-to-existing-processs-stdin-from-external-process
"""

import settings
import re
import sys
from cPickle import dumps
from hotqueue import HotQueue
from datetime import datetime

host, port, db = settings.QUEUE.split(':')
QUEUE = HotQueue("queue", host=host, port=int(port), db=int(db))



def parse(message):
  parts = message.split()
  quotes = re.compile('"(.*?)"').findall(message)
  request = quotes[0]
  referer = quotes[1]
  agent = quotes[2]
  info = {'request_time': float(parts[-1]),
          'user_agent': agent,
          'referer': referer,
          'request': request,
          'remote_addr': parts[0],
          'status': int(re.compile('" (\d+) ').findall(message)[0]),
          'bytes_sent': int(re.compile(' (\d+) "').findall(message)[0]),
          'time': parts[1].strip('[]').split('+')[0]}
  return info


if __name__ == '__main__':
  NAME = 'nginx_6.37_8080_access_log'
  
  print("Try commands below")
  print "$ echo 'foobar' > /proc/`ps -eo pid,args | grep %s | grep -v grep | cut -d' ' -f 1`/fd/0" % __file__.rsplit('/', 1)[-1]
  COUNT = 0
  while True:
    line = sys.stdin.readline()
    COUNT += 1
    
    if COUNT % 10000 == 0:
      print COUNT
    
    try:
      params = parse(line)
    except Exception:
      print line
      continue
    
    if not params.has_key('time'):
      params['time'] = datetime.now().isoformat()
    if not params.has_key('level'):
      params['level'] = settings.LOG_LEVEL
    params['name'] = NAME
    QUEUE.put(dumps(params))
    
    
    
    
    
#! coding: utf-8
# pylint: disable-msg=W0311


import settings
import re
import time
from cPickle import dumps
from hotqueue import HotQueue
from datetime import datetime

host, port, db = settings.QUEUE.split(':')
QUEUE = HotQueue("queue", host=host, port=int(port), db=int(db))

def tail_f(path_to_file, interval=0.1):
  fp = open(path_to_file, 'r')
  fp.seek(0, 2) # Go to the end of the file
  while True:
    where = fp.tell()
    line = fp.readline()
    if not line:
      time.sleep(interval)
      fp.seek(where)
    else:
      yield line


def parse(message):
  if ' [UPLOAD] ' in message:
    t, action, status, filename, secret_key, overwrite, source, unzip  = re.compile(r'\((.*?)\) \[(.*?)\] (\d+) - (.*?) - (.*?) - (.*?) - (.*?) - (.*$)').findall(message)[0]
    info = {'time': datetime.strptime(t, '%Y-%m-%d %H:%M:%S,%f').isoformat(),
            'action': action,
            'status': int(status),
            'filename': filename,
            'secret_key': secret_key,
            'overwrite': 1 if overwrite != 'None' else None,
            'source': source if source != 'None' else None,
            'unzip': unzip if unzip != 'None' else None}
  elif ' [DELETE] ' in message:
    t, action, status, filename, secret_key  = re.compile(r'\((.*?)\) \[(.*?)\] (\d+) - (.*?) - (.*$)').findall(message)[0]
    info = {'time': datetime.strptime(t, '%Y-%m-%d %H:%M:%S,%f').isoformat(),
            'action': action,
            'status': int(status),
            'filename': filename,
            'secret_key': secret_key}
  elif ' [RENAME] ' in message:
    t, action, status, from_name, to_name, secret_key  = re.compile(r'\((.*?)\) \[(.*?)\] (\d+) - (.*?) - (.*?) - (.*$)').findall(message)[0]
    info = {'time': datetime.strptime(t, '%Y-%m-%d %H:%M:%S,%f').isoformat(),
            'action': action,
            'status': int(status),
            'from_name': from_name,
            'to_name': to_name,
            'secret_key': secret_key}
    
  return info

def watch(path_to_log_file):
  for line in tail_f(path_to_log_file):
    try:
      params = parse(line)
    except Exception:
      print line
    if not params.has_key('time'):
      params['time'] = datetime.now().isoformat()
    if not params.has_key('level'):
      params['level'] = settings.LOG_LEVEL
    params['name'] = NAME
    QUEUE.put(dumps(params))
  
      
if __name__ == '__main__':
  NAME = settings.NAME
  watch('/var/log/access.log')
  
    
    
    
    
    
    
    
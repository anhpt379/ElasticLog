#! coding: utf-8
# pylint: disable-msg=W0311

# Tham khảo http://code.activestate.com/recipes/577968-log-watcher-tail-f-log/
# cho thao tác tail -f *.log
#
# Đẩy log vào queue
# inputs: 
#  /var/log/messages
#  /var/log/*.log
#  apache logs
#  database logs


import settings
import re
import time
from cPickle import dumps
from hotqueue import HotQueue
from datetime import datetime, tzinfo, timedelta

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
      
      

class Timezone(tzinfo):
  def __init__(self, name="+0000"):
    self.name = name
    seconds = int(name[:-2])*3600+int(name[-2:])*60
    self.offset = timedelta(seconds=seconds)

  def utcoffset(self, dt):
    return self.offset

  def dst(self, dt):
    return datetime.timedelta(0)

  def tzname(self, dt):
    return self.name

def parse(message):
  parts = [
    r'(?P<host>\S+)',                   # host %h
    r'\S+',                             # indent %l (unused)
    r'(?P<user>\S+)',                   # user %u
    r'\[(?P<time>.+)\]',                # time %t
    r'"(?P<request>.+)"',               # request "%r"
    r'(?P<status>[0-9]+)',              # status %>s
    r'(?P<size>\S+)',                   # size %b (careful, can be '-')
    r'"(?P<referer>.*)"',               # referer "%{Referer}i"
    r'"(?P<agent>.*)"',                 # user agent "%{User-agent}i"
  ]
  pattern = re.compile(r'\s+'.join(parts)+r'\s*\Z')
  
  m = pattern.match(message)
  res = m.groupdict()
  if res["user"] == "-":
    res["user"] = None
  res["status"] = int(res["status"])
  if res["size"] == "-":
    res["size"] = 0
  else:
    res["size"] = int(res["size"])
  if res["referer"] == "-":
    res["referer"] = None
  
  tt = time.strptime(res["time"][:-6], "%d/%b/%Y:%H:%M:%S")
  tt = list(tt[:6]) + [0, Timezone(res["time"][-5:])]
  res["time"] = datetime(*tt).isoformat()
  return res

def run(path_to_log_file):
  for line in tail_f(path_to_log_file):
    params = parse(line)
    if not params.has_key('time'):
      params['time'] = datetime.now().isoformat()
    if not params.has_key('level'):
      params['level'] = 'info'
    params['name'] = NAME
    QUEUE.put(dumps(params))
    print line
  
      
if __name__ == '__main__':
  NAME = 'web_6.37_apache_accesslog'
  run('/usr/local/nginx/logs/access.log')
  
    
    
    
    
    
    
    
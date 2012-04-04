#!/usr/bin/python -u

import re, os, sys

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
  print """
  1. rm -f /var/log/access.log
  2. ln -s /proc/{0}/fd/0 /var/log/access.log
  """.format(os.getpid())
  COUNT = 0
  while True:
    line = sys.stdin.readline()
    COUNT += 1
    print COUNT
#    info = parse(line)
#    print info

#! coding: utf-8
# pylint: disable-msg=W0311

"""
- Hiển thị giao diện:
  + 1 ô nhập truy vấn
  + 1 vùng biểu đồ
  + 1 vùng các kết quả tìm thấy
- Nhận truy vấn
  + Tìm trong ElasticSearch
  + Tổng hợp kết quả, vẽ biểu đồ theo thời gian hoặc các tham số đã tách ở bước phân tích
"""
from flask import Flask, request, render_template, make_response, abort
from pyelasticsearch import ElasticSearch
from mimetypes import guess_type
from datetime import datetime, timedelta
from redis import Redis
import os
import settings


try:
  from collections import OrderedDict as odict
except ImportError:
  from ordereddict import OrderedDict as odict


host, port = settings.CACHE.split(':')
CACHE = Redis(host=host, port=int(port))
INDEX = ElasticSearch('http://' + settings.ES_SERVERS[0])

app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def main():
  if request.method == 'GET':
    query = '*'
    graph_by = 'minute'
    start = datetime.strftime(datetime.now() - timedelta(hours=1), '%Y-%m-%dT%H:%M:%S')
    end = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S')
  else:
    query = request.form.get('query', '*')  
    if '*' not in query:
      query = '*' + query + '*'
    graph_by = request.form.get('graph_by', 'second')
    start = request.form.get('start')
    end = request.form.get('end')
    
  key = graph_by
  query_dsl =  {}

  query_dsl['query'] = { 
          "filtered" : {
                   "query" : {
                      "query_string" :  {"query" : query} 
                   },
                   "filter" : {
                      "numeric_range" : {
                         "time" : {
                            "lt" : end,
                            "gte" : start
                         }
                      }
                   }
                }
        }
  
  if key in ['second', 'minute', 'hour', 'day', 'week', 'month', 'year']:
    query_dsl['facets'] =  {
            "counters": { 
              "date_histogram": {
                "field" : "time",  
                "interval" : key
                } 
              }
            }
  else:
    query_dsl["facets"] = {
          "counters" : {
              "terms" : {
                  "script_field" : "_source.%s" % key
              }
            }
          }
    
  resp = INDEX.search(query=None, body=query_dsl, indexes=['log'])
  
  results = resp.get('hits').get('hits')
  records = []
  for i in results:
    record = {}
    for k in i.get('_source').keys():
      if not k.startswith('_'): 
        record[k] = i['_source'][k]
      records.append(record)
  
  counters = odict()
  delta = timedelta(hours=7)  # utc offset
  if key in ['second', 'minute', 'hour', 'day', 'week', 'month', 'year']:
    entries = resp.get('facets').get('counters').get('entries')
    for i in entries:
      counters[datetime.fromtimestamp(i['time'] / 1000) - delta] = i['count']

  else:
    for i in resp.get('facets').get('counters').get('terms'):
      counters[i['term']] = i['count']
    
  return render_template('home.html', 
                         start=start, end=end,
                         query=query, graph_by=graph_by,
                         records=records, counters=counters)
    

@app.route('/public/<filename>')
def public_files(filename):
  path = 'public/' + filename
  if not os.path.exists(path):
    abort(404, 'File not found')
  filedata = open(path).read()               
    
  response = make_response(filedata)
  response.headers['Content-Length'] = len(filedata)
  response.headers['Content-Type'] = guess_type(filename)[0]
  response.headers['Cache-Control'] = 'public'
  response.headers['Expires'] = '31 December 2037 23:59:59 GMT'
  return response
  
  
if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=False)
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
from collections import OrderedDict as odict
from pyelasticsearch import ElasticSearch
from mimetypes import guess_type
from datetime import datetime
from redis import Redis
import os
import settings

host, port = settings.CACHE.split(':')
CACHE = Redis(host=host, port=int(port))
INDEX = ElasticSearch('http://' + settings.ES_SERVER)

app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def main():
  if request.method == 'GET':
    query = '*'
    graph_by = 'hour'
  else:
    query = request.form.get('query', '*')  
    graph_by = request.form.get('graph_by', 'second')
    
  key = graph_by
  query_dsl =  {"query" : {"query_string": {"query" : query}}}

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
  if key in ['second', 'minute', 'hour', 'day', 'week', 'month', 'year']:
    entries = resp.get('facets').get('counters').get('entries')
    for i in entries:
      counters[datetime.fromtimestamp(i['time'] / 1000)] = i['count']

  else:
    for i in resp.get('facets').get('counters').get('terms'):
      counters[i['term']] = i['count']
    
  return render_template('home.html', 
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
  app.run(debug=True)
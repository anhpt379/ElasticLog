#! coding: utf-8
# pylint: disable-msg=W0311
from pyelasticsearch import ElasticSearch
from pprint import pprint
import settings

INDEX = ElasticSearch('http://192.168.6.126:9200/')


query =  {
          "query" : { 
            "filtered" : {
                     "query" : {
                        "query_string" :  {"query" : "*"} 
                     },
                     "filter" : {
                        "numeric_range" : {
                           "time" : {
                              "lt" : "2012-01-02T10:00:00+0700",
                              "gte" : "2012-01-02T8:00:00+0700"
                           }
                        }
                     }
                  }
          },
          'facets': {
            "counters": { 
              "date_histogram": {
                "field" : "time",  
                "interval" : 'hour'
                } 
              }
            }
          }


resp = INDEX.search(query=None, body=query, indexes=['log'])
pprint(resp)
pprint(resp['facets'])


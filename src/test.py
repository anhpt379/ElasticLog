#! coding: utf-8
# pylint: disable-msg=W0311
from pyelasticsearch import ElasticSearch
from pprint import pprint
import settings

INDEX = ElasticSearch('http://' + settings.ES_SERVER)

## Count
query =  {
          "query" : { "query_string" : {"query" : "1*"} },
          "facets" : {
                      "counters" : { "terms" : {"field" : "agent"} }
                      }
          }

query =  {
          "query" : { "query_string" : {"query" : "*"} },
          "facets" : {
            "counters" : {
                "terms" : {
                    "script_field" : "_source.agent"
                }
              }
            }
          }


resp = INDEX.search(query=None, body=query, indexes=['log'])
pprint(resp['facets'])


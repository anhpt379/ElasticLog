#! coding: utf-8
# pylint: disable-msg=W0311

import pyes
import time
import settings

INDEX = pyes.ES(settings.ES_SERVERS)

while True:
  INDEX.refresh()
  time.sleep(60)
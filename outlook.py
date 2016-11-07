#!/usr/bin/env python

"""download calendar entry"""

import os
import sys
import cgi
import datetime
import json
import urllib
import shuttle
import shcontants


form = cgi.FieldStorage()
if 'k' not in form or 'cal' not in form:
  sys.exit()
key = form.getvalue("k")
cal = form.getvalue("cal")

u, p = shuttle.extract_credentials(key)
shuttle.do_login_full(u, p)
r = shuttle.download_ics_full(cal)

print "Status: 200 Found"
print "Content-type: " + r.headers["content-type"]
print "Content-disposition: " + r.headers["content-disposition"]

print ""

print r.read()

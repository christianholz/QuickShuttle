#!/usr/bin/env python

"""verifies existence of cookie and otherwise shows redirect"""

import os
import sys
import cgi
import shuttle
import Cookie


k = None
try:
  cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
  k = cookie["skey"].value
  u, p, routes = shuttle.extract_credentials(k)
except:
  print "Status: 302 Moved"
  print "Location: %s%s/cookiegen.py" % (os.environ["HTTP_ORIGIN"], os.path.dirname(os.environ["SCRIPT_NAME"]))
  print ""
  print "cookie missing... redirecting."
  sys.exit()

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
  u, p = shuttle.extract_credentials(k)
except:
  print "Status: 302 Moved"
  print "Location: cookiegen.py"
  print ""
  print "cookie missing... redirecting."
  sys.exit()

#!/usr/bin/env python

"""verifies existence of cookie and otherwise shows redirect"""

import os
import sys
import cgi
import shuttle
import Cookie


k = None
form = cgi.FieldStorage()
if 'skey' in form:
  u, p, routes = shuttle.extract_credentials(form.getvalue('skey'))
else:
  try:
    cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
    k = cookie["skey"].value
    u, p, routes = shuttle.extract_credentials(k)
  except:
    print "Status: 302 Moved"
    print "Location: %s/cookiegen.py" % (os.path.dirname(os.environ["SCRIPT_NAME"]))
    print ""
    print "cookie missing... redirecting."
    sys.exit()

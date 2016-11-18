#!/usr/bin/env python

"""one-time cookie generator to contain the credentials"""

import os
import sys
import cgi
import datetime
import Cookie
import shuttle


form = cgi.FieldStorage()

if 'user' in form and 'pass' in form:
  u = form.getvalue("user")
  p = form.getvalue("pass")
  k = shuttle.generate_key(u, p)

  dt = datetime.datetime.now()
  dt += datetime.timedelta(365)
  print "Status: 200 Success"
  
  cookie = Cookie.SimpleCookie()
  cookie["skey"] = k
  cookie["skey"]["domain"] = ".cholz.de"
  cookie["skey"]["path"] = "/shuttle"
  cookie["skey"]["expires"] = dt.strftime("%a, %d-%b-%Y %H:%M:%S PST")
  print cookie.output()
  # print "Set-Cookie: key=%s; expires={}; path=/shuttle/; domain=cholz.de; version=1" % (
  #   k, dt.strftime("%a, %d-%b-%Y %H:%M:%S PST"))
  #   # dt.strftime("%a, %d %b %Y %H:%M:%S +0000"))
  print "Content-type: text/html\r\n"

  print '''<pre>
  ready to bookmark:
  <a href="%s%s/bookings.py">bookings</a>
  <a href="%s%s/bookings.py">bookings</a>
</pre>''' % (os.environ["HTTP_ORIGIN"], os.path.dirname(os.environ["SCRIPT_NAME"]),
    os.environ["HTTP_ORIGIN"], os.path.dirname(os.environ["SCRIPT_NAME"]))
else:
  print "Content-type: text/html\r\n"
  print '''
<pre>
<form method="post">
  <input name="user" type="text" />
  <input name="pass" type="password" />
  <input type="submit" value="submit" />
</form>
</pre>
'''

#!/usr/bin/env python

"""one-time cookie generator to contain the credentials"""

import os
import sys
import cgi
import datetime
import Cookie
import shuttle
import json
import struct


form = cgi.FieldStorage()

if 'user' in form and 'pass' in form:
  u = form.getvalue("user")
  p = form.getvalue("pass")
  if 'r' in form:
    routes = form.getvalue('r')
    alldata = json.load(open("all.json"))
    if type(routes) == str:
      rid = [alldata["true"][routes + " AM"][2]]
    elif type(routes) == list:
      rid = [alldata["true"][r + " AM"][2] for r in routes]
  else:
    rid = []
  k = shuttle.generate_key(u, p, rid)

  dt = datetime.datetime.now()
  dt += datetime.timedelta(365)
  print "Status: 200 Success"
  
  cookie = Cookie.SimpleCookie()
  cookie["skey"] = k
  if SERVER_PORT == 8080:
    cookie["skey"]["domain"] = "localhost"
    cookie["skey"]["path"] = "/cgi-bin"
  else:
    cookie["skey"]["domain"] = '.' + os.environ['SERVER_NAME']
    cookie["skey"]["path"] = "/shuttle"
  cookie["skey"]["expires"] = dt.strftime("%a, %d-%b-%Y %H:%M:%S PST")
  
  if "HTTP_ORIGIN" in os.environ:
    origin = os.environ["HTTP_ORIGIN"]
  else:
    origin = ""
  
  print cookie.output()
  # print "Set-Cookie: key=%s; expires={}; path=/shuttle/; domain=cholz.de; version=1" % (
  #   k, dt.strftime("%a, %d-%b-%Y %H:%M:%S PST"))
  #   # dt.strftime("%a, %d %b %Y %H:%M:%S +0000"))
  print "Content-type: text/html\r\n"

  print '''<pre>
  ready to bookmark:
  <a href="%s%s/bookings.py">bookings</a>
</pre>''' % (origin, os.path.dirname(os.environ["SCRIPT_NAME"]))
else:
  alldata = json.load(open("all.json"))
  routes = [r[:-3] for r in alldata["true"].keys()]
  routes.sort()
  
  print "Content-type: text/html\r\n"
  print '''
<pre>
<form method="post">
user <input name="user" type="text" />
pass <input name="pass" type="password" />
  
<input type="submit" value="submit" />
  
optional:
'''
  for r in routes:
    print '<input type="checkbox" name="r" value="%s">%s<br/>' % (r, r)
  print '''
</form>
</pre>
'''

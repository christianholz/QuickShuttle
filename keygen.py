#!/usr/bin/env python

"""one-time key generator to avoid plain-text credentials in requests"""

print "Content-type: text/html\r\n"

import os
import cgi
import shuttle

form = cgi.FieldStorage()

print '<pre>'

if 'user' in form and 'pass' in form:
  u = form.getvalue("user")
  p = form.getvalue("pass")
  k = shuttle.generate_key(u, p)
  print 'ready to bookmark:\n'
  print '<a href="%s%s/bookings.py?k=%s">bookings</a>\n' % (
    os.environ["HTTP_ORIGIN"], os.path.dirname(os.environ["SCRIPT_NAME"]),
    k)
  print '<a href="%s%s/new.py?k=%s">new booking</a>\n' % (
    os.environ["HTTP_ORIGIN"], os.path.dirname(os.environ["SCRIPT_NAME"]),
    k)
else:
  print '''
<form method="post">
  <input name="user" type="text" />
  <input name="pass" type="password" />
  <input type="submit" value="submit" />
</form>'''

print '''
</pre>
'''

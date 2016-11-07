#!/usr/bin/env python

"""list all previously made bookings"""

import os
import sys
import cgi
import datetime
import json
import shuttle
import shcontants

print "Content-type: text/html\r\n"

form = cgi.FieldStorage()
if 'k' not in form:
  sys.exit()
key = form.getvalue("k")

u, p = shuttle.extract_credentials(key)
shuttle.do_login(u, p)

if 'action' in form:
  act = form.getvalue("action")
  if act == "cancel":
    id = form.getvalue("id")
    shuttle.cancel_booking(id)

bookings = shuttle.get_bookings()

print '''<html>
<head>
<title>Connector bookings for {}</title>
<link href="style.css" rel="stylesheet" />
</head>
<body>
'''.format(u)

alldata = json.load(open("all.json"))
routes = list(alldata["true"].keys()) + list(alldata["false"].keys())
freq = {v[:-3]: 0 for v in routes}
for b in bookings:
  freq[b[0][:-3]] += 1
freq = list(freq.items())
freq.sort()
freq.sort(lambda x, y:y[1] - x[1])

print '''<div id="newbar">
'''
for f in freq:
  print '''<div class="newbutton">
  <a href="new.py?k={}&r={}" class="l">{}</a>
  <a href="new.py?k={}&r={}&m=1" class="m">m</a>
  </div>
  '''.format(key, f[0], f[0], key, f[0])

print '</div>'

if 'cal' in form:
  cal = form.getvalue("cal")
  print '''<div id="outlook">
  <a href="outlook.py?k={}&cal={}">download booked trip</a>
  </div>'''.format(key, cal)

print '<div id="bookings">'

for b in bookings:
  dt = datetime.datetime.strptime(b[1], "%m/%d/%Y")
  print '''<div class="booking">
<span class="t">{}</span>
<span class="r">{}</span>
<span class="d">{}, {}</span>
<span class="g">{}, {}</span>
<form method="post">
<input type="hidden" name="action" value="cancel"/>
<input type="hidden" name="id" value="{}"/>
<input type="submit" value="cancel"/>
</form>
</div>
'''.format(dt.strftime("%A, %b %-d"), b[0], b[4], b[3], b[6], b[5], b[2])

print '</div></body></html>'

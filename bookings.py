#!/usr/bin/env python

"""list all previously made bookings"""

import os
import sys
import cgi
import datetime
import json
import shuttle
import shconstants

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
<title>Connector bookings for %s</title>
<link href="style.css" rel="stylesheet" />
</head>
<body>''' % (u)

alldata = json.load(open("all.json"))
routes = list(alldata["true"].keys()) + list(alldata["false"].keys())
freq = {}
for v in routes:
  freq[v[:-3]] = 0
for b in bookings:
  freq[b[0][:-3]] += 1
freq = list(freq.items())
freq.sort()
freq.sort(lambda x, y:y[1] - x[1])

print '<div id="newbar">'

for f in freq:
  if f[1] != 0:
    a = ' freq'
  else:
    a = ''
  print '''<div class="newbutton">
  <a href="new.py?k=%s&r=%s" class="l%s">%s</a>
  <a href="new.py?k=%s&r=%s&m=1" class="m%s">m</a>
</div>''' % (key, f[0], a, f[0], key, f[0], a)

print '</div>'

if 'cal' in form:
  cal = form.getvalue("cal")
  print '''<div id="outlook">
  <a href="outlook.py?k=%s&cal=%s">download booked trip</a>
</div>''' % (key, cal)

print '<div id="bookings">'

for b in bookings:
  dt = datetime.datetime.strptime(b[1], "%m/%d/%Y")
  print '''<div class="booking">
  <span class="t">%s</span>
  <span class="r">%s</span>
  <span class="d">%s, %s</span>
  <span class="g">%s, %s</span>
  <form method="post" action="%s?k=%s">
  <input type="hidden" name="action" value="cancel"/>
  <input type="hidden" name="id" value="%s"/>
  <input type="submit" value="cancel"/>
  </form>
</div>''' % (dt.strftime("%A, %b %-d"), b[0], b[4], b[3], b[6], b[5], 
  os.environ["SCRIPT_NAME"], key, b[2])

print '</div></body></html>'

#!/usr/bin/env python

"""list all previously made bookings"""

import os
import sys
import cgi
import datetime
import json
import shuttle
import shconstants

import shcookie

print "Content-type: text/html\r\n"

shuttle.do_login(shcookie.u, shcookie.p)

form = cgi.FieldStorage()
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
<body>''' % (shcookie.u)

alldata = json.load(open("all.json"))
routes = [r[:-3] for r in alldata["true"].keys()]
routes.sort()
routes = [[r, alldata["true"][r + " AM"][2]] for r in routes]
# freq = {}
# for v in routes:
#   freq[v[:-3]] = 0
# for b in bookings:
#   freq[b[0][:-3]] += 1
# freq = list(freq.items())
# freq.sort()
# freq.sort(lambda x, y:y[1] - x[1])


# header bar

print '<div id="newbar"><div id="newbarin">'

for r in routes:
  print '''<span class="newbutton">
  <a href="new.py?r=%s" class="l">%s</a>
</span>''' % (r[1], r[0])

print '</div></div>'


# list of rides

if 'cal' in form:
  cal = form.getvalue("cal")
  print '''<div id="outlook">
  <a href="outlook.py?cal=%s">download booked trip</a>
</div>''' % (cal)

print '<div id="bookings">'

for b in bookings:
  dt = datetime.datetime.strptime(b[1], "%m/%d/%Y")
  if dt.hour > 13:
    csspm = " pm"
  else:
    csspm = ""
  print '''<div class="booking%s">
  <span class="t">%s</span>
  <span class="r">%s</span>
  <span class="dt">%s</span><span class="dl">%s</span>
  <span class="gt">%s</span><span class="gl">%s</span>
  <form method="post" action="%s">
  <input type="hidden" name="action" value="cancel"/>
  <input type="hidden" name="id" value="%s"/>
  <input type="submit" value="cancel"/>
  </form>
</div>''' % (csspm, dt.strftime("%A, %b %-d"), b[0], b[4], b[3],
  b[6], b[5], os.environ["SCRIPT_NAME"], b[2])

print '</div></body></html>'

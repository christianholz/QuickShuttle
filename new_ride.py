#!/usr/bin/env python

"""show times and book ride"""

import os
import sys
import cgi
import datetime
import json
import urllib
import shuttle
import shconstants

import shcookie


form = cgi.FieldStorage()
if 'r' not in form or 'p' not in form or 'd' not in form:
  sys.exit()
amk = {True: "true", False: "false"}
if form.getvalue("am") == "1":
  am = True
  ams = " AM"
else:
  am = False
  ams = " PM"
dt = form.getvalue("dt")
dtt = datetime.datetime.strptime(dt, "%m/%d/%Y")
pick = form.getvalue("p")
drop = form.getvalue("d")

error_msg = ""

if 't' in form and 'rid' in form:
  trip = form.getvalue("t")
  routeID = form.getvalue("rid")
  
  # book now
  shuttle.do_login_full(shcookie.u, shcookie.p)
  
  r = shuttle.book_ride_full(am, dt, routeID, pick, drop, trip)

  if r[0] == 2:
    # shuttle rebook confirm?
    # return [2, msg, repl]
    r = shuttle.book_ride_full(am, r[2][1], routeID, pick, drop, trip, r[2][0])
    
  if r[0] == 1:
    # success, send to bookings
    print "Status: 302 Moved"
    print "Location: bookings.py?cal=%s" % (r[1])
    print ""
    print "success... redirecting."
    sys.exit()

  if r[0] == 0:
    error_msg = "unknown error booking shuttle"
    # continue

  if r[0] == 3:
    error_msg = "shuttle booked up now, try different one"
    # continue

alldata = json.load(open("all.json"))
routes = list(alldata[amk[am]].keys())
routes.sort()

r = int(form.getvalue("r"))
for rt in alldata[amk[am]].items() + alldata[amk[not am]].items():
  if rt[1][2] == r:
    route = rt[0][:-3]
    break


print "Content-type: text/html\r\n"

print '''<html>
<head>
<title>New booking for %s on %s</title>
<link href="style.css" rel="stylesheet" />
</head>
<body>
''' % (shcookie.u, route)


if error_msg != "":
  print '<div id="error">%s</div>' % (error_msg)


# navigation

print '<div id="newbar"><div id="newbarin">'
print '<span class="newbutton"><a href="bookings.py">bookings</a></span>'
print '<span class="newbutton"><a href="bookings.py">bookings</a></span>'
print '</div></div>'

print '<div id="info">%s%s</div>' % (dtt.strftime("%a, %m/%-d"), ams)


# all route times

for d in alldata[amk[am]][route + ams][0]:
  if d[0] == int(pick):
    pi = d
    break
for d in alldata[amk[am]][route + ams][1]:
  if d[0] == int(drop):
    di = d
    break

print '''<div id="routes">
<div class="route">
<span class="t">%s</span>
<div class="pick">
<div class="pstop">
<span class="st">%s</span>''' % (route, pi[1])
print '<img src="%s/stop-%s.jpg" />' % (shconstants.STOPS_DIR, pi[0])
print '''</div>
</div>
<div class="drop">
<div class="dstop">
<span class="st">%s</span>''' % (di[1])
print '<img src="%s/stop-%s.jpg" />' % (shconstants.STOPS_DIR, di[0])
print '''</div>
</div>'''


shuttle.do_login(shcookie.u, shcookie.p)
droutes = shuttle.get_routes(amk[am], dt)
routeID = -1
for d in droutes:
  if d[1] == route + ams:
    routeID = d[0]
    break
if routeID == -1:
  print "error finding route in that day's routes!"
  sys.exit()

# get_times(isAM, date, routeID, pickID, dropID):
times = shuttle.get_times(amk[am], dt, routeID, pick, drop)
fk = {}
for k in form.keys():
  fk[k] = form.getvalue(k)
fk["rid"] = routeID

print '<div id="times">'
for t in times:
  if t[3] != "0":
    fk["t"] = t[0]
    print '<div class="slot"><a href="%s?%s">%s => %s</a></div>' % (
      os.path.split(os.environ["SCRIPT_NAME"])[1], shuttle.pencode(fk), t[1], t[2]
    )
if len(times) == 0:
  print '<div class="slot"><span class="nr">no available ride found</span></div>'
print '''</div>
</div>
</div>
</body>
</html>
'''

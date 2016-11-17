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


form = cgi.FieldStorage()
if 'k' not in form or 'r' not in form or 'p' not in form or 'd' not in form:
  sys.exit()
key = form.getvalue("k")
if form.getvalue("am") == "1":
  am = True
  amk = "true"
  ams = " AM"
else:
  am = False
  amk = "false"
  ams = " PM"
dt = form.getvalue("dt")
dtt = datetime.datetime.strptime(dt, "%m/%d/%Y")
route = form.getvalue("r")
pick = form.getvalue("p")
drop = form.getvalue("d")

error_msg = ""

if 't' in form and 'rid' in form:
  trip = form.getvalue("t")
  routeID = form.getvalue("rid")
  
  # book now
  u, p = shuttle.extract_credentials(key)
  shuttle.do_login_full(u, p)
  
  r = shuttle.book_ride_full(am, dt, routeID, pick, drop, trip)

  if r[0] == 2:
    # shuttle rebook confirm?
    # return [2, msg, repl]
    r = shuttle.book_ride_full(am, r[2][1], routeID, pick, drop, trip, r[2][0])
    
  if r[0] == 1:
    # success, send to bookings
    print "Status: 302 Moved"
    print "Location: bookings.py?k=%s&cal=%s" % (key, r[1])
    print ""
    print "success... redirecting."
    sys.exit()

  if r[0] == 0:
    error_msg = "unknown error booking shuttle"
    # continue

  if r[0] == 3:
    error_msg = "shuttle booked up now, try different one"
    # continue

if 'm' in form:
  m = True
else:
  m = False

u, p = shuttle.extract_credentials(key)

print "Content-type: text/html\r\n"

print '''<html>
<head>
<title>New booking for %s on %s</title>
<link href="style.css" rel="stylesheet" />
</head>
<body>
''' % (u, route)


if error_msg != "":
  print '<div id="error">%s</div>' % (error_msg)


# navigation

print '<div id="newbar"><div id="newbarin">'
print '<span class="newbutton"><a href="bookings.py?k=%s">bookings</a></span>' % (key)
print '<span class="newbutton"><a href="bookings.py?k=%s">bookings</a></span>' % (key)
print '</div></div>'

print '<div id="info">%s%s</div>' % (dtt.strftime("%a, %m/%-d"), ams)


# all route times

alldata = json.load(open("all.json"))

for d in alldata[amk][route][0]:
  if d[0] == int(pick):
    pi = [d[1], d[2], d[3]]
    break
for d in alldata[amk][route][1]:
  if d[0] == int(drop):
    di = [d[1], d[2], d[3]]
    break

print '''<div id="routes">
<div class="route">
<span class="t">%s</span>
<div class="pick">
<div class="pstop">
<span class="st">%s</span>''' % (route, pi[0])
if m:
  print '<img src="https://maps.googleapis.com/maps/api/staticmap?center=%s,%s&zoom=12&size=%dx%d&maptype=roadmap%%20&markers=size:tiny%%7C%%7C%s,%s&key=%s"/>' % (
    pi[1], pi[2], shconstants.MAP_W, shconstants.MAP_H, pi[1], pi[2], shconstants.GKEY
  )
print '''</div>
</div>
<div class="drop">
<div class="dstop">
<span class="st">%s</span>''' % (di[0])
if m:
  print '<img src="https://maps.googleapis.com/maps/api/staticmap?center=%s,%s&zoom=12&size=%dx%d&maptype=roadmap%%20&markers=size:tiny%%7C%%7C%s,%s&key=%s"/>' % (
    di[1], di[2], shconstants.MAP_W, shconstants.MAP_H, di[1], di[2], shconstants.GKEY
  )
print '''</div>
</div>'''


shuttle.do_login(u, p)
droutes = shuttle.get_routes(amk, dt)
routeID = -1
for d in droutes:
  if d[1] == route:
    routeID = d[0]
    break
if routeID == -1:
  print "error finding route in that day's routes!"
  sys.exit()

# get_times(isAM, date, routeID, pickID, dropID):
times = shuttle.get_times(amk, dt, routeID, pick, drop)
fk = {}
for k in form.keys():
  fk[k] = form.getvalue(k)
fk["rid"] = routeID

print '<div id="times">'
for t in times:
  if t[3] != "0":
    fk["t"] = t[0]
    print '<div class="slot"><a href="%s?%s">%s => %s</a></div>' % (
      os.environ["SCRIPT_NAME"], urllib.urlencode(fk), t[1], t[2]
    )
if len(times) == 0:
  print '<div class="slot"><span class="nr">no available ride found</span></div>'
print '''</div>
</div>
</div>
</body>
</html>
'''

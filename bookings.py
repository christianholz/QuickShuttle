#!/usr/bin/env python

"""list all previously made bookings"""

import os
import sys
import cgi
import datetime
import json
import shuttle
import shconstants
import smtplib

import shcookie

print "Content-type: text/html\r\n"

shuttle.do_login(shcookie.u, shcookie.p)

form = cgi.FieldStorage()
if 'action' in form:
  act = form.getvalue("action")
  if act == "cancel":
    id = form.getvalue("id")
    shuttle.cancel_booking(id)

show_all_routes = 'ar' in form
bookings = shuttle.get_bookings()

print '''<html>
<head>
<title>Connector bookings for %s</title>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
<link href="style.css" rel="stylesheet" />
</head>
<body>''' % (shcookie.u)

alldata = json.load(open("all.json"))
routes = [r[:-3] for r in alldata["true"].keys()]
routes.sort()
routes = [[r, alldata["true"][r + " AM"][2]] for r in routes if len(shcookie.routes) == 0 or show_all_routes or alldata["true"][r + " AM"][2] in shcookie.routes]


# header bar

print '<div id="newbar"><div id="newbarin">'

for r in routes:
  print '''<span class="newbutton">
  <a href="new.py?r=%s" class="l">%s</a>
</span>''' % (r[1], r[0])
if len(shcookie.routes) != 0 and not show_all_routes: 
  print '''<span class="newbutton"><a href="bookings.py?ar=1" class="l">all routes</a></span>'''
print '</div></div>'


# list of rides

if 'cal' in form:
  cal = form.getvalue("cal")
  print '''<div id="outlook">
  <a href="outlook.py?cal=%s">download booked trip</a>
</div>''' % (cal)

print '<div id="bookings">'

for b in bookings:
  past = False
  dt = datetime.datetime.strptime(b['dd'] + ' ' + b['dt'], "%m/%d/%Y %I:%M %p")
  if dt < datetime.datetime.now() - datetime.timedelta(hours=2) - datetime.timedelta(minutes=60):
	  continue
  if "PM" in b['dt']:
    csspm = " pm"
  else:
    csspm = ""
  if dt < datetime.datetime.now() - datetime.timedelta(hours=2) - datetime.timedelta(minutes=1):
    past = True
    csspm += " past"
  
  print '''<div class="booking%s">
  <span class="t">%s</span>
  <span class="r">%s</span>
  <span class="dt">%s</span><span class="dl">%s</span>
  <span class="gt">%s</span><span class="gl">%s</span>''' % (
    csspm, dt.strftime("%A, %b %d"), b['r'], b['dt'], b['dl'], b['gt'], b['gl'])
  
  if 'cn' in b:
    print '  <span class="cn">Connector %s</span>' % (b['cn'])
    if not past:
      loc = shuttle.get_shuttle_location(b['r'], b['cn'])
      if loc != None:
        stop = shuttle.get_stop_gps(b['r'], b['dl'])
        if stop != None:
          dst = shuttle.get_maps_eta((loc['lat'], loc['lon']), (stop[0], stop[1]))
          print '  <span class="et">ETA: %s (<a href="https://www.google.com/maps?q=%f,%f">%s</a>)</span>' % (
            dst[1], loc['lat'], loc['lon'], dst[0])
        
  if 'cl' in b:
    print '''  <form method="post" action="%s" onsubmit="return confirm('Cancel?');">
    <input type="hidden" name="action" value="cancel"/>
    <input type="hidden" name="id" value="%s"/>
    <input type="submit" value="cancel"/>
  </form>''' % (os.environ["SCRIPT_NAME"], b['cl'])
  print '</div>'

print '</div></body><!--'
# print datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
print '--></html>'

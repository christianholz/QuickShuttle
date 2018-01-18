#!/usr/bin/env python

"""calendar feed for all bookings"""

import os
import sys
import cgi
import datetime
import json
import shuttle
import shconstants

import shcookie
shuttle.do_login(shcookie.u, shcookie.p)

# print 'Content-Type: text/html'
print 'Content-Type: text/calendar;charset=utf-8'
print 'Content-Disposition: attachment;filename=connector-%s.ics' % (shcookie.u)
print 'Pragma: no-cache'
print 'Vary: Origin'
print 'Strict-Transport-Security: max-age=15552000; preload'
print 'Expires: Sat, 01 Jan 2000 00:00:00 GMT'
print 'Cache-Control: private, no-cache, no-store,must-revalidate'
print ''

print '''BEGIN:VCALENDAR
PRODID:-//QuickShuttle//booked schedule 0.1//EN
X-WR-CALNAME:%s's Connector bookings
X-PUBLISHED-TTL:PT12H
X-ORIGINAL-URL:/shuttle/
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:PUBLISH''' % (shcookie.u)

bookings = shuttle.get_bookings()

n = datetime.datetime.now()
u = datetime.datetime.utcnow()
h = int((u - n).seconds / 60 / 60) + 2
h = datetime.timedelta(hours = h)

# alldata = json.load(open("all.json"))
# routes = [r[:-3] for r in alldata["true"].keys()]
# routes.sort()
# routes = [[r, alldata["true"][r + " AM"][2]] for r in routes if len(shcookie.routes) == 0 or show_all_routes or alldata["true"][r + " AM"][2] in shcookie.routes]

for b in bookings:
  past = False
  dt = datetime.datetime.strptime(b['dd'] + ' ' + b['dt'], "%m/%d/%Y %I:%M %p")
  gt = datetime.datetime.strptime(b['dd'] + ' ' + b['gt'], "%m/%d/%Y %I:%M %p")
  dt += h
  gt += h
  
  print 'BEGIN:VEVENT'
  print 'DTSTAMP:%s' % (n.strftime('%Y%m%dT%H%M%SZ'))
  print 'LAST-MODIFIED:%s' % (n.strftime('%Y%m%dT%H%M%SZ'))
  print 'CREATED:%s' % (n.strftime('%Y%m%dT%H%M%SZ'))
  print 'SEQUENCE:0'
  print 'ORGANIZER;CN=QuickShuttle:MAILTO:shuttle@cholz.de'
  print 'DTSTART:%s' % (dt.strftime('%Y%m%dT%H%M%SZ'))
  print 'DTEND:%s' % (gt.strftime('%Y%m%dT%H%M%SZ'))
  print 'UID:%s@shuttle.cholz.de' % (dt.strftime('%Y%m%dT%H%M%SZ'))
  print 'SUMMARY:' + b['r']
  print 'LOCATION:' + b['dl']
  print 'URL:http://cholz.de/shuttle/bookings.py'
  print '''DESCRIPTION:Connector ride %s
 %s %s
 %s %s''' % (dt.strftime("%A, %b %d"), b['dt'], b['dl'], b['gt'], b['gl'])
  print 'CLASS:PUBLIC'
  print 'STATUS:CONFIRMED'
  print 'PARTSTAT:NEEDS-ACTION'
  print 'END:VEVENT'

print 'END:VCALENDAR'

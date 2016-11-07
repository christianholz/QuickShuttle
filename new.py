#!/usr/bin/env python

"""show routes and stops"""

import os
import sys
import cgi
import datetime
import json
import urllib
import shuttle
import shconstants


print "Content-type: text/html\r\n"

form = cgi.FieldStorage()
if 'k' not in form:
  sys.exit()
key = form.getvalue("k")

if 'm' in form:
  m = True
else:
  m = False

u, p = shuttle.extract_credentials(key)

if 'action' in form:
  act = form.getvalue("action")
  if act == "cancel":
    id = form.getvalue("id")
    shuttle.cancel_booking(id)

if 'dt' in form:
  dt = datetime.datetime.strptime(form.getvalue("dt"), "%m/%d/%Y")
else:
  dt = datetime.datetime.now()
  while dt.weekday() > 4:
    dt += datetime.timedelta(1, 0)
if 'am' in form:
  if form.getvalue("am") == "1":
    am = True
  else:
    am = False
else:
  if dt.date() != datetime.date.today():
    am = True
  elif dt.hour > 19:
    am = True
    dt += datetime.timedelta(1, 0)
  elif dt.hour > 10:
    am = False
  else:
    am = True
    
if 'm' in form:
  m = True
  mk = "1"
else:
  m = False
  mk = "0"
  
if 'r' in form:
  r = form.getvalue("r")
else:
  r = ""
  
if am:
  ams = " AM"
  amk = "true"
else:
  ams = " PM"
  amk = "false"


print '''<html>
<head>
<title>New booking for %s</title>
<link href="style.css" rel="stylesheet" />
''' % (u)

print '''<script>rid='';pid='';did='';
function pSel(r,d,e){rid=r;pid=d;e.parentElement.style.backgroundColor="red";nav();}
function dSel(r,d,e){rid=r;did=d;e.parentElement.style.backgroundColor="red";nav();}
function nav(){if(rid!=''&&pid!=''&&did!='')location.href="new_ride.py?k=%s&dt=%s&am=%s&m=%s&r="+rid+"&p="+pid+"&d="+did;}
</script>
''' % (key, dt.strftime("%m/%-d/%Y"), amk, mk)

print '''</head>
<body>
'''


alldata = json.load(open("all.json"))
routes = list(alldata[amk].keys())
routes.sort()

fk = {}
for k in form.keys():
  fk[k] = form.getvalue(k)
print '<div id="newbar">'
fk["am"] = "1"
print '<a href="%s?%s">am</a>' % (os.environ["SCRIPT_NAME"], urllib.urlencode(fk))
fk["am"] = "0"
print '<a href="%s?%s">pm</a> |' % (os.environ["SCRIPT_NAME"], urllib.urlencode(fk))

dn = dt
for i in range(5):
  dn += datetime.timedelta(1, 0)
  while dn.weekday() > 4:
    dn += datetime.timedelta(1, 0)
  fk["dt"] = dn.strftime("%m/%-d/%Y")
  fk["am"] = "1"
  print ' <a href="%s?%s">%s am</a>' % (os.environ["SCRIPT_NAME"], urllib.urlencode(fk), dn.strftime("%a, %m/%-d"))
  fk["am"] = "0"
  print ' <a href="%s?%s">pm</a>' % (os.environ["SCRIPT_NAME"], urllib.urlencode(fk))
print '</div>'

print '<div id="routes">'

try:
  i = routes.index(r + ams)
  routes = [r + ams] + routes[:i] + routes[i + 1:]
except:
  pass

print '<div id="info">%s%s</div>' % (dt.strftime("%a, %m/%-d"), ams)

blu = {False: "0", True: "1"}

for r in routes:
  print '<div class="route"><span class="t">%s</span>' % (r)
  
  print '<div id="pick">'
  for d in alldata[amk][r][0]:
    print '<div class="pstop">'
    print '''<a href="#" onclick="pSel('%s','%s',this);return false">''' % (r, d[0])
    print '<span class="st">%s</span>' % (d[1])
    if m:
      print '<img src="https://maps.googleapis.com/maps/api/staticmap?center=%s,%s&zoom=12&size=100x100&maptype=roadmap%20&markers=size:tiny%7C%7C%s,%s&key=%s"/>' % (
        d[2], d[3], d[2], d[3], shconstants.GKEY
      )
    print '</a></div>'  
  print '</div>'

  print '<div id="drop">'
  for d in alldata[amk][r][1]:
    print '<div class="dstop">'
    print '''<a href="#" onclick="dSel('%s','%s',this);return false">''' % (r, d[0])
    print '<span class="st">%s</span>' % (d[1])
    if m:
      print '<img src="https://maps.googleapis.com/maps/api/staticmap?center=%s,%s&zoom=12&size=100x100&maptype=roadmap%20&markers=size:tiny%7C%7C%s,%s&key=%s"/>' % (
        d[2], d[3], d[2], d[3], shconstants.GKEY
      )
    print '</a></div>'  
  print '</div>'
  
  print '</div>'

print '</div></body></html>'

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

import shcookie


print "Content-type: text/html\r\n"

form = cgi.FieldStorage()
if 'action' in form:
  act = form.getvalue("action")
  if act == "cancel":
    id = form.getvalue("id")
    shuttle.do_login(shcookie.u, shcookie.p)
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
  
amk = {True: "true", False: "false"}
if am:
  ams = " AM"
else:
  ams = " PM"


print '''<html>
<head>
<title>New booking for %s</title>
<link href="style.css" rel="stylesheet" />
''' % (shcookie.u)

print '''<script>
rid='';pid='';did='';
function pSel(r,d,e){pid=d;nav(r,e);}
function dSel(r,d,e){did=d;nav(r,e);}
function nav(r,e){rid=r;
	var ch=e.parentElement.parentElement.children;
	for(var i=0;i!=ch.length;++i){
		ch[i].classList.remove("sel");
	}
	e.parentElement.classList.add("sel");
	if(rid!=''&&pid!=''&&did!='')location.href="new_ride.py?dt=%s&am=%d&r="+rid+"&p="+pid+"&d="+did;}
</script>
''' % (dt.strftime("%m/%-d/%Y"), int(am))

print '''</head>
<body>
'''


alldata = json.load(open("all.json"))
routes = list(alldata[amk[am]].keys())
routes.sort()

if 'r' in form:
  r = int(form.getvalue("r"))
  for rt in alldata[amk[am]].items() + alldata[amk[not am]].items():
    if rt[1][2] == r:
      r = rt[0][:-3]
      break
else:
  r = ""
      

# header

fk = {}
for k in form.keys():
  fk[k] = form.getvalue(k)
print '<div id="newbar"><div id="newbarin">'
if not am:
  fk["am"] = "1"
  print '<a href="%s?%s">am</a><span class="s">|</span>' % (os.path.split(os.environ["SCRIPT_NAME"])[1], shuttle.pencode(fk))
else:
  fk["am"] = "0"
  print '<a href="%s?%s">pm</a><span class="s">|</span>' % (os.path.split(os.environ["SCRIPT_NAME"])[1], shuttle.pencode(fk))

dn = dt
for i in range(5):
  dn += datetime.timedelta(1, 0)
  while dn.weekday() > 4:
    dn += datetime.timedelta(1, 0)
  fk["dt"] = dn.strftime("%m/%-d/%Y")
  fk["am"] = "1"
  print '<a href="%s?%s">%s am</a>' % (os.path.split(os.environ["SCRIPT_NAME"])[1], shuttle.pencode(fk), dn.strftime("%a, %m/%-d"))
  fk["am"] = "0"
  print '<a href="%s?%s">pm</a>' % (os.path.split(os.environ["SCRIPT_NAME"])[1], shuttle.pencode(fk))
print '</div></div>'


# routes

print '<div id="info">%s%s</div>' % (dt.strftime("%a, %m/%-d"), ams)
print '<div id="routes">'

try:
  i = routes.index(r + ams)
  routes = [r + ams]
except:
  pass

blu = {False: "0", True: "1"}

for r in routes:
  print '<div class="route"><span class="t">%s</span>' % (r)
  
  print '<div class="pick">'
  for d in alldata[amk[am]][r][0]:
    print '<div class="pstop">'
    print '''<a href="#" onclick="pSel('%s','%s',this);return false">''' % (alldata[amk[am]][r][2], d[0])
    print '<span class="st">%s</span>' % (d[1])
    print '<img src="%s/stop-%s.jpg" />' % (shconstants.STOPS_DIR, d[0])
    print '</a></div>'  
  print '</div>'

  print '<div class="drop">'
  for d in alldata[amk[am]][r][1]:
    print '<div class="dstop">'
    print '''<a href="#" onclick="dSel('%s','%s',this);return false">''' % (alldata[amk[am]][r][2], d[0])
    print '<span class="st">%s</span>' % (d[1])
    print '<img src="%s/stop-%s.jpg" />' % (shconstants.STOPS_DIR, d[0])
    print '</a></div>'  
  print '</div>'
  
  print '</div>'

print '</div></body></html>'

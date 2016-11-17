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

print '''<script>
window.onload=function(){
  var l=document.getElementsByTagName('a');
  for(var i=0;i!=l.length;++i) {
    l[i].href+="&k=%s";
  }
}
rid='';pid='';did='';
function pSel(r,d,e){pid=d;nav(r,e);}
function dSel(r,d,e){did=d;nav(r,e);}
function nav(r,e){rid=r;
	var ch=e.parentElement.parentElement.children;
	for(var i=0;i!=ch.length;++i){
		ch[i].classList.remove("sel");
	}
	e.parentElement.classList.add("sel");
	if(rid!=''&&pid!=''&&did!='')location.href="new_ride.py?k=%s&dt=%s&am=%d&m=%s&r="+rid+"&p="+pid+"&d="+did;}
</script>
''' % (key, key, dt.strftime("%m/%-d/%Y"), int(am), mk)

print '''</head>
<body>
'''


alldata = json.load(open("all.json"))
routes = list(alldata[amk].keys())
routes.sort()


# header

fk = {}
for k in form.keys():
  if k != "k":
    fk[k] = form.getvalue(k)
print '<div id="newbar"><div id="newbarin">'
if not am:
  fk["am"] = "1"
  print '<a href="%s?%s">am</a><span class="s">|</span>' % (os.environ["SCRIPT_NAME"], urllib.urlencode(fk))
else:
  fk["am"] = "0"
  print '<a href="%s?%s">pm</a><span class="s">|</span>' % (os.environ["SCRIPT_NAME"], urllib.urlencode(fk))

dn = dt
for i in range(5):
  dn += datetime.timedelta(1, 0)
  while dn.weekday() > 4:
    dn += datetime.timedelta(1, 0)
  fk["dt"] = dn.strftime("%m/%-d/%Y")
  fk["am"] = "1"
  print '<a href="%s?%s">%s am</a>' % (os.environ["SCRIPT_NAME"], urllib.urlencode(fk), dn.strftime("%a, %m/%-d"))
  fk["am"] = "0"
  print '<a href="%s?%s">pm</a>' % (os.environ["SCRIPT_NAME"], urllib.urlencode(fk))
print '</div></div>'


# routes

print '<div id="info">%s%s</div>' % (dt.strftime("%a, %m/%-d"), ams)
print '<div id="routes">'

try:
  i = routes.index(r + ams)
  routes = [r + ams] + routes[:i] + routes[i + 1:]
except:
  pass

blu = {False: "0", True: "1"}

for r in routes:
  print '<div class="route"><span class="t">%s</span>' % (r)
  
  print '<div class="pick">'
  for d in alldata[amk][r][0]:
    print '<div class="pstop">'
    print '''<a href="#" onclick="pSel('%s','%s',this);return false">''' % (r, d[0])
    print '<span class="st">%s</span>' % (d[1])
    if m:
      print '<img src="https://maps.googleapis.com/maps/api/staticmap?center=%s,%s&zoom=12&size=%dx%d&maptype=roadmap%%20&markers=size:tiny%%7C%%7C%s,%s&key=%s"/>' % (
        d[2], d[3], shconstants.MAP_W, shconstants.MAP_H, d[2], d[3], shconstants.GKEY
      )
    print '</a></div>'  
  print '</div>'

  print '<div class="drop">'
  for d in alldata[amk][r][1]:
    print '<div class="dstop">'
    print '''<a href="#" onclick="dSel('%s','%s',this);return false">''' % (r, d[0])
    print '<span class="st">%s</span>' % (d[1])
    if m:
      print '<img src="https://maps.googleapis.com/maps/api/staticmap?center=%s,%s&zoom=12&size=%dx%d&maptype=roadmap%%20&markers=size:tiny%%7C%%7C%s,%s&key=%s"/>' % (
        d[2], d[3], shconstants.MAP_W, shconstants.MAP_H, d[2], d[3], shconstants.GKEY
      )
    print '</a></div>'  
  print '</div>'
  
  print '</div>'

print '</div></body></html>'

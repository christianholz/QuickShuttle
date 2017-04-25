#!/usr/bin/env python

"""hacked-together API for backend"""

import urllib
import urllib2
import cookielib
import re
import datetime
import json
import base64
import struct
import md5
import shconstants
import os
import sys
if sys.stdin.isatty():
  import PIL.Image


handler = urllib2.HTTPSHandler(debuglevel=0)
cj = cookielib.CookieJar()


class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    https_response = http_response


def date_today():
  dt = datetime.date.today()
  while dt.weekday() > 4:
    dt += datetime.timedelta(1, 0)
  ds = "%d/%d/%d" % (dt.month, dt.day, dt.year)
  return ds


def date_tomorrow():
  dt = datetime.date.today() + datetime.timedelta(1, 0)
  while dt.weekday() > 4:
    dt += datetime.timedelta(1, 0)
  ds = "%d/%d/%d" % (dt.month, dt.day, dt.year)
  return ds


def do_login(u, p):
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), handler, NoRedirection)
  opener.addheaders = [('User-Agent', shconstants.USER_AGENT)]
  r = opener.open(shconstants.URL_LOGIN_MOBILE)
  s = r.read()
  
  re1 = re.compile('name="__RequestVerificationToken" .*? value="(.+?)"')
  m = re1.findall(s)
  if len(m) == 0:
    return
  
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), handler, NoRedirection)
  opener.addheaders = [('User-Agent', shconstants.USER_AGENT)]
  r = opener.open(shconstants.URL_LOGIN_MOBILE, urllib.urlencode({
    "__RequestVerificationToken": m[0],
    "UserName": u,
    "Password": p
  }))
  r.read()


def do_login_full(u, p):
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), handler, NoRedirection)
  opener.addheaders = [('User-Agent', shconstants.USER_AGENT)]
  r = opener.open(shconstants.URL_LOGIN_DESKTOP)
  s = r.read()
  
  re1 = re.compile('name="__RequestVerificationToken" .*? value="(.+?)"')
  m = re1.findall(s)
  if len(m) == 0:
    return
  
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), handler)
  opener.addheaders = [('User-Agent', shconstants.USER_AGENT)]
  r = opener.open(shconstants.URL_LOGIN_DESKTOP, urllib.urlencode({
    "__RequestVerificationToken": m[0],
    "ComputerTypes": "PrivateComputer",
    "UserName": u,
    "Password": p
  }))
  r.read()


def get_bookings():
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), handler)
  opener.addheaders = [('User-Agent', shconstants.USER_AGENT),
    ('Referer', shconstants.URL_LOGIN_MOBILE),
    ('Accept', '*/*'),
    ('Accept-Encoding', 'gzip, deflate, br'),
    ('Accept-Language', 'en-US,en;q=0.8')
  ]
  r = opener.open(shconstants.URL_FLEX_MY_MOBILE)
  s = r.read()
  
  st = 0
  trips = []
  rc = re.compile('<a href="#" onclick="cancelFlex\(([0-9]+?)\)" style="margin:')
  spl = s.split("\n")
  for j, l in enumerate(spl):
    l = l.strip()
    if l == '</li>' and st != 0:
      st = 0
      continue
    
    if st == 0:
      try:
        i = l.index('Date: ')
        t = {'r': spl[j - 5].strip(), 'dd': l[i + 6:]}
        trips.append(t)
        st = 1
      except ValueError:
        pass
    if st == 1:
      m = rc.findall(l)
      if len(m):
        t['cl'] = m[0]
        st = 2
        
    if st <= 2:
      try:
        i = l.index('Pickup: <b>')
        t['dl'] = l[i + 11:-4]
        st = 3
      except ValueError:
        pass
    elif st == 3:
      i = l.index('&nbsp;@&nbsp;<b>')
      t['dt'] = l[i + 16:-4]
      st = 4
    
    if st <= 4:
      try:
        i = l.index('Dropoff: <b>')
        t['gl'] = l[i + 12:-4]
        st = 5
      except ValueError:
        pass
    elif st == 5:
      i = l.index('&nbsp;@&nbsp;<b>')
      t['gt'] = l[i + 16:-4]
      st = 6
    
    if st <= 6:
      try:
        i = l.index('Connector : ')
        t['cn'] = l[i + 12:]
        st = 0
      except ValueError:
        pass
  return trips


def cancel_booking(id):
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), handler, NoRedirection)
  opener.addheaders = [('User-Agent', shconstants.USER_AGENT),
    ('Origin', shconstants.URL_MOBILE),
    ('X-Requested-With', 'XMLHttpRequest'),
    ('Referer', shconstants.URL_FLEX_MY_MOBILE),
    ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
    ('Accept', '*/*'),
    ('Accept-Encoding', 'gzip, deflate, br'),
    ('Accept-Language', 'en-US,en;q=0.8')
  ]
  r = opener.open(shconstants.URL_CANCEL_MOBILE, urllib.urlencode({
    "id": id
  }))
  s = r.read()


def get_trips(isAM, date, routeID, pickID, dropID, tripID):
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), handler, NoRedirection)
  opener.addheaders = [('User-Agent', shconstants.USER_AGENT),
    ('Origin', shconstants.URL_MOBILE),
    ('X-Requested-With', 'XMLHttpRequest'),
    ('Referer', shconstants.URL_FLEX_MOBILE),
    ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
    ('Accept', '*/*'),
    ('Accept-Encoding', 'gzip, deflate, br'),
    ('Accept-Language', 'en-US,en;q=0.8')
  ]
  r = opener.open(shconstants.URL_RETURN_MOBILE, urllib.urlencode({
    "isAM": str(isAM).lower(),
    "date": date,
    "routeID": routeID,
    "pickID": pickID,
    "dropID": dropID,
    "tripID": tripID,
    "park": "false"
  }))
  return r


def get_trips_full(isAM, date, routeID, pickID, dropID, tripID):
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), handler, NoRedirection)
  opener.addheaders = [('User-Agent', shconstants.USER_AGENT),
    ('Origin', shconstants.URL_DESKTOP),
    ('X-Requested-With', 'XMLHttpRequest'),
    ('Referer', shconstants.URL_FLEX_DESKTOP),
    ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
    ('Accept', '*/*'),
    ('Accept-Encoding', 'gzip, deflate, br'),
    ('Accept-Language', 'en-US,en;q=0.8')
  ]
  r = opener.open(shconstants.URL_RETURN_DESKTOP, urllib.urlencode({
    "isAM": str(isAM).lower(),
    "date": date,
    "routeID": routeID,
    "pickID": pickID,
    "dropID": dropID,
    "tripID": tripID,
    "bike": "false"
  }))
  return r


def book_ride_full(isAM, date, routeID, pickID, dropID, tripID, cancelID=None):
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), handler, NoRedirection)
  opener.addheaders = [('User-Agent', shconstants.USER_AGENT),
    ('Origin', shconstants.URL_DESKTOP),
    ('X-Requested-With', 'XMLHttpRequest'),
    ('Referer', shconstants.URL_FLEX_DESKTOP),
    ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
    ('Accept', '*/*'),
    ('Accept-Encoding', 'gzip, deflate, br'),
    ('Accept-Language', 'en-US,en;q=0.8')
  ]
  ampm = {True: "AM", False: "PM"}

  if not cancelID:
    r = opener.open(shconstants.URL_BOOK_DESKTOP, urllib.urlencode({
      "AMorPMValue": ampm[isAM],
      "NeedsBikeRack": "false",
      "DatePicker": date,
      "DropDownList": routeID,
      "DropDownListPick": pickID,
      "DropDownListDrop": dropID,
      "rbScheds": tripID,
      "IsFavorite": "false",
      "X-Requested-With": "XMLHttpRequest"
    }))
  else:
    r = opener.open(shconstants.URL_DOUBLE_DESKTOP, urllib.urlencode({
      "isAM": str(isAM).lower(),
      "d": date,
      "rid": routeID,
      "tid": tripID,
      "pid": pickID,
      "did": dropID,
      "bike": "False",
      "park": "False",
      "wc": "False",
      "fav": "false",
      "db": "false",
      "cid": cancelID
    }))
  s = r.read()
  
  rs = re.compile('<label>CONFIRMATION:</label>&nbsp;<i>(C.+?)</i>')
  ro = re.compile("var fid = '([0-9]+)';")
  rr = re.compile('<button id="Replace" onclick="buttonYes_onclick\(&quot;([0-9|]+?)&quot;,&quot;([0-9]+?)&quot;,([0-9]+?),([0-9]+?),([0-9]+?),([0-9]+?),&quot;.*?;\)')
  rb = re.compile('<tr')
  rc = re.compile('</tr')
  rh = re.compile('(<.+?>)')
  
  res = 0 # 1 = good, 2 = already, 3 = full
  n = False
  outlook = ""
  cm = False
  msg = ""
  repl = []
  for l in s.split("\n"):
    l = l.strip()
    
    if res == 2:
      m = rr.findall(l)
      if len(m):
        repl = list(m[0])
        break
    
    if 'You already have the following trip' in l:
      res = 2
      cm = True
      dc = 1
      
    if cm:
      msg += rh.sub('', l)
      dc += len(rb.findall(l))
      dc -= len(rc.findall(l))
      if dc <= 0:
        cm = False
    
    if '<li>Unavailable due to Seats</li>' in l:
      res = 3
      break
    
    if '<label>CONFIRMATION:</label>' in l:
      res = 1
      m = rs.findall(l)
      if len(m):
        msg = m[0]
      break
    
    if n:
      m = ro.findall(l)
      if len(m):
        outlook = m[0]
      n = False
    if 'function buttonOutlook_click()' in l:
      n = True
  
  if res == 1:
    return [1, outlook, msg]
  if res == 2:
    return [2, msg, repl]
  if res == 3:
    return [3, "unavailable"]
  return [0, "error"]

  
def download_ics_full(cal):
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), handler, NoRedirection)
  opener.addheaders = [('User-Agent', shconstants.USER_AGENT),
    ('Referer', shconstants.URL_BOOK_DESKTOP),
  ]
  r = opener.open(shconstants.URL_OUTLOOK_DESKTOP + "?id=" + cal)
  return r


def get_routes_full(isAM, dt=None):
  if dt == None:
    dt = date_today()
  r = get_trips_full(isAM, dt, "0", "0", "0", "0")
  s = r.read()
  
  rg = re.compile('jQuery\("#DropDownList"\).*?"dataSource":(.*?),[ ]?"dataTextField"')
  for l in s.split("\n"):
    l = l.strip()
    m = rg.findall(l)
    if len(m):
      routes = json.loads(m[0])
      break
  return [[r["ID"], r["Name"], r["RouteMasterID"], r["Description"]] for r in routes]


def get_routes(isAM, dt):
  r = get_trips(isAM, dt, "0", "0", "0", "0")
  s = r.read()
  
  rg = re.compile('<option.*?value="([0-9]+)">(.+?)</option>')
  logging = False
  routes = []
  for l in s.split("\n"):
    l = l.strip()
    if logging and '</select>' in l:
      logging = False
      break
    if logging:
      m = rg.findall(l)
      if len(m):
        routes.append([m[0][0], m[0][1]])
    if not logging and 'select id="ddRoutes"' in l and '--SELECT A ROUTE--' in l:
      logging = True
  return routes
  

def get_stops_for(isAM, routeID):
  ds = date_today()
  rg = re.compile('<option.*?value="([0-9]+)">(.+?)</option>')
  # get_trips(isAM, date, routeID, pickID, dropID, tripID, park, handler, cj)
  r = get_trips(isAM, ds, routeID, "0", "0", "0", "false", handler, cj)
  s = r.read()
  pick = False
  drop = False
  stops = [[], []]
  for l in s.split("\n"):
    l = l.strip()
    if (pick or drop) and '</select>' in l:
      pick = False
      drop = False
    if pick:
      m = rg.findall(l)
      if len(m):
        stops[0].append([m[0][0], m[0][1]])
    if drop:
      m = rg.findall(l)
      if len(m):
        stops[1].append([m[0][0], m[0][1]])
    if not pick and not drop and 'select id="ddPicks"' in l and '--SELECT A PICKUP--' in l:
      pick = True
    if not pick and not drop and 'select id="ddDrops"' in l and '--SELECT A DROPOFF--' in l:
      drop = True
  return stops


def get_stop_locations_full(isAM, routeID, dt=None):
  if dt == None:
    dt = date_today()
  r = get_trips_full(isAM, dt, routeID, "NaN", "NaN", "NaN")
  s = r.read()
  
  rg1 = re.compile('jQuery\("#DropDownListPick"\).*?"dataSource":(.*?),[ ]?"dataTextField"')
  rg2 = re.compile('jQuery\("#DropDownListDrop"\).*?"dataSource":(.*?),[ ]?"dataTextField"')
  for l in s.split("\n"):
    l = l.strip()
    m = rg1.findall(l)
    if len(m):
      pick = json.loads(m[0])
    m = rg2.findall(l)
    if len(m):
      drop = json.loads(m[0])
  stops = [
    [[p["ID"], p["Name"], p["Latitude"], p["Longitude"]] for p in pick],
    [[d["ID"], d["Name"], d["Latitude"], d["Longitude"]] for d in drop]
  ]
  return stops


def get_times(isAM, date, routeID, pickID, dropID):
  r = get_trips(isAM, date, routeID, pickID, dropID, "0")
  s = r.read()
  
  rg = re.compile('<label class="label-sched-radio" for="rb([0-9]+)">(.+?)</label>')
  tab = False
  tr = 0
  times = []
  n = False
  
  for l in s.split("\n"):
    l = l.strip()
    if n:
      t.append(l)
      n = False
      continue
    if '</tr>' in l:
      tr = 0
      continue
    if tab and tr == 2 and '<td class="td-schedule">' in l:
      n = True
    if tab and tr == 1:
      m = rg.findall(l)
      if len(m) != 0:
        t = list(m[0])
        times.append(t)
        tr = 2
    if tab and tr == 0 and '<tr>' in l:
      tr = 1
    if tab and l == "</table>":
      break
    if 'id="tableSchedules"' in l:
      tab = True
  return times


def get_times_full(isAM, date, routeID, pickID, dropID):
  r = get_trips_full(isAM, date, routeID, pickID, dropID, "NaN")
  s = r.read()
  
  rg = re.compile('<input id="rbScheds" name="rbScheds" type="radio" value="([0-9]+)" />')
  rn = re.compile('">(.+?)</td>')
  nl = 0
  times = []
  for l in s.split("\n"):
    l = l.strip()
    if nl > 0:
      m = rn.findall(l)
      if len(m):
        t.append(m[0])
      nl -= 1
    else:
      m = rg.findall(l)
      if len(m):
        t = [m[0]]
        times.append(t)
        nl = 5
  return times
  

def download_all_full():
  all_routes = {}
  morning = [True, False]
  dt = datetime.datetime.now()
  for isAM in morning:
    print "downloading for morning = " + str(isAM)
    routes = get_routes_full(isAM, dt=dt.strftime('%m/%d/%Y'))
    all_routes[isAM] = {}
    for j, r in enumerate(routes):
      print "  downloading stops for " + r[1] + " (%d/%d)" % (j + 1, len(routes))
      s = get_stop_locations_full(isAM, r[0], dt=dt.strftime('%m/%d/%Y'))
      s.extend(r[2:4])
      all_routes[isAM][r[1]] = s
  json.dump(all_routes, open("all.json", "w"))
  

def download_map_tiles():
  tm = ["true", "false"]
  routes = json.load(open("all.json"))
  dl = []
  if not os.path.exists(shconstants.STOPS_DIR):
    os.mkdir(shconstants.STOPS_DIR)
  for am in tm:
    for route in routes[am].items():
      for stop in route[1][0] + route[1][1]:
        sid = int(stop[0])
        if not sid in dl:
          print "downloading stop %s (%s) for %s" % (stop[0], stop[1], route[0])
          r = urllib2.urlopen("https://maps.googleapis.com/maps/api/staticmap?center=%s,%s&zoom=12&size=%dx%d&maptype=roadmap%%20&markers=size:tiny%%7C%%7C%s,%s&key=%s" % (
            stop[2], stop[3], shconstants.MAP_W, shconstants.MAP_H + 40, stop[2], stop[3], shconstants.GKEY))
          f = open(os.path.join(shconstants.STOPS_DIR, "stop-%s.jpg" % stop[0]), "wb")
          f.write(r.read())
          f.close()
          img = PIL.Image.open(os.path.join(shconstants.STOPS_DIR, "stop-%s.jpg" % stop[0]))
          nig = img.crop((0, 20, shconstants.MAP_W, shconstants.MAP_H + 20))
          nig.convert("RGB").save(os.path.join(shconstants.STOPS_DIR, "stop-%s.jpg" % stop[0]), "JPEG", quality=70, optimize=True, progressive=True)
          dl.append(sid)


def pencode(d):
  if len(d) == 0:
    return ""
  it = d.items()
  s = "%s=%s" % (it[0][0], it[0][1])
  for i in range(1, len(it)):
    s += "&%s=%s" % (it[i][0], it[i][1])
  return s
  

def generate_key(user, pw, routes=None):
  l = len(user)
  k = shconstants.ENCRYPT_KEY[l:]
  s = user + '\x00' + pw + '\x00'
  if routes == None or routes == []:
    r = '\0'
  else:
    r = struct.pack('<B', len(routes)) + b''.join([struct.pack('<H', v) for v in routes])
  s += r
  h = md5.md5(s).hexdigest()
  s += h[:32 - len(s)]
  c = encode(k, s)
  return base64.urlsafe_b64encode(c[:16] + chr(l) + c[16:])
  
  
def extract_credentials(s):
  s = base64.urlsafe_b64decode(s)
  c = s[:16] + s[-16:]
  l = ord(s[16])
  k = shconstants.ENCRYPT_KEY[l:]
  s = decode(k, c)
  i = s.index("\x00")
  u = s[:i]
  s = s[i + 1:]
  i = s.index("\x00")
  p = s[:i]
  s = s[i + 1:]
  l = struct.unpack('<B', s[0])[0]
  if l > 0:
    rid = struct.unpack('<' + 'H' * l, s[1:l * 2 + 1])
  else:
    rid = ()
  return [u, p, rid]


def encode(key, clear):
  enc = []
  for i in range(len(clear)):
    key_c = key[i % len(key)]
    enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
    enc.append(enc_c)
  return "".join(enc)


def decode(key, enc):
  dec = []
  for i in range(len(enc)):
    key_c = key[i % len(key)]
    dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
    dec.append(dec_c)
  return "".join(dec)


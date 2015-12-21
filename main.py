#!/usr/bin/env python
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, os, urllib, urllib2, json, logging, sha, time, datetime
import jinja2

from google.appengine.ext import db
from google.appengine.ext.db import Key
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from math import radians, cos, sin, asin, sqrt


class Request(db.Model):
  name = db.StringProperty()
  gender = db.StringProperty()
  what = db.StringProperty()
  phone = db.StringProperty()
  opt_contact = db.StringProperty()
  duration = db.IntegerProperty()
  post_time = db.IntegerProperty()
  expire_time = db.IntegerProperty()
  location_lat = db.FloatProperty()
  location_lon = db.FloatProperty()
  location_name = db.StringProperty()

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
  def get(self):
    vals={}
    # key = self.request.get('key')
    # if key:
    #   keyclass = Key(key)
    #   db.get(keyclass)
    #   self.redirect('/')
    template = JINJA_ENVIRONMENT.get_template('frontpage.html')
    self.response.write(template.render(vals))

  def post(self):
    vals = {}
    newpost = Request()
    newpost.name = self.request.get('name')
    newpost.gender = self.request.get('sex')
    newpost.what = self.request.get('description')
    newpost.phone = self.request.get('phone')
    newpost.opt_contact = ''
    opt = self.request.get('optional_contact')
    if opt:
      newpost.opt_contact = ', ' + opt
    newpost.duration = int(self.request.get('duration'))
    submit_time = int(datetime.datetime.now().strftime("%s")) * 1000
    newpost.post_time = submit_time
    newpost.expire_time = newpost.post_time+newpost.duration*1000
    newpost.location_lat = float(self.request.get('lat'))
    newpost.location_lon = float(self.request.get('lon'))
    newpost.location_name = self.request.get('location')
    newpost_key = newpost.put()
    # self.redirect('/?key=' + str(newpost_key))
    self.redirect('/')

class PostsHandler(webapp2.RequestHandler):
  def get(self):
    vals = {}
    posts = Request.all().order('-post_time')
    post_list = []
    ip = self.request.remote_addr
    logging.info(ip)
    # data = json.load(urllib2.urlopen('https://freegeoip.net/json/66.249.16.2'))
    # data = json.load(urllib2.urlopen('https://freegeoip.net/json/2601:602:8a02:5793:e07f:89be:be4a:f52d'))
    data = json.load(urllib2.urlopen('https://freegeoip.net/json/' + str(ip)))
    lon = data['longitude']
    lat = data['latitude']
    logging.info('location %s and %s',lon, lat)

    for each in posts:
      lon1, lat1, lon2, lat2 = map(radians, [lon, lat, each.location_lon, each.location_lat])
      dlon = lon2 - lon1 
      dlat = lat2 - lat1 
      a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
      c = 2 * asin(sqrt(a)) 
      km = 6367 * c
      logging.info(km)
      if each.expire_time > int(datetime.datetime.now().strftime("%s")) * 1000:
        # post_list.append(each)
        if km < 5.0:
          post_list.append(each)
    # vals['data'] = posts
    vals['data'] = post_list
    template = JINJA_ENVIRONMENT.get_template('results.html')
    self.response.write(template.render(vals))

application = webapp2.WSGIApplication([ \
                                      ('/', MainHandler),
                                      ('/posts', PostsHandler)
                                      ],
                                     debug=True)
#!/usr/bin/env python
#
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

from google.appengine.api import urlfetch
import webapp2
import urllib
import time
import json

import datetime
from google.appengine.ext import db
from google.appengine.api import users
  
class FundInfo(db.Model):
  fc = db.StringProperty(required=True, indexed=True)
  name = db.StringProperty(required=True)
  base = db.FloatProperty(indexed=False)
  units = db.FloatProperty(indexed=False)
  rate = db.FloatProperty(indexed=False)
  
class FundRecord(db.Model):
  fc = db.StringProperty(required=True, indexed=True)
  name = db.StringProperty(required=True)
  isredemptive = db.BooleanProperty(required=True)
  date = db.DateProperty(auto_now=True)
  base = db.FloatProperty(indexed=False)
  units = db.FloatProperty(indexed=False)
  rate = db.FloatProperty(indexed=False)

class DbIndex(webapp2.RequestHandler):
    def get(self):
        self.response.write('<html>')
        self.response.write("""
            <head>
                <style>
                table, th, td {
                    border: 1px solid black;
                    border-collapse: collapse;
                }
                th, td {
                    padding: 5px;
                    text-align: left;
                }
                table#t01 {
                    width: 100%;    
                    background-color: #f1f1c1;
                }
                </style>
            </head>
            """)
        self.response.write('<body>')
    
        funds = db.GqlQuery("SELECT * FROM FundInfo")
        self.response.out.write("""
            <table>
                <tr>
                    <th>fund code</th>
                    <th>fund name</th> 
                    <th>fund base</th>
                    <th>fund units</th>
                    <th>fund rate</th>
                    <th>Action</th>
                </tr>
            """)
        for fund in funds:
            self.response.out.write("""
                <tr>
                    <td>%s</td>
                    <td>%s</td>
                    <td><input type="text" disabled value="%f"></td>
                    <td>%f</td>
                    <td>%f</td>
                    <td><input type="button" value="Modify?"><input type="button" value="Delete?"></td>
                </tr>
            """ % (fund.fc, fund.name, fund.base, fund.units, fund.rate))
        self.response.out.write("""
        </table>
            """)
    
        self.response.out.write("""
        <form action="db/add" method="GET">
            <div>fund code:<input type="text" name="fc" value="000711"></div>
            <div>fund name:<input type="text" name="name" value="name 000711"></div>
            <div>fund base:<input type="text" name="base"></div>
            <div>fund units:<input type="text" name="units"></div>
            <div>fund rate:<input type="text" name="rate"></div>
            <div><input type="submit" value="Add new fund record"></div>
        </form>
          """ )
        self.response.write('</body>')
        self.response.write('</html>')
        
class DbRecord(webapp2.RequestHandler):
    def get(self):
        self.response.write('<html>')
        self.response.write('<head></head>')
        self.response.write('<body>')
    

        self.response.out.write("""
        <form action="db/rec/add" method="post">
            <div>fund code:<input type="text" name="fc" value="000711"></div>
            <div>fund name:<input type="text" name="name" value="fund  aaa"></div>
            <div>isredemptive:<input type="checkbox" name="isredemptive"></div>
            <div>fund date:<input type="date" name="date"></div>
            <div>fund base:<input type="text" name="base"></div>
            <div>fund units:<input type="text" name="units"></div>
            <div>fund rate:<input type="text" name="rate"></div>
            <div><input type="submit" value="Add a new fund record"></div>
        </form>
          """ )
        self.response.write('</body>')   
        self.response.write('</html>')
        
class Add(webapp2.RequestHandler):
    def get(self):
        fc = self.request.get('fc')
        name = self.request.get('name')
    
        funds = db.GqlQuery("SELECT * FROM FundInfo WHERE fc = :1", fc)
        for fund in funds:
            self.response.out.write("""
                <table>
                    <tr>
                        <th>fund code</th>
                        <th>fund name</th> 
                        <th>fund base</th>
                        <th>fund units</th>
                        <th>fund rate</th>
                    </tr>
                    <tr>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%f</td>
                        <td>%f</td>
                        <td>%f</td>
                    </tr>
                </table>
            """ % (fund.fc, fund.name, fund.base, fund.units, fund.rate))
            self.response.write('Add Failed: Record Exist!')
            return
    

        
        if self.request.get('base').isalnum():
            base = float(self.request.get('base'))
        else:
            base = 0.0
            
        if self.request.get('units').isalnum():
            units = float(self.request.get('units'))
        else:
            units = 0.0
            
        if self.request.get('rate').isalnum():
            rate = float(self.request.get('rate'))
        else:
            rate = 0.0

        
        #funds = db.GqlQuery("SELECT * FROM FundInfo WHERE fc = :1", fc)
        #for fund in funds:
        #    fund.delete()

        fund = FundInfo(key_name=fc,
                     fc=fc,
                     name=name,
                     base=base,
                     units=units,
                     rate=rate
                     )
        fund.put()
        

        self.response.write('Add/Update OK!')
        
class Delete(webapp2.RequestHandler):
    def get(self):
        self.response.write('not support!')
        
class DeleteAll(webapp2.RequestHandler):
    def get(self):
        funds = db.GqlQuery("SELECT * FROM FundInfo")
        for fund in funds:
            fund.delete()
        self.response.write('delete all success!')
        
class Query(webapp2.RequestHandler):
    def get(self):
        fc = self.request.get('fc')
        if fc is '':
            funds = db.GqlQuery("SELECT * FROM FundInfo")
            self.response.write("aaa")
        else:
            funds = db.GqlQuery("SELECT * FROM FundInfo WHERE fc = :1", fc)
            self.response.write(fc)
        for fund in funds:
            fc = fund.fc
            name = fund.name
            self.response.write("fc=%s, name=%s, base=%d, units=%d, rate=%f\n" % (fund.fc, fund.name, fund.base, fund.units, fund.rate))

app = webapp2.WSGIApplication([
    ('/db/?', DbIndex),
    ('/db/add', Add),
    ('/db/del', Delete),
    ('/db/delall', DeleteAll),
    #('/db/update', Update),
    ('/db/query', Query),
    ('/db/rec', DbRecord),
], debug=True)

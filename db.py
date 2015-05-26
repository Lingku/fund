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
  base = db.FloatProperty()
  units = db.FloatProperty()
  rate = db.FloatProperty()
  
class FundRecord(db.Model):
  fc = db.StringProperty(required=True, indexed=True)
  name = db.StringProperty(required=True)
  isredemptive = db.BooleanProperty(required=True)
  date = db.DateProperty(required=True, auto_now=True)
  base = db.FloatProperty(required=True)
  units = db.FloatProperty(required=True)
  rate = db.FloatProperty(required=True)

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
    
        funds = db.GqlQuery("SELECT * FROM FundInfo WHERE units > :1", 0.0)
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
          
        self.response.out.write("""
        <form action="db/addall" method="GET">
            <div>
                <textarea name="fundinfo"></textarea>
            </div>
            <div><input type="submit" value="Add new fund record"></div>
        </form>
          """ )
          
        self.response.out.write("""
        <form action="db/addrec" method="GET">
            <div>fund code:<input type="text" name="fc" value="000711"><input type="button" value="check fund code"></div>
            <div>fund name:<input type="text" name="name"></div>
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


def _add(fc, name):
    
    #todo: check fc first

    funds = db.GqlQuery("SELECT * FROM FundInfo WHERE fc = :1", fc)
    if funds.count() >= 1:
        return False

    base = 0.0
    units = 0.0
    rate = 0.0

    fund = FundInfo(key_name=fc,
                 fc=fc,
                 name=name,
                 base=base,
                 units=units,
                 rate=rate
                 )
    fund.put()

    return True
        
class Add(webapp2.RequestHandler):
    def get(self):
        fc = self.request.get('fc')
        name = self.request.get('name')
    
        funds = db.GqlQuery("SELECT * FROM FundInfo WHERE fc = :1", fc)
        for fund in funds:
            self.response.write('Add Failed: fc=%s Record Exist!' % (fund.fc, ))
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

        fund = FundInfo(key_name=fc,
                     fc=fc,
                     name=name,
                     base=base,
                     units=units,
                     rate=rate
                     )
        fund.put()

        self.response.write('Add/Update OK!')

class AddAll(webapp2.RequestHandler):
    def get(self):
        context = self.request.get('fundinfo')
        #self.response.write(fundinfo)
        fundinfos = json.loads(context)
        #self.response.write(fundinfo)
        for fundinfo in fundinfos:
            fc = fundinfo[0]
            name = fundinfo[2]
            if _add(fc, name) is False:
                self.response.write("Add fc=%s Failed<br>" % (fc, ))
        
class Update(webapp2.RequestHandler):
    def get(self):
        self.response.write('not support!')
        
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
            
        fc = self.request.get('fc')
        if fc is '':
            funds = db.GqlQuery("SELECT * FROM FundInfo")
        else:
            funds = db.GqlQuery("SELECT * FROM FundInfo WHERE fc = :1", fc)

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

        self.response.write('</body>')
        self.response.write('</html>')
        
class AddRecord(webapp2.RequestHandler):
    def get(self):
        pass

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
            
app = webapp2.WSGIApplication([
    ('/db/?', DbIndex),
    ('/db/add', Add),
    ('/db/addall', AddAll),
    ('/db/del', Delete),
    ('/db/delall', DeleteAll),
    ('/db/update', Update),
    ('/db/query', Query),
    ('/db/rec', DbRecord),
    ('/db/addrec', AddRecord),
], debug=True)

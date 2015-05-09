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

def handle_context(context):
    return context

def handle_result(rpc, response, fund_list):
    try:
        result = rpc.get_result()
    except urlfetch.DownloadError:
        #response.write('Oops! Timeout!')
        response.set_status(500)   # set as 500 Internal Server Error
        return
    
    status_code = result.status_code
    #response.write(status_code)
    if status_code != 200:
        response.write('Oops! Error Code: %d' % (status_code,))
        response.set_status(500)   # set as 500 Internal Server Error
        #return

    #response.set_status(500, "Error!")
    context = result.content
    #response.write(context[:-1])
    try:
        fund = eval(context[:-1])
    except TypeError:
        fund = {}
    fund_list.append(fund)
    #return fund
    #response.write(fund)
    #response.write(lambda : context)

# Use a helper function to define the scope of the callback.
def create_callback(rpc, response, fund_list):
    return lambda: handle_result(rpc, response, fund_list)

class FundIndex(webapp2.RequestHandler):
    def get(self):
        #cb = self.request.get('cb')
        fcs = self.request.get('fcs').split(',')
        timeout = float(self.request.get('timeout', default_value=5))
        url = 'http://fund.eastmoney.com/data/funddataforgznew.aspx'
        #url = 'http://fund.eastmoney.com/api/ZXZT.ashx?m=0&fcodes=213008,519069,163409,320012&fileds=FSRQ,&sortfile=FCODE&sorttype=asc&callback='

        rpcs = []
        fund_list = []
        #self.response.write(url)
        #self.response.write(fcs)

        for fc in fcs:
            #self.response.write("fc=%s, cb=%s, timeout=%f\n" % (fc, cb, timeout))
            form_fields = {
                't': 'basewap',
                'cb': handle_context.__name__,
                'fc': fc
            }
            form_data  = urllib.urlencode(form_fields)
            rpc = urlfetch.create_rpc(timeout)
            rpc.callback = create_callback(rpc, self.response, fund_list)
            urlfetch.make_fetch_call(rpc, url, payload=form_data, method=urlfetch.POST)
            rpcs.append(rpc)

        # ...
        #self.response.set_status(404)
        # Finish all RPCs, and let callbacks process the results.
        for rpc in rpcs:
            rpc.wait()
            
        #for fund in fund_list:
        self.response.write(fund_list)

app = webapp2.WSGIApplication([
    ('/fund', FundIndex),
    #('/fund/\d{6}', FundHandler)
], debug=True)

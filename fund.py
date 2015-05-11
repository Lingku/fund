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

def handle_result(rpc, response, fund_info, fc, request_type):
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
        return

    context = result.content
    #response.write(context)
    #return

    #fund = eval(context)
    fund = json.loads(context)

    if fc not in fund_info.keys():
        fund_info[fc] = {}
    
    if request_type == 'base':
        fund_info[fc]['fundcode'] = fund['fundcode']
        fund_info[fc]['name'] = fund['name']
        fund_info[fc]['gztime'] = fund['gztime'] and fund['gztime'] or fund['jzrq']
        fund_info[fc]['gsz'] = fund['gsz'] and fund['gsz'] or fund['dwjz']
        fund_info[fc]['gszzl'] = fund['gszzl'] and fund['gszzl'] or '0.00'
    elif request_type == 'gz':
        fund_info[fc]['gzdata'] = fund['gzdata']
    elif request_type == 'dwjznew':
        #fetch jzdata
        if fund['jzdata'] == 0:
            fund_info[fc]['jzdata'] = []
        if fund['jzdata'] == 1:
            fund_info[fc]['jzdata'] = [fund['jzdata'][-1].split(','), fund['jzdata'][-1].split(','), fund['jzdata'][-1].split(',')]
        elif fund['jzdata'] == 2:
            fund_info[fc]['jzdata'] = [fund['jzdata'][-1].split(','), fund['jzdata'][-2].split(','), fund['jzdata'][-2].split(',')]
        else:
            fund_info[fc]['jzdata'] = [fund['jzdata'][-1].split(','), fund['jzdata'][-2].split(','), fund['jzdata'][-3].split(',')]
    else:
        pass

# Use a helper function to define the scope of the callback.
def create_callback(rpc, response, fund_info, fc, request_type):
    return lambda: handle_result(rpc, response, fund_info, fc, request_type)

class FundIndex(webapp2.RequestHandler):
    def get(self):
        #cb = self.request.get('cb')
        fcs = self.request.get('fcs').split(',')
        timeout = float(self.request.get('timeout', default_value=5))
        url = 'http://fundex2.eastmoney.com/FundWebServices/FundDataForMobile.aspx'

        rpcs = []
        fund_info = {}
        #self.response.write(url)
        #self.response.write(fcs)
        
        for fc in fcs:
            form_fields = [
                # fetch fund info
                {
                    't': 'base',
                    'fc': fc,
                },
                ## fetch gz
                #{
                #    't': 'gz',
                #    'fc': fc,
                #    'rg': 'y',
                #    'rk': '3y',
                #},
                # fetch dwjz
                {
                    't': 'dwjznew',
                    'fc': fc,
                    'rg': 'y',
                    'rk': '3y',
                }
            ]
            for form_field in form_fields:
                #self.response.write("fc=%s, timeout=%f\n" % (fc, timeout))

                form_data = urllib.urlencode(form_field)
                rpc = urlfetch.create_rpc(timeout)
                rpc.callback = create_callback(rpc, self.response, fund_info, fc, form_field['t'])
                urlfetch.make_fetch_call(rpc, url, payload=form_data, method=urlfetch.POST)
                rpcs.append(rpc)


        #self.response.set_status(404)
        # Finish all RPCs, and let callbacks process the results.
        for rpc in rpcs:
            rpc.wait()
            
            
        #for fund in fund_list:
        self.response.write(json.dumps(fund_info))

app = webapp2.WSGIApplication([
    ('/fund', FundIndex),
    #('/fund/\d{6}', FundHandler)
], debug=True)

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
import webapp2
import urllib2
import urllib
import time

class FundIndex(webapp2.RequestHandler):
    def get(self):
        cb = self.request.get('cb')
        fc = self.request.get('fc')
        timeout = float(self.request.get('timeout'))

        #self.response.write("fc=%s, cb=%s, timeout=%s" % (fc, cb, timeout))

        url = 'http://fund.eastmoney.com/data/funddataforgznew.aspx'
        #url = 'http://fund.eastmoney.com/api/ZXZT.ashx?m=0&fcodes=213008,519069,163409,320012&fileds=FSRQ,&sortfile=FCODE&sorttype=asc&callback='
        params = urllib.urlencode({'t': 'basewap', 'cb': cb, 'fc': fc})

        try:
            time1 = time.time()
            f = urllib2.urlopen(url, params, timeout)
            
        except Exception, e:
            time2 = time.time()
            self.response.write("time1=%lf, time1=%lf, delta time=%lf\n" % (time1, time2, time2-time1))
            #self.response.write(e)
            self.response.write('Oops! Timeout!')
            self.response.set_status(500)   # set as 500 Internal Server Error
            return
        
        code = f.getcode()
        #self.response.write(code)
        if code != 200:
            self.response.write('Oops! Error Code: %d' % (code,))
            self.response.set_status(500)   # set as 500 Internal Server Error
            return

        #self.response.set_status(500, "Error!")
        context = f.read()
        self.response.write(context)

app = webapp2.WSGIApplication([
    ('/fund', FundIndex),
    #('/fund/\d{6}', FundHandler)
], debug=True)

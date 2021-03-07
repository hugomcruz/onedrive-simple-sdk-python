'''
------------------------------------------------------------------------------
 Copyright (c) 2021 Hugo Cruz - hugo.m.cruz@gmail.com
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
------------------------------------------------------------------------------
'''



class Payload:
    
    status_code = 0
    status_message = ""
    payload = None
    headers = None
    #
    # Class Initialization
    #
    def __init__(self, status_code, status_message, payload, headers=None):
        self.status_code = status_code
        self.status_message = status_message
        self.payload = payload
        self.headers = headers

    #
    # Getter - Status Code
    #
    def get_status_code(self):
        return self.status_code

    #
    # Getter
    #
    def get_status_message(self):
        return self.status_message

            #
    # Getter
    #
    def get_payload(self):
        return self.payload

    # Getter
    #
    def get_headers(self):
        return self.headers

    def get_header(self, key):
        test = dict(self.headers)
        return test[key]
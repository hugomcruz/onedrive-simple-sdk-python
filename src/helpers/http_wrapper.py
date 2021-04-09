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

# 
# Wrap HTTP Client Calls to Onedrive APIs
#

import os
import http.client
import json
import urllib.parse
import time
from .payload import Payload
import logging


RETRY_WAIT = 5


### HTTP GET - Wrap the entire requires
## DO NOT USE for very large download requests.
## For APIS whose payload is large enough to fit in the memory
def https_get(uri, headers='', body='', retry=3):
    logging.debug("http_get(): Starting")

    retry_count = 0
    
    url_data = urllib.parse.urlparse(uri)
    host = url_data.netloc
    path = url_data.path

    last_error = ""
 
    while(True):     
        try:
            connection = http.client.HTTPSConnection(host)
            connection.request("GET", path,  headers=headers, body=body)
            response = connection.getresponse()
            
            # Returned Headers
            headers = response.getheaders()
            data = response.read()
            
            reply = Payload(response.status, response.reason, data, headers=headers)
            
            connection.close()

            return reply
        except ConnectionResetError as ex1:
            retry_count = retry_count + 1
            logging.warning("http_get(): Connection Reset Error: %s", ex1)
            last_error = str(ex1)
            time.sleep(RETRY_WAIT)
        except Exception as e:
            retry_count = retry_count + 1
            logging.warning("http_get() General Error: %s", e)
            last_error = str(e)
            time.sleep(RETRY_WAIT)

        if(retry_count > retry):
            logging.error("http_get():Failed 3 times - Skipping URI: %s", uri)
            return Payload(0,last_error,"")




## HTTP POST
# Reads the entire reply to memory.f
def https_post(uri, headers, body, retry=3):
    retry_count = 0

    logging.debug("https_post(): Starting HTTPS POST")

    url_data = urllib.parse.urlparse(uri)
    host = url_data.netloc
    path = url_data.path    

    while(True):
        try:
            connection = http.client.HTTPSConnection(host)
            connection.request("POST", path,  headers=headers, body=body)
            response = connection.getresponse()
            data = response.read()
            reply = Payload(response.status, response.reason, data)
            connection.close()
            return reply
        except ConnectionResetError as ex1:
            retry_count = retry_count + 1
            logging.warn("https_post(): Connection Reset Error: %s", ex1)
            last_error = str(ex1)
            time.sleep(RETRY_WAIT)
        except Exception as e:
            retry_count = retry_count + 1
            logging.warn("https_post(): General Error: %s", e)
            last_error = str(e)
            time.sleep(RETRY_WAIT)

        if(retry_count > retry):
            logging.error("https_post(): Failed 3 times - Skipping URI: %s", uri)
            return Payload(0,last_error,"")



def https_put(uri, headers, body, retry=3):
    retry_count = 0

    logging.debug("https_put(): Starting HTTPS PUT")

    url_data = urllib.parse.urlparse(uri)
    host = url_data.netloc
    path = url_data.path

    while(True):
        try:
            connection = http.client.HTTPSConnection(host)
            connection.request("PUT", path,  headers=headers, body=body)
            response = connection.getresponse()
            data = response.read()
            reply = Payload(response.status, response.reason, data)
            connection.close()

            ## Transient error handling
            if(response.status == 503):
                retry_count = retry_count + 1
                logging.warn("https_put(): Got a 503 error. Retrying.")
            else:
                return reply
        except ConnectionResetError as ex1:
            retry_count = retry_count + 1
            logging.warning("https_put(): Connection Reset Error: %s", ex1)
            last_error = str(ex1)
            time.sleep(RETRY_WAIT)
        except Exception as e:
            retry_count = retry_count + 1
            logging.warning("https_put()General Error: %s", e)
            last_error = str(e)
            time.sleep(RETRY_WAIT)

        if(retry_count > retry):
            logging.error("https_put(): Failed 3 times - Skipping URI: %s", uri)
            return Payload(0,last_error,"")


def https_patch(uri, headers, body):
    logging.error("https_patch(): Not implemented")
    return None


def https_delete(uri, headers='', body=''):
    logging.debug("https_delete(): Starting HTTP DELETE")
    
    url_data = urllib.parse.urlparse(uri)
    host = url_data.netloc
    path = url_data.path

    connection = http.client.HTTPSConnection(host)
    connection.request("DELETE", path,  headers=headers, body=body)
    response = connection.getresponse()
    return response


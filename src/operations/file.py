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


from helpers.http_wrapper import https_get
from helpers.payload import Payload
import json
import time
import logging

URL_TEMPLATE = "https://graph.microsoft.com/v1.0/me/drive/root:{0}"

RETRY_WAIT = 5 #In case of potentially recoverable error the time lapse between tries

## This will list all the files
def file_details(path, headers):
    logging.debug("file_details(): Starting list files operation...")
    
    uri = URL_TEMPLATE.format(path)
    
    logging.debug("file_details(): File details for file: %s",path)
    
    # To test unauthorized request
    #headers = {"Authorization" :"bearer dummy", "Content-Type" : "application/json"}

    response = https_get(uri, headers=headers)
    
    logging.debug("listfiles(): Status: {} and reason: {}".format(response.get_status_code(), response.get_status_message()))


    ## Sucessfull response - Lets process it
    if(response.get_status_code() == 200):
        data_parsed = json.loads(response.get_payload())

        #print(data_parsed)

        return {"status": True,
                "size": data_parsed["size"],
                "id": data_parsed["id"],
                "sha256hash": data_parsed["file"]["hashes"]["sha256Hash"]
        }

    # File Not found
    elif(response.get_status_code() == 404):
        return { "status": False, 
                "message": "File not found"
                }



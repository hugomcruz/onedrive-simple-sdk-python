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

from helpers.http_wrapper import https_delete
import logging

URL_TEMPLATE =  "https://graph.microsoft.com/v1.0/me/drive/items/root:{0}:/"

def delete(file_path,headers):
    logging.debug("delete(): Starting delete...")
    uri = URL_TEMPLATE.format(file_path)
    response = https_delete(uri, headers=headers)
    
    logging.debug("delete(): Status: {} and reason: {}".format(response.status, response.reason))

    ## Error and response handling
    if(response.status == 204):
        return {    
                "status": True,
                "message":"File deleted successfuly"
                }
    else:
        return {    
                "status": False,
                "message": response.reason
                }

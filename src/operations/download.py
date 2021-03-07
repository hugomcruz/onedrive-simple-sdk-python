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
import os
import time
import http.client
import urllib.parse
import logging

URL_TEMPLATE =  "https://graph.microsoft.com/v1.0/me/drive/root:{0}:/content"

RETRY_WAIT = 5

def download(file_path,local_path, headers, retry=3):
    logging.debug("download(): Starting download operation...")
    
    file_path_quoted = urllib.parse.quote(file_path)
    uri = URL_TEMPLATE.format(file_path_quoted)
    retry_count = 0


    ## variables needed globaly
    location = ""

    ### First API call to return the download URL
    while(True):
        try:
            
            filename = os.path.basename(file_path)
            logging.debug("download(): Filename to download: %s",filename)
            
            response = https_get(uri, headers=headers)
            logging.debug("download(): Status 1: {} and reason: {}".format(response.get_status_code(), response.get_status_message()))
            
            
            # Success Status: 302 - Redirect with Location
            # Status: 404 and reason: Not Found
            if(response.get_status_code() == 404):
                return {
                    "status": False, 
                    "message": "File not found."
                }
            
            if(response.get_status_code() != 302):
                return {
                    "status": False, 
                    "message": response.get_status_message()
                }


            # Retrieve the download URL
            location = response.get_header("Location")

            logging.debug("download(): Redirect link to download: %s", location)


            break
            
        
        except Exception as ex2:
            logging.warning("download(): Exception caught: %s - Retry mode routine is continuing.", ex2)
            retry_count = retry_count + 1

        if(retry_count > 3):
            logging.error("download(): Maximum retried exceeded. Download was not completed.")
            return {
                    "status": False, 
                    "message": "Maximum retried exceeded. Download was not completed."
                }
            
         

    ## Second API call to download the entire file
    while(True):     
        try:
            url_data = urllib.parse.urlparse(location)
            host = url_data.netloc
            
            connection = http.client.HTTPSConnection(host)
            connection.request("GET", location,  headers=headers)
            response = connection.getresponse()
            
            #reply = Payload(response.status, response.reason, data)
            #connection.close()

            logging.debug("download(): Status 2: {} and reason: {}".format(response.status, response.reason))

            if(response.status == 200):

                # Status: 200 and reason: OK
                # Status: 404 and reason: Not Found - This is probably hard to happen

                #Open the file to write the download
                f = open(filename, "wb")

                #Download and write in chunks -- FIX Here... Needs a connection reset treatment too. Lot of content data being retrived. 
                # REVIEW THE CHUNK SIZE - 10KB for now

                logging.debug("download(): Download Started.")

                while chunk := response.read(1024*10):
                    f.write(chunk)
                f.close()
                connection.close()
                logging.debug("download(): Download Completed.")

                break
            if(response.status == 503):

                #  503 and reason: Service Unavailable
                retry_count = retry_count + 1
                logging.warning("download(): Server response is Service Unavailabe. Preparing retry")
                time.sleep(RETRY_WAIT)
            else:
                logging.error("download(): UNEXPECTED ERROR. Code: {} and reason: {}".format(response.status, response.reason))
                return {    
                    "status": False,
                    "message":"UNEXPECTED ERROR. Status : {} and reason: {}".format(response.status, response.reason)
                }



        except ConnectionResetError as ex1:
            retry_count = retry_count + 1
            logging.warning("download(): Connection Reset Error: %s", ex1)
            last_error = str(ex1)
            time.sleep(RETRY_WAIT)
        except Exception as e:
            retry_count = retry_count + 1
            logging.warning("download() General Error: %s", e)
            last_error = str(e)
            time.sleep(RETRY_WAIT)

        if(retry_count > retry):
            logging.error("download():Failed 3 times - Skipping URI: %s", uri)
            return {    
                "status": False,
                "message":"Failed after 3 retries."
                }



    

        
    
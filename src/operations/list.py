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


### NOTES TODO
# - Need to simulate a 503 error as the code has not been tested

from helpers.http_wrapper import https_get
from helpers.payload import Payload
import json
import time
import logging

URL_TEMPLATE = "https://graph.microsoft.com/v1.0/me/drive/root:{0}:/children"

RETRY_WAIT = 5 #In case of potentially recoverable error the time lapse between tries

## This will list all the files
def listfiles(path, headers):
    logging.debug("listfiles(): Starting list files operation...")
    
    uri = URL_TEMPLATE.format(path)
    
    logging.debug("listfiles(): Listing Remote Path: %s",path)

    page_number = 0
    retry_count=0

    item_list = list()

    ## Loop until there are further pages
    while(True):
        
        response = https_get(uri, headers=headers)
    
        # Used to simulate very rare error
        #if(page_number == 1 and retry_count == 0):
        #    response = Payload(503, "Simulation Error","")

        logging.debug("listfiles(): Status: {} and reason: {}".format(response.get_status_code(), response.get_status_message()))


        ## Sucessfull response - Lets process it
        if(response.get_status_code() == 200):
            retry_count=0
            page_number = page_number + 1

            data_parsed = json.loads(response.get_payload())

            logging.debug("listfiles() - Page Number: %s", page_number)
            # In some uders the odata cound does not exit. 
            # Using the array count to obtain the number of elements.
            #number_items = data_parsed["@odata.count"]
            number_items = len(data_parsed["value"])
            logging.debug("listfiles() - Total Items: %s", number_items)

            next_link = None

            if('@odata.nextLink' in data_parsed.keys()):
                next_link = data_parsed["@odata.nextLink"]
                logging.debug("listfiles() - THERE ARE ADDITIONAL PAGES. Next link: %s", next_link)
                
            else:
                logging.debug("listfiles() - no further pages")
                next_link = None

            ## Mapping just the relevant fields
            for item in data_parsed["value"]:
                created_date_time = item["createdDateTime"]
                last_modified_datetime = item["lastModifiedDateTime"]
                ctag = item["cTag"]
                etag = item["eTag"]
                item_id = item["id"]
                name = item["name"]
                item_type = ""  # folder/file
                size = 0 #only return size for files

                #Determine item type for the listing
                if("folder" in item):
                    item_type = "folder"
                    
                if("file" in item):
                    item_type = "file"
                    size = item["size"]

                item_data= { "type": item_type,
                            "id": item_id,
                            "name": name,
                            "size": size,
                            "ctag": ctag,
                            "etag": etag,
                            "created": created_date_time,
                            "lastmodified": last_modified_datetime
                }
                item_list.append(item_data)

            logging.debug("listfiles(): Page completed: %s", page_number)

            #Check if we exit the paging when it ends or not
            if(next_link == None):
                logging.debug("listfiles(): Total number of items returned: %s", len(item_list))
                return { "status":True,
                        "message":"Success",
                        "itemlist":item_list
                }
            else:
                uri = next_link #Prepare the URL for the next page


        # Status: 503 and reason: Service Unavailable
        # This is a recoverable error.  
        elif(response.get_status_code() == 503):
            retry_count = retry_count + 1
            time.sleep(RETRY_WAIT) #Sleep 5 seconds before retry
            logging.warn("listfiles(): 503 Error - Sleeping 5 seconds and retrying")

        ## The specified path does not exist
        elif(response.get_status_code() == 404):
            return {    
                    "status": False,
                    "message":"Path not found."
                }

        elif(response.get_status_code() == 401):
            return {    
                    "status": False,
                    "message":"Unauthorized."
                }
           
        # There were exceptions on the http which exceeded the interval between retried and we had to abort. 
        elif(response.get_status_code() == 0):
            return {    
                    "status": False,
                    "message":response.get_status_message()
                }
        else:
            return {    
                    "status": False,
                    "message": response.get_status_message()
                }

        if(retry_count > 3):
            return {    
                    "status": False,
                    "message":"Failure after number of retries exceeded"
                }

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

from helpers.http_wrapper import https_post
from helpers.http_wrapper import https_put
import json
import os
import time
import urllib.parse
import logging

URL_MULTIPART_CREATE_SESSION = "https://graph.microsoft.com/v1.0/drive/root:{}:/createUploadSession"
URL_DIRECT_UPLOAD = "https://graph.microsoft.com/v1.0/me/drive/items/root:{}:/content"

# CONSTANTS
UPLOAD_MULTIPART_THRESHOLD = 0 #Threshold set to ZERO temporary. Need to check on confict on direct upload. 
FILE_DOWNLOAD_BUFFER = 1024*10
MULTIPART_UPLOAD_CHUNK = 1024 * 1024 * 5  #Probably create a dynamic chunk size depending on the size of the file. 
LOCAL_WRITE_CHUNCK = 1024*10

def upload(local_file, destination_path, headers='', exists='fail'):
    logging.debug("upload(): Starting upload operation...")

    # Get the size of the file to upload.
    # This is important as files < 4MB will not use multi-part upload
    stat = os.stat(local_file)
    size = stat.st_size

    destination_path_quoted = urllib.parse.quote(destination_path)

    # Get the file name from the full path
    original_file = os.path.basename(local_file)
    original_file_quoted = urllib.parse.quote(original_file)

    # Condition to decide the type of upload:
    # File < 5MB - direct single upload
    # File > 5MB - multi part upload
    if(size > UPLOAD_MULTIPART_THRESHOLD):
        #Multipart upload
        logging.debug("File is larger then theshold. Starting multipart upload.")

        #Create a Multipart Upload Session
        uri = URL_MULTIPART_CREATE_SESSION.format(destination_path_quoted + "/" + original_file_quoted)
                        
        
        body = {
                    "item": {
                    "@odata.type": "microsoft.graph.driveItemUploadableProperties",
                    "@microsoft.graph.conflictBehavior": exists,
                    "name": original_file
                    }
                }
        body_str = json.dumps(body)

        response = https_post(uri,  headers=headers, body=body_str)
        
        logging.debug("upload(): Multipart create upload session - Status: {} and reason: {}".format(response.get_status_code(), response.get_status_message()))

        # Code 200: The upload URL was returned and it is good. 
        if(response.get_status_code() == 200):
            data_parsed = json.loads(response.get_payload())

            # In the first request to create upload session we get the URL for the upload
            # Retrieve the URL to send the second request
            multipart_upload_url = data_parsed["uploadUrl"]
        
            logging.debug("Multipart Upload URL: %s", multipart_upload_url)
                  
            # Control variable for the bytes transfered  
            low_range=0


            # For statistics
            timeBefore = time.time()

            with open(local_file, "rb") as f:
                while True:
                    chunk = f.read(MULTIPART_UPLOAD_CHUNK)
                    if chunk:
                        high_range = low_range + len(chunk) -1 

                        range = "bytes " + str(low_range) +"-" + str(high_range) + "/" +str(size)
                            
                        headers = {"Content-Range": range}
                        low_range = low_range + MULTIPART_UPLOAD_CHUNK

                        chunk_response = https_put(multipart_upload_url, headers=headers, body=chunk)
                                
                        logging.debug("upload(): Chunk upload -  Status: {} and reason: {}".format(chunk_response.get_status_code(), chunk_response.get_status_message()))
                        
                        if(chunk_response.get_status_code() == 202):
                            logging.debug("upload(): File CHUNK upload completed")
                        elif(chunk_response.get_status_code() == 201):
                            logging.debug("upload(): File upload completed")

                        if(chunk_response.get_payload() == None):
                            logging.error("Something is wrong. Response payload was null.")
                            
                            f.close() #Close the file gracefuly
                            
                            return {    
                                "status": False,
                                "message":"Somethig is unexpected"
                                }
                           

                        dataParsed = json.loads(chunk_response.get_payload())
                        #prin(dataParsed) 
                    else:
                        break

            f.close()

            timeAfter = time.time()
            uploadTime = timeAfter - timeBefore

            logging.debug("upload(): Total time to upload: %s", uploadTime)

            return {
                "status": True,
                "message": "File Upload success. More details about upload coming in next releases."
            }

        
        # Conflict - File exists
        elif(response.get_status_code() == 409):
            return {    
                    "status": False,
                    "message":"File already exists. Solve conflict by changing upload policy from 'fail' to other."
                    }
        else:
            logging.error("upload(): Unexpected error -  Status: {} and reason: {}".format(response.get_status_code(), response.get_status_message()))
            
            return {    
                    "status": False,
                    "message":"Unexpected error. "
                    } 


    else:
        #Single Direct upload
        logging.debug("File is smaller then theshold. Starting direct upload.")

        uri = URL_DIRECT_UPLOAD.format(destination_path_quoted + "/" + original_file_quoted)
 
        #Open file
        f = open(local_file,"rb")
        content = f.read()

        response = https_put(uri, headers=headers, body=content)
        f.close()

        logging.debug("upload(): Direct upload - Status: {} and reason: {}".format(response.get_status_code(), response.get_status_message()))

        ### Add here ERROR HANDLING INFO] upload(): Status: 409 and reason: Conflict
        if(response.get_status_code() == 200):
            data_parsed = json.loads(response.get_payload())

            return {
                "status": True,
                "message": "File Upload success. More details about upload coming in next releases."
            }
        elif(response.get_status_code() == 409):
            return {    
                    "status": False,
                    "message":"File already exists. Solve conflict by changing upload policy from 'fail' to other."
                    }
        elif(response.get_payload() == None):
            logging.error("Something is wrong. Response payload was null.")
                                         
            return {    
                "status": False,
                "message":"Somethig is unexpected as return payload should not be Null"
                }
        else:
            logging.error("upload(): Something is wrong. We should not have gotten here.")
                                         
            return {    
                "status": False,
                "message":"Something went very wrong. We should not have gottent here."
                }


        


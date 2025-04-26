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


import os
import http.client
import json
import urllib.parse
import time
import logging
from operations.delete import delete
from operations.list import listfiles
from operations.download import download
from operations.upload import upload
from operations.file import file_details

class onedrive_simple_sdk:
    
    #Other Constants
    UPLOAD_MULTIPART_THRESHOLD = 1024*1024 #1MB threshold
    FILE_DOWNLOAD_BUFFER = 1024*10
    MULTIPART_UPLOAD_CHUNK = 1024 * 1024 * 50  #Probably create a dynamic chunk size depending on the size of the file. 
    LOCAL_WRITE_CHUNCK = 1024*10


    ##### CONSTANTS
    AUTH_URI = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
    AUTH_HOST = "login.microsoftonline.com"
    AUTH_PATH = "/consumers/oauth2/v2.0/token"

    GRAPH_HOST = "graph.microsoft.com"


    #Client Items
    clientID = ""
    clientSecret = ""
    grantType = "refresh_token" 
 
    refresh_token_str = ""


    ### Access Token Data
    token_type = ""
    scope = ""
    expires_in = 0
    ext_expires_in = 0
    access_token = ""
    refresh_token = ""
    tokenIssueTimestamp = 0
    tokenIssueExpiry = 0


    #### Onde Drive Profile
    driveId = ""
    driveType = ""
    ownerDisplayName = ""
    ownerId = ""
    quotaDeleted = ""
    quotaRemaining = ""
    quotaState = ""
    quotaTotal = ""
    quotaUsed = ""




    #
    # Class Initialization
    #
    def __init__(self, clientID, clientSecret, refresh_token_str):
        self.refresh_token_str = refresh_token_str
        self.clientID = clientID
        self.clientSecret = clientSecret

        logging.info("OneDrive - Initialized")
        
        self.refreshToken()
        self.getMyProfile()
        


    #
    # Refresh Token 
    #
    def refreshToken(self):
        
        logging.debug("refreshToken() Refreshing Token")
        connection = http.client.HTTPSConnection(self.AUTH_HOST)
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        
        params = {  "client_id": self.clientID,
                    "client_secret": self.clientSecret,
                    "refresh_token": self.refresh_token_str,
                    "grant_type": self.grantType}
        paramsData = urllib.parse.urlencode(params)
        connection.request("GET", self.AUTH_PATH, body=paramsData, headers=headers)
        

        response = connection.getresponse()
        #print("Status: {} and reason: {}".format(response.status, response.reason))
    
        data = response.read()
        connection.close()

        dataParsed = json.loads(data)


        self.token_type = dataParsed["token_type"]
        self.scope = dataParsed["scope"]
        self.expires_in = dataParsed["expires_in"]
        self.ext_expires_in = dataParsed["ext_expires_in"]
        self.access_token = dataParsed["access_token"]
        self.refresh_token = dataParsed["refresh_token"]

        self.tokenIssueTimestamp = int(time.time())
        self.tokenIssueExpiry = self.tokenIssueTimestamp + self.expires_in


    def getMyProfile(self):
        PROFILE_PATH = "/v1.0/me/drive"
        connection = http.client.HTTPSConnection(self.GRAPH_HOST)
        headers = {"Authorization": self.token_type + " " + self.access_token}
        connection.request("GET", PROFILE_PATH,  headers=headers)
        

        response = connection.getresponse()
        #print("Status: {} and reason: {}".format(response.status, response.reason))

        data = response.read()
        dataParsed = json.loads(data)

        self.driveId = dataParsed["id"]
        self.driveType = dataParsed["driveType"]
        self.ownerDisplayName = dataParsed["owner"]["user"]["displayName"]
        #self.ownerId = dataParsed["owner"]["user"]["id"]
        self.quotaDeleted = dataParsed["quota"]["deleted"]
        self.quotaRemaining = dataParsed["quota"]["remaining"]
        self.quotaState = dataParsed["quota"]["state"]
        self.quotaTotal = dataParsed["quota"]["total"]
        self.quotaUsed = dataParsed["quota"]["used"]



    def printMyProfile(self):
        print("------ > Profile Data")
        print("Drive ID    :", self.driveId)
        print("Drive Type  : " + self.driveType)
        print("Display Name: " + self.ownerDisplayName)
        #print("Owner ID    : " + self.ownerId)
        print("> Quota:") 
        print("Deleted  :", self.quotaDeleted)
        print("Remaining:", self.quotaRemaining)
        print("State    :",self.quotaState)
        print("Total    :",self.quotaTotal)
        print("Used     :",self.quotaUsed)
        print()


    def printTokenData(self):
        print("------ > Token Data")
        print("Token Type:", self.token_type)
        print("Scope     : " + self.scope)
        print("Access Token: " + self.access_token)
        print("Refresh Token: " + self.refresh_token)
        print("> Token Expiry") 
        print("Token Issues TS:", self.tokenIssueTimestamp)
        print("Token Expiry TS:", self.tokenIssueExpiry)

        tokenExpiringInSeconds = self.tokenIssueExpiry - int(time.time())

        print("Expires in (s) :", tokenExpiringInSeconds)
        print()


    def listfiles(self,path):
        self.checkExpiredToken()
        headers = {"Authorization": self.token_type + " " + self.access_token, "Content-Type" : "application/json"}
        path = urllib.parse.quote(path)
        result = listfiles(path,headers)
        return result

    

    def filedetails(self, path):
        self.checkExpiredToken()
        headers = {"Authorization": self.token_type + " " + self.access_token, "Content-Type" : "application/json"}
        path = urllib.parse.quote(path)
        result = file_details(path, headers)
        return result


    def download(self, file_path, local_path):
        self.checkExpiredToken()
        headers = {"Authorization": self.token_type + " " + self.access_token, "Content-Type" : "application/json"}
        result = download(file_path,local_path, headers)
        return result



    def upload(self, local_file, destination_path):
        self.checkExpiredToken()
        headers = {"Authorization": self.token_type + " " + self.access_token, "Content-Type" : "application/json"}
        result = upload(local_file, destination_path, headers=headers)
        return result


    def rename(self, filePathOriginal, filePathDestination):
        loggin.error("rename(): Operation is not implemented")
        return None


    def move(filePathOriginal, filePathDestination):
        loggin.error("move(): Operation is not implemented")
        return None


    def copy(filePathOriginal, filePathDestination):
        loggin.error("copy(): Operation is not implemented")
        return None


    def delete(self,file_path):
        self.checkExpiredToken()
        headers = {"Authorization": self.token_type + " " + self.access_token, "Content-Type" : "application/json"}
        file_path = urllib.parse.quote(file_path)
        result = delete(file_path, headers)
        return result


    def checkExpiredToken(self):
        tokenExpiringInSeconds = self.tokenIssueExpiry - int(time.time())
        if(tokenExpiringInSeconds < 5):
            self.refreshToken()


    


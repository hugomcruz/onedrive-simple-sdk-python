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

import sys
import os
import time
import json
import datetime

from onedrive import onedrive_simple_sdk


##### TEMPORARY TO HELP DEBUG
def pretty_print(obj):
    #Pretty print
    json_formatted_str = json.dumps(obj, indent=2)
    print(json_formatted_str)


def cli_print(result):
    print("cli_print(): Total records to print today is:",len(result))
    for item in result:
        date_str = dateConvert(item["created"])
        if(item["type"]=="folder"):
            print("d---------", date_str, item["size"],item["name"])
        else:
            print("----------",  date_str, item["size"], item["name"])



def dateConvert(date_str):
    date_time_obj = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    date_output = date_time_obj.strftime("%Y-%m-%d %H:%M:%SZ")

    return date_output



#### Define here as the main part

if(len(sys.argv) != 2):
    print("Wrong Arguments!")
    print("Usage:")
    print(sys.argv[0] + " <onedrive path>")
else:
    #### ---- ####
    
    ## Read the configuration file with the IDs and refresh tokens.
    with open('credentials.json') as json_file:
        data = json.load(json_file)
        refreshToken = data["refreshToken"]
        clientSecret = data["clientSecret"]
        clientID = data["clientID"]

        # Create the Onedrive SDK object
        client = onedrive_simple_sdk(clientID, clientSecret, refreshToken)


        #Upload the data
        result =  client.listfiles(sys.argv[1])

        cli_print(result)
       
        #pretty_print(result)





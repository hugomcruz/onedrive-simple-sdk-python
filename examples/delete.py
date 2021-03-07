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
sys.path.append('/Users/hcruz/Documents/development/python/onedrive_simple_sdk/src')
sys.path.append('/root/dev/onedrive_simple_sdk/src')

import os
import time
import json

from onedrive import onedrive_simple_sdk


##### TEMPORARY TO HELP DEBUG
def pretty_print(obj):
    #Pretty print
    json_formatted_str = json.dumps(obj, indent=2)
    print(json_formatted_str)


def cli_print(result):
    print("cli_print(): Total records to print today is:",len(result))
    for item in result:
        if(item["type"]=="folder"):
            print("d---------", item["size"], item["created"],item["name"])
        else:
            print("---------", item["size"], item["created"],item["name"])


#### Define here as the main part

if(len(sys.argv) != 2):
    print("Wrong Arguments!")
    print("Usage:")
    print(sys.argv[0] + " <onedrive file path>")
else:
    #### ---- ####
    
    ## Read the configuration file with the IDs and refresh tokens.
    with open('credentials_hugo.json') as json_file:
        data = json.load(json_file)
        refreshToken = data["refreshToken"]
        clientSecret = data["clientSecret"]
        clientID = data["clientID"]

        # Create the Onedrive SDK object
        client = onedrive_simple_sdk(clientID, clientSecret, refreshToken)


        #Upload the data
        result =  client.delete(sys.argv[1])

        print(result)
        #cli_print(result)
       
        #pretty_print(result)





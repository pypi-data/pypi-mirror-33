#!/usr/bin/env python

import os
import sys
import time
import socket
import requests
import json
import subprocess
import urllib3
import urllib3.contrib.pyopenssl
from urllib3.exceptions import HTTPError as BaseHTTPError
import certifi
sys.path.append('/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell')
import traceback
import azure_dbg as dbg


# Specify files accessed by this script in guestshell
get_response_file = "/home/guestshell/azure/tools/TokenMgr/token_get_rsp"
at_file = "/home/guestshell/azure/tools/TokenMgr/at_command_file"
debug_file = "/home/guestshell/azure/tools/TokenMgr/tokenMgr.log"
sock_file = "/home/guestshell/azure/tools/TokenMgr/sock_file"
cert_file = "/etc/ssl/certs/ca-bundle.trust.crt"

msi_dir = "/var/log/azure/Microsoft.ManagedIdentity.ManagedIdentityExtensionForLinux"
msi_service_file = "/etc/systemd/system/azuremsixtn.service"

token = ''


def aad_get_token(debug_fh, cloud, tenantId, appId, appKey):

    if cloud == 'azure':
        url = "https://login.microsoftonline.com/%s/oauth2/token?api-version=1.1" % tenantId
        payload = {'grant_type' : 'client_credentials',
                   'client_id' : appId,
                   'resource' : 'https://management.core.windows.net/',
                   'client_secret' : appKey}

    elif cloud == 'azusgov':
        url = "https://login-us.microsoftonline.com/%s/oauth2/token?api-version=1.1" % tenantId
        payload = {'grant_type' : 'client_credentials',
                   'client_id' : appId,
                   'resource' : 'https://management.core.usgovcloudapi.net/',
                   'client_secret' : appKey}
    else:
        dbg.log(debug_fh, 'ERR', "Server: aad_get_token: invalid cloud name %s" % cloud)
        return ''

    # Specify the HTTP POST request to obtain a token
    all_headers = {'Content-Type':'application/x-www-form-urlencoded',
                   'Accept':'accept:application/json',
                   'Authorization':'OAuth 2.0'}

    # Send the HTTP POST request for the token
    try:
        response = requests.post(url, data=payload, verify=cert_file, headers=all_headers)
    except requests.exceptions.RequestException as e:
        dbg_log(debug_fh, "Server: aad_get_token: request had error %s" % e)
        return ''
        
    if 200 != response.status_code :
        dbg.log(debug_fh, 'ERR', "Server: aad_get_token: request failed rc=%d" % response.status_code)
        with open(get_response_file, 'wb') as token_fh:
            for chunk in response.iter_content(chunk_size=64):
                token_fh.write(chunk)
        return ''

    # Parse the HTTP GET response
    try:
        token = response.json()["access_token"]
        dbg.log(debug_fh, 'INFO', "Server: aad_get_token: obtained token")

        # Schedule a job to invalidate this token
        command = "/usr/bin/at -f %s now + %d minutes" % (at_file, 5)
        os.system(command)

    except Exception as e:
        dbg.log(debug_fh, 'ERR', "Server: aad_get_token: caught exception %s" % e)
        tb = traceback.format_exc()
        dbg.log(debug_fh, 'ERR', "%s" % tb)
        token = ''

    return token



def msi_get_token_by_http(debug_fh):
    # Specify the HTTP GET request to obtain a token
    url      = "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01"
    payload  = {'resource':'https://management.azure.com/'}
    header   = {'Metadata':'true'}

    # Send the HTTP GET request for the token
    try:
        response = requests.get(url, params=payload, verify=False, headers=header)
    except requests.exceptions.RequestException as e:
        dbg_log(debug_fh, "Server: msi_get_token: request had error %s" % e)
        return ''

    if 200 != response.status_code :
        dbg.log(debug_fh, 'ERR', "Server: msi_get_token: request failed rc=%d" % response.status_code)
        with open(token_file, 'w') as token_fh:
            token_fh.write(response.json())
        return ''

    # Parse the HTTP GET response
    try:
        token = response.json()["access_token"]
        dbg.log(debug_fh, 'INFO', "Server: msi_get_token: obtained token")

        # Schedule a job to invalidate this token
        command = "/usr/bin/at -f %s now + %d minutes" % (at_file, 5)
        os.system(command)

    except Exception as e:
        dbg.log(debug_fh, 'ERR', "Server: msi_get_token: caught exception %s" % e)
        tb = traceback.format_exc()
        dbg.log(debug_fh, 'ERR', "%s" % tb)
        token = ''
    
    return token


def msi_get_token_by_extension(debug_fh):

    # Check if user has successfully installed the Managed Identity Extension
    if not os.path.exists(msi_dir):
        # Directory does not exist.  Don't use MSI
        dbg.log(debug_fh, 'INFO', "Server: msi_get_token: MSI not installed")
        return ''

    # Check if the MSI service is running
    try:
        subprocess.check_output("pgrep -f msi-extension", shell=True)
    except:
        # Check if the Managed Identity Extension has been installed
        if os.path.exists(msi_service_file):
            # File has been installed.  Try to start the service.
            os.system("sudo systemctl enable azuremsixtn")
            os.system("sudo systemctl start azuremsixtn")
            dbg.log(debug_fh, 'INFO', "Server: msi_get_token: started MSI service")
        else:
            # Directory does not exist.  Don't use MSI
            dbg.log(debug_fh, 'INFO', "Server: msi_get_token: MSI not installed")
            return ''

    # Specify the HTTP GET request to obtain a token
    url      = "http://localhost:50342/oauth2/token"
    payload  = {'resource':'https://management.azure.com/'}
    header   = {'Metadata':'true'}

    # Send the HTTP GET request for the token
    response = requests.get(url, params=payload, verify=False, headers=header)

    if 200 != response.status_code :
        dbg.log(debug_fh, 'ERR', "Server: msi_get_token: request failed rc=%d" % response.status_code)
        with open(token_file, 'w') as token_fh:
            token_fh.write(response.json())
        return ''

    # Parse the HTTP GET response
    token = response.json()["access_token"]
    dbg.log(debug_fh, 'INFO', "Server: msi_get_token: obtained token")

    # Schedule a job to invalidate this token
    command = "/usr/bin/at -f %s now + %d minutes" % (at_file, 5)
    os.system(command)

    return token


# Find out the process ID
pid = os.getpid()

# Open the debug log file
debug_fh = open(debug_file, "a", os.O_NONBLOCK)
dbg.log(debug_fh, 'INFO', "Token server started, pid=%d" % pid)

# Make sure the socket does not already exist
try:
    os.unlink(sock_file)
except OSError:
    if os.path.exists(sock_file):
        raise

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind the socket to the port
sock.bind(sock_file)

# Use OpenSSL to check certificates for https
urllib3.contrib.pyopenssl.inject_into_urllib3()

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    connection, client_address = sock.accept()
    try:
        while True:
            # Read a command from the client
            line = connection.recv(255)
            if line == '':
                break
            
            command = line.rsplit(' ')
            if command[0] == "MSI_req":
                if token == '':
                    # Get a new token
                    token = msi_get_token_by_http(debug_fh)
                else:
                    dbg.log(debug_fh, 'INFO', "Server: MSI_req: using cached token")

                # Send the number of bytes in the token
                token_len = len(token)
                token_len_as_str = str(token_len) + ' '
                connection.sendall(token_len_as_str)
  
                # Send the token
                if token != '':
                    connection.sendall(token)
                else:
                    dbg.log(debug_fh, 'ERR', "Server: no token returned by MSI")

            elif command[0] == "AAD_req":
                if token == '':
                    # Get a new token
                    token = aad_get_token(debug_fh, command[1], command[2], command[3], command[4])
                else:
                    dbg.log(debug_fh, 'INFO', "Server: AAD_req: using cached token")

                # Send the number of bytes in the token
                token_len = len(token)
                token_len_as_str = str(token_len) + ' '
                connection.sendall(token_len_as_str)
  
                # Send the token
                if token != '':
                    connection.sendall(token)
                else:
                    dbg.log(debug_fh, 'ERR', "Server: no token returned by AAD")

            elif command[0] == "Clear":
                dbg.log(debug_fh, 'INFO', "Token cleared")
                token = ''
                connection.sendall("OK")

            elif command[0] == "Ping":
                connection.sendall("Ack")

            else:
                dbg.log(debug_fh, 'ERR', "Token server unrecognized command %s" % command)
                err_msg = "Error: invalid command %s" % command
                connection.sendall(err_msg)
    
        # Clean up the connection
        debug_fh.close
        connection.close()

    except Exception as e:
        dbg.log(debug_fh, 'ERR', "Token server caught exception %s" % e)
        tb = traceback.format_exc()
        dbg.log(debug_fh, 'ERR', "%s" % tb)
        connection.sendall(e.message)
        debug_fh.close
        connection.close()
        

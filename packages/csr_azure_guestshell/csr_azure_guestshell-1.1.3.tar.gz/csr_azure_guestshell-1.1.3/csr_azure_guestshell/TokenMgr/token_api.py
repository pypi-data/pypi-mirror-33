#!/usr/bin/env python

import socket
import sys
import os
import time
sys.path.append('/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell')
import azure_dbg as dbg

sock_file = "/home/guestshell/azure/tools/TokenMgr/sock_file"
debug_file = "/home/guestshell/azure/tools/TokenMgr/tokenMgr.log"


def open_socket(debug_fh):
    # Create a UDS socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    try:
        sock.connect(sock_file)
    except socket.error, msg:
        dbg.log(debug_fh, 'ERR', "API: open_socket connect error %s" % msg)
        return (1, msg)
    return (0, sock)


def ping_server(debug_fh, sock):
    sock.settimeout(3)
    try:
        # Send data
        message = 'Ping'
        sock.sendall(message)

        # Receive the response
        data = sock.recv(8)
        if data == "Ack":
            return 0
        dbg.log(debug_fh, 'ERR', "API: ping_server: unexpected server response %s" % data)
        return 1

    except socket.error as err:
        dbg.log(debug_fh, 'ERR', "API: ping_server: socket error %d" % err.errno)
        return 2
    except socket.timeout:
        dbg.log(debug_fh, 'ERR', "API: ping_server: socket timeout")
        return 3
    except Exception as err:
        dbg.log(debug_fh, 'ERR', "API: ping_server: other socket error %d" % err.errno)
        return 4


def connect():
    global sock, debug_fh

    # Open up a file to write error and debug messages
    debug_fh = open(debug_file, "a", os.O_NONBLOCK)

    (rc, sock) = open_socket(debug_fh)
    if rc  != 0:
        return rc

    rc = ping_server(debug_fh, sock)
    if rc != 0:
        dbg.log(debug_fh, 'ERR', "API: connect: ping failed")

    return rc


def request_token_by_msi():
    global sock, debug_fh
    token = ''
    try:
        # Send request message
        req_msg = "MSI_req"
        sock.sendall(req_msg)

        # Receive the number of bytes in the token
        data = sock.recv(8)
        # Split the first response from the server 
        two_str = data.rsplit(' ')    
        token_len = int(two_str[0])
        token = two_str[1]

        # Now get the remaining bytes of the token
        done = False
        total_bytes_received = len(two_str[1])
        while total_bytes_received < token_len:
            data = sock.recv(8)
            bytes_received = len(data)
            token = token + data
            total_bytes_received += bytes_received

    except socket.error as err:
        dbg.log(debug_fh, 'ERR', "API: msi: socket error %d" % err.errno)
        dbg.log(debug_fh, 'ERR', "API: msi: expected token len %d" % token_len)
        dbg.log(debug_fh, 'ERR', "API: msi: actual token len %d" % total_bytes_received)
        token = ''
    except socket.timeout:
        dbg.log(debug_fh, 'ERR', "API: msi: socket timeout")
        dbg.log(debug_fh, 'ERR', "API: msi: expected token len %d" % token_len)
        dbg.log(debug_fh, 'ERR', "API: msi: actual token len %d" % total_bytes_received)
        token = ''
    except Exception as err:
        dbg.log(debug_fh, 'ERR', "API: msi: other socket error %d" % err.errno)
        dbg.log(debug_fh, 'ERR', "API: msi: expected token len %d" % token_len)
        dbg.log(debug_fh, 'ERR', "API: msi: actual token len %d" % total_bytes_received)
        token = ''

    finally:
        return token


def request_token_by_aad(cloud, tenantId, appId, appKey):
    global sock, debug_fh
    token = ''
    try:
        # Send request message
        req_msg = "AAD_req %s %s %s %s" % (cloud, tenantId, appId, appKey)
        sock.sendall(req_msg)

        # Receive the number of bytes in the token
        data = sock.recv(8)
        # Split the first response from the server 
        two_str = data.rsplit(' ')    
        token_len = int(two_str[0])
        token = two_str[1]
        token_len = token_len - len(two_str[1])

        # Now get the remaining bytes of the token
        done = False
        total_bytes_received = 0
        while total_bytes_received < token_len:
            data = sock.recv(8)
            bytes_received = len(data)
            token = token + data
            total_bytes_received += bytes_received

    except socket.error as err:
        dbg.log(debug_fh, 'ERR', "API: aad: socket error %d" % err.errno)
        token = ''
    except socket.timeout:
        dbg.log(debug_fh, 'ERR', "API: aad: socket timeout")
        token = ''
    except Exception as err:
        dbg.log(debug_fh, 'ERR', "API: aad: other socket error")
        token = ''

    finally:
        return token


def clear_token():
    global sock, debug_fh

    try:
        # Send data
        message = 'Clear'
        sock.sendall(message)

        # Receive the response
        data = sock.recv(32)
        if data == "OK":
            return 0
        dbg.log(debug_fh, 'ERR', "API: clear_token: unexpected server response %s" % data)
        return 0

    except socket.error:
        dbg.log(debug_fh, 'ERR', "API: clear_token: socket error")
        return 1 


def bad_cmd():
    global sock

    # Send data
    message = 'FooBar'
    print >>sys.stderr, 'sending "%s"' % message
    sock.sendall(message)

    data = sock.recv(64)
    if data == "OK":
        return 0
    dbg.log(debug_fh, 'ERR', "API: clear_token: unexpected server response %s" % data)
    return 0


def disconnect():
    global sock
    sock.close()


def get_token_by_msi():
    for attempt in range(3):
        rc = connect()
        if rc == 0:
            token = request_token_by_msi()

            if token == '':
                dbg.log(debug_fh, 'ERR', "API:msi: Failed to get token on attempt %d" % attempt)
                disconnect()
                if attempt < 3:
                    time.sleep(2)
                else:
                    return token
            else:
                disconnect()
                break
        else:
            if attempt < 3:
                time.sleep(2)
    return token

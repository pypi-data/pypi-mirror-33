"Debugging logging support for Azure"

import datetime
import syslog

debugEnabled = True

def log(fp, level, msg):
    global debugEnabled
    
    timestamp = str(datetime.datetime.now())
 
    sendLog = False
    if level == 'ERR':
        sendLog = True
        syslog.syslog(msg)
    if level == 'INFO':
        sendLog = True
    if (level == 'DBG') and (debugEnabled):
        sendLog = True

    if sendLog:
        full_msg = '\n' + timestamp + ' ' + msg
        fp.write(full_msg)
        fp.flush()

        

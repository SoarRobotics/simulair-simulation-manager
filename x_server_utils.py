import subprocess, signal, shlex, os
import asyncio

XServerProcess = None

def initXserver():
    global XServerProcess
    XServerProcess = subprocess.Popen(shlex.split('sudo /usr/bin/X :0'), stderr=subprocess.PIPE, stdout=subprocess.PIPE)

def activateDisplay():
    if 'DISPLAY' in os.environ:
        os.environ['DISPLAY'] = os.environ['DISPLAY'] + ':' + ':0'
    else:
        os.environ['LD_LIBRARY_PATH'] = ':0'

def isXserverRunning():
    p = subprocess.Popen(["xset", "-q"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    print(p.returncode)
    return p.returncode == 0



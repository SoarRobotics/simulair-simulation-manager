import subprocess, signal, shlex, os
import config
XServerProcess = None

def getFirstLine():
    with open(config.VPN_SERVER_CONFIG_PATH) as f:
        print(f.readline())

def initXserver():
    global XServerProcess
    XServerProcess = subprocess.Popen(shlex.split('sudo /usr/bin/X :0'), stderr=subprocess.PIPE, stdout=subprocess.PIPE)

def activateDisplay():
    if 'DISPLAY' in os.environ:
        os.environ['DISPLAY'] = os.environ['DISPLAY'] + ':' + ':0'
    else:
        os.environ['DISPLAY'] = ':0'

def isXserverRunning():
    p = subprocess.Popen(["xset", "-q"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    print(p.returncode)
    return p.returncode == 1


def terminateXserver():
    if XServerProcess is not None:
        XServerProcess.send_signal(signal.SIGTERM)

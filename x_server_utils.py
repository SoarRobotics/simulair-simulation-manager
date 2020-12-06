import subprocess, signal, shlex, os
import config
XServerProcess = None


def initXserver():
    global XServerProcess
    XServerProcess = subprocess.Popen(shlex.split('sudo /usr/bin/X :0'), stderr=subprocess.PIPE, stdout=subprocess.PIPE)

def activateDisplay():
    if 'DISPLAY' in os.environ:
        os.environ['DISPLAY'] = os.environ['DISPLAY'] + ':' + ':0'
    else:
        os.environ['DISPLAY'] = ':0'

def isXserverRunning():
    p = subprocess.Popen(["pgrep Xorg"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    p.communicate()
    return p.returncode == 0


def terminateXserver():
    if XServerProcess is not None:
        XServerProcess.send_signal(signal.SIGTERM)

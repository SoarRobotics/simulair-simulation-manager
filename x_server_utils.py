import subprocess, signal, shlex, os
import config

def initXserver():
    if not isXserverRunning():
        p = subprocess.Popen(shlex.split('sudo /usr/bin/X :0'), stderr=subprocess.PIPE, stdout=subprocess.PIPE)

def activateDisplay():
    if isXserverRunning():
        p = subprocess.Popen("export DISPLAY=:0", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        p.communicate()
        return p.returncode == 0 
    else :
        return True
        
def isXserverRunning():
    p = subprocess.Popen("pgrep Xorg", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    p.communicate()
    return p.returncode == 0


def terminateXserver():
    if isXserverRunning():
        p = subprocess.Popen("sudo pkill -9 Xorg", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        p.communicate()
        return p.returncode == 0
    else :
        return True

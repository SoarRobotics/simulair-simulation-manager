import subprocess, signal, shlex

XServerProcess = None

def initXserver():
    global XServerProcess
    XServerProcess = subprocess.Popen(shlex.split('sudo /usr/bin/X :0'), stderr=subprocess.PIPE, stdout=subprocess.PIPE)

def isXserverRunning():
    p = subprocess.Popen(["xset", "-q"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    print(p.returncode)
    return p.returncode == 0



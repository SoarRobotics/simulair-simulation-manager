import subprocess, signal, shlex

XServerProcess = None

def initXserver():
    global XServerProcess
    XServerProcess = subprocess.Popen(shlex.split('sudo /usr/bin/X :0'), stderr=subprocess.PIPE, stdout=subprocess.PIPE)



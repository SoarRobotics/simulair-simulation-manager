import subprocess

def initXserver():
    result = subprocess.run(['sudo /usr/bin/X :0 &', 'export DISPLAY=:0'], stdout=subprocess.PIPE)
    print(result.stdout.decode('utf-8'))
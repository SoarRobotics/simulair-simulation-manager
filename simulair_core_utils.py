import subprocess, signal, shlex, os
import config

def initCoreProcess(env_id, socketIP):
    if isCoreRunning():
        stopCoreProcess()
    p = subprocess.Popen('export ROS_DOMAIN_ID=42 && DISPLAY=:0 python3 {}/start_player.py socketPort={} socketIP={}'.format(config.CORE_PATH+"/"+env_id, config.MANAGER_PORT, socketIP) ,stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)


def isCoreRunning():
    p = subprocess.Popen('pgrep RosApplication', stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    p.communicate()
    return p.returncode == 0

def stopCoreProcess():
    if isCoreRunning():
        p = subprocess.Popen('sudo pkill -9 RosApplication',stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        p.communicate()
        return p.returncode == 0
    else:
        return True
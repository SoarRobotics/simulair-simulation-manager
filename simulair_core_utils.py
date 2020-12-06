import subprocess, signal, shlex, os
import config
CoreProcess= None

def initCoreProcess(env_id, socketIP):
    global CoreProcess
    CoreProcess = subprocess.Popen('export ROS_DOMAIN_ID=42 && python3 {}/start_player.py socketPort={} socketIP={}'.format(config.CORE_PATH+"/"+env_id, config.MANAGER_PORT, socketIP) ,stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    
def isCoreRunning():
    p = subprocess.Popen('pgrep RosApplication', stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    p.communicate()
    return p.returncode == 0
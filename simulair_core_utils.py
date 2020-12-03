import subprocess, signal, shlex, os
import config
CoreProcess= None

def initCoreProcess(env_id, socketIP):
    global CoreProcess
    CoreProcess = subprocess.Popen('export ROS_DOMAIN_ID=42 && export DISPLAY=:0 && python3 {}/start_player.py socketPort={} socketIP={}'.format(config.CORE_PATH+"/"+env_id, config.MANAGER_PORT, socketIP), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)


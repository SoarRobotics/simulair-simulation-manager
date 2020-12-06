import subprocess, signal, shlex, os
import config
CoreProcess= None

def initCoreProcess(env_id, socketIP):
    global CoreProcess
    my_env = os.environ.copy()
    CoreProcess = subprocess.Popen('python3 {}/start_player.py socketPort={} socketIP={}'.format(config.CORE_PATH+"/"+env_id, config.MANAGER_PORT, socketIP), env=my_env  ,stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    
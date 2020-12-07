import threading, time, subprocess 
import config, simulair_core_utils, state_manager, log_manager, x_server_utils, aws_utils, vpn_server_utils



SimulationInfo = {}

def getInstanceInfo(): #
    instanceId = aws_utils.getInstanceId()
    publicIp = aws_utils.getPublicIp()
    publicDnsName = aws_utils.getPublicDnsName()
    _id = aws_utils.getSimulationId(instanceId)[0].get("_id", None)
    global SimulationInfo
    if _id is not None:
        aws_utils.setPublicIp(_id, publicIp)
        aws_utils.setPublicDnsName(_id, publicDnsName)
        SimulationInfo = aws_utils.getSimulationInfo(_id)  # TODO write this to a file
        if not SimulationInfo["_id"]:
            logLine("Fatal Error: No valid simulation found!")
            return None
        logLine("Simulation info has received: {}".format(SimulationInfo["_id"]))
    return SimulationInfo

def setInstanceStatus(status):
    if SimulationInfo is not None:
        aws_utils.setStatus(SimulationInfo["_id"], status)
        logLine("The instance state has updated to '{}'".format(status))
    else :
        logLine("Invalid Operation: System unable to get simulation info")


def run_sim(env_id, socketIP):
    local_environments = state_manager.get("downloaded_environments")
    if (local_environments != None) and (env_id in local_environments):
        logLine("Core module is starting")
        simulair_core_utils.initCoreProcess(env_id, socketIP)
        logLine("Core module has started")
        return True
    if (local_environments == None) or not (env_id in local_environments):
         if aws_utils.downloadAndSaveEnvironment(env_id):
             run_sim(env_id, socketIP)
         else:
             return False

        
def async_initialize():
    setInstanceStatus("pending1")
    getInstanceInfo()
    state_manager.set("initialized", False)
    if SimulationInfo is not None:
        if not vpn_server_utils.isVpnServerInstalled():
            state_manager.set("last_created_cred_index", None)
            logLine("Vpn server is being installed!!")
            vpn_server_utils.installVpnServer(SimulationInfo["instance_info"]["publicIpAddress"], SimulationInfo["instance_info"]["privateIpAddress"])
            setInstanceStatus("pending2")
            time.sleep(3)
        x_server_utils.initXserver()
        time.sleep(3)
        x_server_utils.activateDisplay()
        run_sim(SimulationInfo["environment_id"], SimulationInfo["instance_info"]["privateIpAddress"])
        setInstanceStatus("pending3")
        state_manager.set("initialized", True)


def initialize():
    x = threading.Thread(target=async_initialize())
    x.start()
    return x


SimulationInfo = None
result = {
    "status" : None,
    "meta" : {
        "message" : None
    }
}


def createVpnCred(user_id):
    
    last_index = state_manager.get("last_created_cred_index")
    name="default"
    if last_index is not None:
        last_index = last_index + 1
        name = SimulationInfo["_id"]+"_"+str(last_index)
        state_manager.set("last_created_cred_index", last_index)
    else:
        name = SimulationInfo["_id"]+"_0"
        state_manager.set("last_created_cred_index", 0)
    vpn_server_utils.createClientCredential(name)
    time.sleep(1) #wait some
    a = aws_utils.uploadUserFile(config.VPN_CREDENTIALS_DIR+"/"+name+".ovpn", user_id)
    aws_utils.addNewCredToUser(user_id, SimulationInfo["_id"], name, a)
    return name

def dispatchLogFile(sim_id):
    a = aws_utils.uploadLogFile(sim_id)
    aws_utils.addLogToSim(sim_id, a)

def updateLogFile(sim_id):
    aws_utils.uploadLogFile(sim_id)

def logLine(line):
    log_manager.writeLogLine(line)

def freeManagerPort():
    p = subprocess.Popen("sudo fuser -n tcp -k " + config.MANAGER_PORT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    p.communicate()
    return p.returncode == 0
##this method reset everything except for the vpn server
def resetInstance():
    setInstanceStatus("pending2") #instance is initialized but modules are not initialized
    logLine("cached environments are being removed...")
    p = subprocess.Popen("sudo rm -r " + config.CORE_PATH+"/*", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    p.communicate()
    freeManagerPort() ## free port if already in use
    logLine("cached environments are removed")
    logLine("state file is cleaning...")
    p = subprocess.Popen("sudo echo '{}' > /home/ubuntu/.state/state.json", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) ## clean the state file
    p.communicate()
    if p.returncode != 0:
        return False
    logLine("state file is cleaned")
    if not x_server_utils.terminateXserver():
        return False
    if not simulair_core_utils.stopCoreProcess():
        return False
    return True
    
import threading, time, x_server_utils, aws_utils, vpn_server_utils, subprocess
import config, simulair_core_utils, state_manager, log_manager

SimulationInfo = {"_id" : "2f370ff0-3040-11eb-9e8e-7d37a30c8bc0"}
result = {
    "status" : None,
    "meta" : {
        "message" : None
    }
}

def getInstanceInfo():
    instanceId = aws_utils.getInstanceId()
    publicIp = aws_utils.getPublicIp()
    publicDnsName = aws_utils.getPublicDnsName()
    _id = aws_utils.getSimulationId(instanceId)[0].get("_id", None)
    global SimulationInfo
    if _id is not None:
        aws_utils.setPublicIp(_id, publicIp)
        aws_utils.setPublicDnsName(_id, publicDnsName)
        setInstanceStatus("pending2")
        SimulationInfo = aws_utils.getSimulationInfo(_id)  # TODO write this to a file
        log_manager.writeLogLine("Simulation info has received: {}".format(SimulationInfo["_id"]))
    return SimulationInfo

def setInstanceStatus(status):
    if SimulationInfo is not None:
        aws_utils.setStatus(SimulationInfo["_id"], status)
        log_manager.writeLogLine("The instance state has updated to '{}'".format(status))
    else :
        log_manager.writeLogLine("The instance state has updated to '{}'".format(status))


def run_demo_sim(socketIP):
    time.sleep(2)
    simulair_core_utils.initCoreProcess(config.DEMO_CORE_PATH, socketIP)
    time.sleep(3)



def async_initialize():
    setInstanceStatus("pending1")
    state_manager.set("initialized", False)
    if SimulationInfo is not None:
        if not vpn_server_utils.isVpnServerInstalled():
            vpn_server_utils.installVpnServer(SimulationInfo["instance_info"]["publicIpAddress"], SimulationInfo["instance_info"]["privateIpAddress"])
            setInstanceStatus("pending2")
            time.sleep(3)
        run_demo_sim(SimulationInfo["instance_info"]["privateIpAddress"])
        setInstanceStatus("pending3")
        state_manager.set("initialized", True)


def initialize():
    getInstanceInfo()
    x = threading.Thread(target=async_initialize())
    x.start()
    return x


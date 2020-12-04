import threading, time, x_server_utils, aws_utils, vpn_server_utils, subprocess
import config, simulair_core_utils, state_manager

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
    return SimulationInfo

def setInstanceStatus(status):
    if SimulationInfo is not None:
        aws_utils.setStatus(SimulationInfo["_id"], status)


def run_x_server(timeout=6, delay=2):
    loop_count = timeout // delay
    for i in range(0, loop_count):
        if not x_server_utils.isXserverRunning():
            x_server_utils.initXserver()
        else:
            x_server_utils.activateDisplay()
            return True
        time.sleep(delay)
    result["status"] = 400
    result["meta"]["message"] = "X server initialization failed"
    return False

def run_demo_sim(socketIP):
    time.sleep(2)
    simulair_core_utils.initCoreProcess(config.DEMO_CORE_PATH, socketIP)
    setInstanceStatus("pending3")
    time.sleep(3)

def async_initialize():
    state_manager.set("initialized", False)
    if SimulationInfo is not None:
        if state_manager.get("vpn_initialized") is None:
            vpn_server_utils.initVpnServer(SimulationInfo["instance_info"]["publicIpAddress"], SimulationInfo["instance_info"]["privateIpAddress"])
            time.sleep(3)
            state_manager.set("vpn_initialized", True)
        run_x_server()
        time.sleep(3)
        run_demo_sim(SimulationInfo["instance_info"]["privateIpAddress"])
        state_manager.set("initialized", True)


def initialize():
    getInstanceInfo()
    x = threading.Thread(target=async_initialize())
    x.start()
    return x


import threading, time, x_server_utils, aws_utils, vpn_server_utils
import config, simulair_core_utils

SimulationInfo = None
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


def run_x_server(timeout=20, delay=2):
    loop_count = timeout // delay
    for i in range(0, loop_count):
        if not x_server_utils.isXserverRunning():
            x_server_utils.initXserver()
        else:
            x_server_utils.activateDisplay()
            return True
        time.sleep(delay)
    result["status"] = 400
    result["meta"]["message"] = "X server initialization failed";
    return False

def run_demo_sim(socketIP):
    time.sleep(2)
    simulair_core_utils.initCoreProcess(config.DEMO_CORE_PATH, socketIP)
    setInstanceStatus("pending3")
    time.sleep(3)

def async_initialize():
    if SimulationInfo is not None:
        vpn_server_utils.initVpnServer(SimulationInfo["instance_info"]["publicIpAddress"], SimulationInfo["instance_info"]["privateIpAddress"])
        time.sleep(3)
        run_x_server()
        run_demo_sim(SimulationInfo["instance_info"]["publicIpAddress"])


def initialize():
    x = threading.Thread(target=async_initialize())
    x.start()
    return result


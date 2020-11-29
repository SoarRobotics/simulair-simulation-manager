import asyncio, x_server_utils, aws_utils, vpn_server_utils
import config

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
        aws_utils.setStatus(_id, "pending2")
        SimulationInfo = aws_utils.getSimulationInfo(_id)  # TODO write this to a file
    return SimulationInfo

async def run_x_server(timeout=20, delay=3):
    loop_count = timeout // delay
    for i in range(0, loop_count):
        if not x_server_utils.isXserverRunning():
            x_server_utils.initXserver()
        else:
            x_server_utils.activateDisplay()
            return True
        await asyncio.sleep(delay)
    result["status"] = 400
    result["meta"]["message"] = "X server initialization failed";
    return False

async def async_initialize():
    if SimulationInfo is not None:
        await vpn_server_utils.initVpnServer(SimulationInfo["instance_info"]["publicIpAddress"], SimulationInfo["instance_info"]["privateIpAddress"])
        await asyncio.sleep(5)
        await run_x_server()


def initialize():
    getInstanceInfo()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_initialize())
    loop.close()
    return result


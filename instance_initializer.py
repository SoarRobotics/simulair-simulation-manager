import asyncio, x_server_utils, aws_utils

result = {
    "status" : None,
    "meta" : {
        "message" : None
    }
}
async def run_x_server(timeout=10, delay=2):
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

def initialize():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_x_server())
    loop.close()
    return result

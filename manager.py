import threading, time, x_server_utils, aws_utils, vpn_server_utils
import config, simulair_core_utils, state_manager, instance_initializer

SimulationInfo = None
result = {
    "status" : None,
    "meta" : {
        "message" : None
    }
}

def createVPNAccess(user_id):
    last_index = state_manager.get("last_created_cred_index")
    name="default"
    if last_index is not None:
        name = instance_initializer.SimulationInfo["_id"][:5]+"_"+last_index
    else:
        name = instance_initializer.SimulationInfo["_id"][:5]+"_0"
        state_manager.set("last_created_cred_index", 0)
    vpn_server_utils.createClientCredential(name)
    time.sleep(4)
    a = aws_utils.uploadUserFile(config.VPN_CREDENTIALS_DIR+"/"+name, user_id)
    aws_utils.setVpnCredAddress(user_id, instance_initializer.SimulationInfo["_id"], a)





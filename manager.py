import threading, time, x_server_utils, aws_utils, vpn_server_utils
import config, simulair_core_utils, state_manager, instance_initializer


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
        name = instance_initializer.SimulationInfo["_id"]+"_"+str(last_index)
        state_manager.set("last_created_cred_index", last_index)
    else:
        name = instance_initializer.SimulationInfo["_id"]+"_0"
        state_manager.set("last_created_cred_index", 0)
    vpn_server_utils.createClientCredential(name)
    time.sleep(1) #wait some
    a = aws_utils.uploadUserFile(config.VPN_CREDENTIALS_DIR+"/"+name+".ovpn", user_id)
    print("here is your fucking credential bitch oç ?^+%34. {}".format(instance_initializer.SimulationInfo["_id"]))
    aws_utils.addNewCredToUser(user_id, instance_initializer.SimulationInfo["_id"], name, a)
    return name




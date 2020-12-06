import subprocess, asyncio, shlex, os
import config, state_manager

MAX_ALLOWED_CRED_PER_USER = 3

def installVpnServer(publicIp, privateIp):
    global VpnProcess
    vpnProcess = subprocess.Popen(shlex.split('sudo bash ' + config.BASH_SCRIPTS_DIR+"/set_vpn_params.sh --publicIp={} --privateIp={}".format(publicIp, privateIp)),
                                  stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    vpnProcess.wait()
    out, error = vpnProcess.communicate()
    if error != b'':
        print(error)
        return False
    else:
        state_manager.set("vpn_initialized", True)
        print("vpn service configured!")
        return True       

def isVpnServerInstalled():
    p = subprocess.Popen(["service openvpn-server@server status > /dev/null"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    p.communicate()
    return p.returncode == 0

    
def createClientCredential(name):
    process = subprocess.Popen(shlex.split('sudo bash ' + config.BASH_SCRIPTS_DIR + "/create_user.sh --userName={}".format(name)),
                                  stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    process.wait()
    out, error = process.communicate()
    print(error.decode("utf-8"))

def isVpnServerRunning():
    stat = os.system('sudo systemctl status openvpn-server@server.service > /dev/null')
    return stat == 0


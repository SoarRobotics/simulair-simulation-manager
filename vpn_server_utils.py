import subprocess, asyncio, shlex, os
import config


def initVpnServer(publicIp, privateIp):
    global VpnProcess
    vpnProcess = subprocess.Popen(shlex.split('sudo bash ' + config.BASH_SCRIPTS_DIR+"/set_vpn_params.sh --publicIp={} --privateIp={}".format(publicIp, privateIp)),
                                  stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    vpnProcess.wait()
    out, error = vpnProcess.communicate()
    print(out, error)



def createClientCredential(name):
    process = subprocess.Popen(shlex.split('sudo bash ' + config.BASH_SCRIPTS_DIR + "/create_user.sh --userName={}".format(name)),
                                  stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    process.wait()
    out, error = process.communicate()
    print(out, error)

def isVpnServerRunning():
    stat = os.system('sudo systemctl status openvpn-server@server.service > /dev/null')
    return stat == 0


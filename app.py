from flask import  Flask, render_template, request, redirect, jsonify, make_response
from flask_socketio import SocketIO, emit
import  config
import instance_initializer, manager, aws_utils, state_manager
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
simulair_web_api = "https://ju5x7v2aji.execute-api.eu-central-1.amazonaws.com/dev"
serverID = 'undefined'




@app.route('/')
def index():
    userId = request.args.get("userId")
    publicIp = instance_initializer.SimulationInfo["instance_info"]["publicIpAddress"]
    publicDns = instance_initializer.SimulationInfo["instance_info"]["publicDnsName"]
    return render_template('home.html', _userId=userId, _publicIp=publicIp, _publicDns=publicDns)

def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/new_credential', methods=["GET", "OPTIONS"])
def new_cred():
    if request.method == "OPTIONS":
        return _build_cors_prelight_response()
    elif request.method == "GET":
        userId = request.args.get("userId")
        print("user id is here amk senin oç piç.ç. {}".format(userId))
        sim_id = instance_initializer.SimulationInfo["_id"]
        if state_manager.get("initialized") is not None or state_manager.get("initialized") is not False:
            cred_name = manager.createVpnCred(userId)
            params = {
                'userId' : userId,
                "sim_id" : sim_id,
                "cred_name" : cred_name
            }
            r = requests.get(simulair_web_api+"/vpn-red", params=params).content
            print(r)
            response = {"data " : "done"}
            return _corsify_actual_response(jsonify("response"))
        return ""

@socketio.on("connect")
def notify_connect():
    emit("connection-accepted", {"connected": True})
    print("a user is connected: {} (server: {} )".format(request.sid, serverID))

@socketio.on("disconnect")
def disconnect():
    global serverID
    if serverID == request.sid:
        serverID = 'undefined'
        print('removed Server: {}'.format(request.sid))
    else:
        print('user disconnected: {}'.format(request.sid))

@socketio.on("RegServerId")
def regServerId():
    global serverID
    serverID = request.sid
    instance_initializer.setInstanceStatus("running")
    print("reg server id : {} ".format(serverID))

@socketio.on('OnReceiveData')
def onReceiveData(data):
    if serverID != 'undefined':
        if data["EmitType"] == 0:
            emit('OnReceiveData', {"DataString" : data["DataString"], "DataByte" : data["DataByte"]})
        if data["EmitType"] == 1:
            emit('OnReceiveData', {"DataString": data["DataString"], "DataByte": data["DataByte"]}, room=serverID)
        if data["EmitType"] == 2:
            emit('OnReceiveData', {"DataString": data["DataString"], "DataByte": data["DataByte"]}, broadcast=True)
    else:
        print('cannot find any active server')


if __name__ == "__main__":
    instance_initializer.initialize()
    socketio.run(app, port=int(config.MANAGER_PORT), host="0.0.0.0")

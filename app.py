from flask import  Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit
import requests
import awsGetters
import boto3
import X_Server_Init
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


serverID = 'undefined'

@app.route('/')
def index():
    return render_template('home.html')

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
    X_Server_Init.isXserverRunning()
    instanceId = awsGetters.getInstanceId()
    publicIp = awsGetters.getPublicIp()
    _id = awsGetters.getSimulationId("i-02a2ba4a9759c23b4")[0].get("_id", None)
    simulation_info = None;
    if _id is not None:
        simulation_info = awsGetters.getSimulationInfo(_id)#TODO write this to a file
        print(awsGetters.setPublicIp(_id, "buraya o ip gelecek!!"))
        awsGetters.setStatus(_id, "pending2")


    socketio.run(app, port=3003, host="0.0.0.0")

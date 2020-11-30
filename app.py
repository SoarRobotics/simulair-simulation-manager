from flask import  Flask, render_template, request, redirect, jsonify
from flask_socketio import SocketIO, emit
import  config
import instance_initializer, manager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


serverID = 'undefined'




@app.route('/')
def index():
    return render_template('home.html')

@app.route('/new_credential/<user_id>')
def new_cred(user_id):
    r = manager.createVPNAccess(user_id)
    return r

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

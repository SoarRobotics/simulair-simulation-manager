import config, app

def writeLogLine(line):
    print(line)
    with open(config.LOG_DIR, "a") as log:
        log.write(line)
        broadcastLine(line)

def readLog():
    return open(config.LOG_DIR, 'r').read()

def getLogFile():
    return open(config.LOG_DIR, "r")

def broadcastLine(line):
    if app.socketio:
       app.socketio.emit("new-log", {"data" : line}, broadcast=True) 
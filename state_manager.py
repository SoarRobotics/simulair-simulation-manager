import config, os, json

path = config.STATE_PATH + "/" + config.STATE_FILE
def checkIfExists():
    if os.path.exists(path):
        return True
    else:
        return False

def createStateFile():
    if checkIfExists():
        return
    else:
        try:
            os.mkdir(config.STATE_PATH)
        except Exception:
            pass

    f = open(path, "a")
    f.write("{}")
    f.close()

def get(key):
    if checkIfExists():
        with open(path) as f:
            data = json.load(f)
            return data.get(key, None)
    else:
        return None

def set(key, value):
    if checkIfExists():
        with open(path) as f:
            data = json.load(f)
            data[key] = value
        with open(path, 'w') as outfile:
            json.dump(data, outfile)
    else:
        createStateFile()
        set(key, value)
import requests, os, subprocess
import boto3
import config, state_manager, vpn_server_utils
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

user_resources_bucket = s3.Bucket(config.USER_RESOURCE_BUCKET_NAME)
global_resources_bucket = s3.Bucket(config.GLOBAL_RESOURCE_BUCKET_NAME)
SIM_TABLE = 'simulair_simulations'
USER_ASSETS_TABLE = 'simulair-user-assets'

def getInstanceId():
    return (requests.get("http://169.254.169.254/latest/meta-data/instance-id").text)

def getPublicIp():
    return (requests.get("http://169.254.169.254/latest/meta-data/public-ipv4").text)

def getPublicDnsName():
    return (requests.get("http://169.254.169.254/latest/meta-data/public-hostname").text)

def getSimulationId(instance_id):
    table = dynamodb.Table(SIM_TABLE)
    scan_kwargs = {
        "FilterExpression" : Key('instanceId').eq(instance_id),
        "ProjectionExpression" : "#id",
        "ExpressionAttributeNames" : {"#id" : "_id"}
    }

    done = False
    start_key = None
    response = []
    while not done:
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key
        temp_response = table.scan(**scan_kwargs)
        start_key = temp_response.get("LastEvaluatedKey", None)
        response += temp_response.get("Items", None)
        done = start_key is None

    return response


def getSimulationInfo(simId):
    table = dynamodb.Table(SIM_TABLE)

    response = table.get_item(Key={
        "_id": simId,
    })
    return response.get("Item", None)

def getUserInfo(userId):
    table = dynamodb.Table(USER_ASSETS_TABLE)
    response = table.get_item(Key={
        "_id": userId,
    })
    return response.get("Item", None)

def addNewCredToUser(userId, simId, name, url):
    index = _checkIfUserEligible(userId, simId)
    print(index)
    if index is None:
        raise Exception("Not Authorized!")

    table = dynamodb.Table(USER_ASSETS_TABLE)
    updateExp = "SET simulations[{}].vpn_credentials = :item".format(index[0]) #create if doesn't exist
    if index[1] != 0:
        updateExp = "SET simulations[{}].vpn_credentials = list_append(simulations[{}].vpn_credentials, :item)".format(index[0], index[0])
    
    response = table.update_item(
        Key={
            '_id': userId
        },
        UpdateExpression=updateExp,
        ExpressionAttributeValues = {
                    ':item' : [{ "name" : name, "url":url}]
            }, 
        ReturnValues="UPDATED_NEW"
    )

def addLogToSim(sim_id, url):
    table = dynamodb.Table(SIM_TABLE)
    updateExp = "SET log_file = :item" #create if doesn't exist
    response = table.update_item(
        Key={
            '_id': sim_id
        },
        UpdateExpression=updateExp,
        ExpressionAttributeValues = {
                    ':item' : url
            }, 
        ReturnValues="UPDATED_NEW")


def _checkIfUserEligible(userId, simId):
    a = getUserInfo(userId)
    if a is None:
        return None
    index = getIndexOfSim(a["simulations"], simId)
    if index is None:
        return None
    try:
        creds_list = a["simulations"][index]["vpn_credentials"]
        if len(creds_list) <= vpn_server_utils.MAX_ALLOWED_CRED_PER_USER:
            return (index, len(creds_list))
        else :
            return None
    except KeyError:
        return (index, 0)
    return None


def getIndexOfSim(simList, simId):
    for sim in simList:
        if sim["sim_id"] == simId:
            return simList.index(sim)  

    return None

    

def setPublicIp(_id, ip):
    table = dynamodb.Table(SIM_TABLE)
    response = table.update_item(
        Key={
            '_id': _id
        },
        UpdateExpression='SET instance_info.publicIpAddress = :ip',
        ExpressionAttributeValues = {
                    ':ip' : ip
            },
        ReturnValues="UPDATED_NEW"
    )

    return(response)

def setPublicDnsName(_id, dnsName):
    table = dynamodb.Table(SIM_TABLE)
    response = table.update_item(
        Key={
            '_id': _id
        },
        UpdateExpression='SET instance_info.publicDnsName = :dns',
        ExpressionAttributeValues = {
                    ':dns' : dnsName
            },
        ReturnValues="UPDATED_NEW"
    )

    return(response)


def setStatus(_id, status):
    table = dynamodb.Table(SIM_TABLE)
    response = table.update_item(
        Key={
            '_id': _id
        },
        UpdateExpression='SET #status = :status',
        ExpressionAttributeValues = {
                    ':status' : status
            },
        ExpressionAttributeNames={
            "#status" : "status"
        },
        ReturnValues="UPDATED_NEW"
    )

    return(response)


def uploadFile(bucket, file_path, upload_name):
    bucket.upload_file(
        Filename=file_path,
        Key=upload_name,
        ExtraArgs={'ACL': 'public-read'}
    )

def uploadUserFile(file_path, user_id):
    file_dir, file_name = os.path.split(file_path)
    upload_name = getUserFolderName(user_id)+"/"+file_name
    uploadFile(user_resources_bucket, file_path, upload_name)
    return f"https://{config.USER_RESOURCE_BUCKET_NAME}.s3.amazonaws.com/{upload_name}"

def uploadLogFile(sim_id):
    upload_name = getSimFolderName(sim_id)+"/logs/log"
    uploadFile(user_resources_bucket, config.LOG_DIR, upload_name)
    return f"https://{config.GLOBAL_RESOURCE_BUCKET_NAME}.s3.amazonaws.com/{upload_name}"

def getUserFolderName(user_id):
    prefix = user_id
    postfix = "-resource"
    return prefix+postfix

def getSimFolderName(sim_id):
    prefix = sim_id
    postfix = "-data"
    return prefix+postfix

def downloadAndSaveEnvironment(env_id):
    try :
        global_resources_bucket.download_file("environments/"+env_id, config.CORE_PATH+"/"+env_id+".tar.xz")
        set_val = (state_manager.get("downloaded_environments") == None) and [env_id] or (state_manager.get("downloaded_environments") + [env_id])
        state_manager.set("downloaded_environments", set_val)
    except Exception as e:
        print(e)
        return False
    p = subprocess.Popen("tar -xf " + config.CORE_PATH+"/"+env_id+".tar.xz -C "+ config.CORE_PATH+"/", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    p.communicate()
    if p.returncode != 0:
        return False
    p = subprocess.Popen("rm " + config.CORE_PATH+"/"+env_id+".tar.xz", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    p.communicate()
    if p.returncode != 0:
        return False
    return True
    

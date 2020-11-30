import requests, os
import boto3
import config, state_manager
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
s3 = boto3.resource('s3')
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

def getSimulationInfo(_id):
    table = dynamodb.Table(SIM_TABLE)

    response = table.get_item(Key={
        "_id": _id,
    })
    return response.get("Item", None)

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

def setVpnCredAddress(user_id, sim_id, url):
    table = dynamodb.Table(USER_ASSETS_TABLE)
    scan = table.get_item(Key={
        "_id": user_id,
    })

    new_data = None
    for item, index in scan["simulations"]:
        if item["sim_id"] == sim_id:
            if "vpn_creds" in item:
                item["vpn_creds"].append(url)
            else:
                item["vpn_cred"] = [url]

            new_data[index] = item

        if new_data is not None:
            response = table.update_item(
                Key={
                    '_id': user_id
                },
                UpdateExpression='SET #simulations = :simulations',
                ExpressionAttributeValues={
                    ':simulations': new_data
                },
                ExpressionAttributeNames={
                    "#simulations" : "simulations"
                },
                ReturnValues="UPDATED_NEW"
            )
    return url


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


def getUserFolderName(user_id):
    prefix = user_id[:5]
    postfix = "-resource"
    return prefix+postfix

def downloadAndSaveFile(file):
    return None

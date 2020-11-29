import requests
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
SIM_TABLE = 'simulair_simulations';

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


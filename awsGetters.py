import requests
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

def getInstanceId():
    return (requests.get("http://169.254.169.254/latest/meta-data/instance-id").text)

def getPublicIp():
    return (requests.get("http://169.254.169.254/latest/meta-data/public-ipv4").text)

def getSimulation(instance_id):
    table = dynamodb.Table('simulair_simulations')
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
        response.append(table.scan(**scan_kwargs))
        start_key = response.get("LastEvaluatedKey", None)
        done = start_key is None

    return response


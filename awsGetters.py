import requests
import boto3
from boto3.dynamodb.conditons import Key

dynamodb = boto3.resource('dynamodb')

def getInstanceId():
    return (requests.get("http://169.254.169.254/latest/meta-data/instance-id").text)

def getPublicIp():
    return (requests.get("http://169.254.169.254/latest/meta-data/public-ipv4").text)

def getSimulation(instance_id):
    table = dynamodb.Table('simulair_simulations')
    return table.scan(
        ScanFilter =
        {
            'instanceId' : {
                'AttributeValueList' :
                    [
                        'S' : instance_id
                    ],
                    'ComparisonOperator': 'EQ'
            }
        }
    )

# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except
# in compliance with the License. A copy of the License is located at
#
# https://aws.amazon.com/apache-2-0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import boto3
import json

from aws_xray_sdk.core import patch_all

patch_all()


s3 = boto3.client('s3','us-east-2')
ssm = boto3.client('ssm', 'us-east-2')
bucket_name = ssm.get_parameter( Name='baggy765',WithDecryption=False)['Parameter']['Value']
file_name = ssm.get_parameter( Name='dragon_stats_one.txt',WithDecryption=False)['Parameter']['Value']

def listDragons(event, context):
    
    expression = "select * from s3object[*][*] s"

    if 'queryStringParameters' in event and event['queryStringParameters'] is not None:
        if 'dragonName' in event['queryStringParameters']:
            expression = "select * from S3Object[*][*] s where s.dragon_name_str =  '" + event["queryStringParameters"]['dragonName'] + "'"
        if 'family' in event['queryStringParameters']:
            expression = "select * from S3Object[*][*] s where s.family_str =  '" + event["queryStringParameters"]['family'] + "'"

    result = s3.select_object_content(
            Bucket=bucket_name,
            Key=file_name,
            ExpressionType='SQL',
            Expression=expression,
            InputSerialization={'JSON': {'Type': 'Document'}},
            OutputSerialization={'JSON': {}}
    )
    
    result_stream = []
    for event in result['Payload']:
        if 'Records' in event:
            for line in event['Records']['Payload'].decode('utf-8').strip().split("\n"):
                result_stream.append(json.loads(line))
            
        
    return {
        "statusCode": 200,
        "body": json.dumps(result_stream),
        "headers" : {"access-control-allow-origin": "*"}
    }

     



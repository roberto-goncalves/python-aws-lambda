"""Send metric to cloudwatch from another lambda function"""
import boto3
import logging
import os
import json
import datetime

os.environ['TZ'] = 'America/Sao_Paulo'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cloudwatch_client = boto3.client('cloudwatch')
lambda_client = boto3.client('lambda')


def sendCloudWatchMetric():
    response = lambda_client.invoke(FunctionName='<name_of_lambda_function_to_call>', InvocationType='RequestResponse')
    string_response = response["Payload"].read().decode('utf-8')
    logger.info("response: %s", string_response)
    response_attributes = json.loads(string_response)
    for item in response_attributes["result"]: 
        logger.info("Sending metric to cloudwatch %s", cloudwatch_client.put_metric_data(
        Namespace=item["metric_namespace"],
        MetricData=[
            {
                'MetricName': '<metric_name>',
                'Dimensions': [
                    {
                       'Name': 'Y',
                       'Value': '<metric_dashboard_value>'
                    },
                 ],
                 'Timestamp': datetime.datetime.utcnow(),
                 'Value': "<metric_real_value>",
                 'Unit': 'Gigabytes',
                 'StorageResolution': 60
            },
        ]
        ))

def lambda_handler(event, context):
    return sendCloudWatchMetric()
    
if __name__ == '__main__':
    lambda_handler(None, None)

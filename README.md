# AWS Lambda Functions


## python-call-another-lambda-cloudwatch

This function call another lambda function and send them to cloudwatch

```python
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
```

## python-oracle-access	

This function access oracle and executes queries inside, remembering to read AWS Lambda documents on how to pack and execute it.

## python-rds-snapshot-cross-region

This function access snapshots created by the RDS service and migrate them to another AWS AZ.

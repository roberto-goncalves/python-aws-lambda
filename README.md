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

```python
def callOracleResponse():
    result = {'result': []}
    compose = executeQuery("<my_db_endpoint>","<db_sid>", "<db_user>", "<db_pwd>", "<query>")
    result['result'].append(compose)
    logger.info("Result %s", json.dumps(result, ensure_ascii=False))
    return json.dumps(result)

def executeQuery(ENDPOINT, SID, USER, PASSWORD, QUERY):
    function_return = {'values': []}
    dsn_tns = cx_Oracle.makedsn(ENDPOINT, 1600, SID)
    connection = cx_Oracle.connect(USER, PASSWORD, dsn_tns)
    cursor = connection.cursor()
    cursor.execute(QUERY)
    for values in cursor:
        function_return['values'].append(values)
    return function_return
```

## python-rds-snapshot-cross-region

This function access snapshots created by the RDS service and migrate them to another AWS AZ.
```python
def copy_latest_snapshot():
    client = boto3.client('rds', 'sa-east-1')
    virginia_client = boto3.client('rds', 'us-east-1')

    response = client.describe_db_snapshots(SnapshotType='automated',IncludeShared=False,IncludePublic=False)

    if len(response['DBSnapshots']) == 0:
        raise Exception("No automated snapshots found")

    snapshots_per_project = {}
    for snapshot in response['DBSnapshots']:
        if snapshot['Status'] != 'available':
            continue

        if snapshot['DBInstanceIdentifier'] not in snapshots_per_project.keys():
            snapshots_per_project[snapshot['DBInstanceIdentifier']] = {}

        snapshots_per_project[snapshot['DBInstanceIdentifier']][snapshot['DBSnapshotIdentifier']] = snapshot[
            'SnapshotCreateTime']

    for project in snapshots_per_project:
        sorted_list = sorted(snapshots_per_project[project].items(), key=operator.itemgetter(1), reverse=True)

        copy_name = project + "-" + sorted_list[0][1].strftime("%Y-%m-%d")

        print("Checking if " + copy_name + " is copied")

        try:
            virginia_client.describe_db_snapshots(
                DBSnapshotIdentifier=copy_name
            )
        except:
            response = virginia_client.copy_db_snapshot(
                SourceDBSnapshotIdentifier='arn:aws:rds:sa-east-1:' + ACCOUNT + ':snapshot:' + sorted_list[0][0],
                TargetDBSnapshotIdentifier=copy_name,
                #KmsKeyId='kms_key_id',  IF SNAPSHOT IS ENCRYPTED
                CopyTags=True
            )

            if response['DBSnapshot']['Status'] != "pending" and response['DBSnapshot']['Status'] != "available":
                raise Exception("Copy operation for " + copy_name + " failed!")
            print("Copied " + copy_name)

            continue

        print("Already copied")


def remove_old_snapshots():
    client = boto3.client('rds', 'sa-east-1')
    virginia_client = boto3.client('rds', 'us-east-1')

    response = virginia_client.describe_db_snapshots(
        SnapshotType='manual'
    )

    if len(response['DBSnapshots']) == 0:
        raise Exception("No manual snapshots in virginia found")

    snapshots_per_project = {}
    for snapshot in response['DBSnapshots']:
        if snapshot['Status'] != 'available':
            continue

        if snapshot['DBInstanceIdentifier'] not in snapshots_per_project.keys():
            snapshots_per_project[snapshot['DBInstanceIdentifier']] = {}

        snapshots_per_project[snapshot['DBInstanceIdentifier']][snapshot['DBSnapshotIdentifier']] = snapshot[
            'SnapshotCreateTime']

    for project in snapshots_per_project:
        if len(snapshots_per_project[project]) > 1:
            sorted_list = sorted(snapshots_per_project[project].items(), key=operator.itemgetter(1), reverse=True)
            to_remove = [i[0] for i in sorted_list[1:]]

            for snapshot in to_remove:
                print("Removing " + snapshot)
                virginia_client.delete_db_snapshot(
                    DBSnapshotIdentifier=snapshot
                )

```

"""Return values from query"""
import hashlib
import zipfile
import boto3
import json
from urllib2 import Request, urlopen, URLError, HTTPError
import cx_Oracle
import logging
import os
import datetime

os.environ['TZ'] = 'America/Sao_Paulo'

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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

def lambda_handler(event, context):
    return callOracleResponse()
    
if __name__ == '__main__':
    lambda_handler(None, None)

"""
Summary:
    Boto3 DynamoDB Reader Operations

Module Args:
    DYNAMODB_AWS_ACCOUNT_NR: AWS Account containing DynamoDB table
    DYNAMODB_AWS_ROLE: IAM Role assumed for use of DynamoDB table
"""

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from lambda_utils import read_env_variable

# dynamoDB env
DYNAMODB_AWS_ACCOUNT_NR = read_env_variable('DYNAMODB_AWS_ACCOUNT_NR')
DYNAMODB_AWS_ROLE = read_env_variable('DYNAMODB_AWS_ROLE')



class DynamoDBReader():
    def __init__(self, dynamodb_table, dynamodb_aws_region):
        """
        Reads DynamoDB table
        """
        self.dynamodb_table = dynamodb_table
        self.dynamodb_aws_region = dynamodb_aws_region
        self.aws_credentials = self.assume_role()

    def boto_dynamodb_resource(self, dynamodb_aws_region):
        """
        Initiates boto resource to communicate with AWS API
        """
        try:
            dynamodb_resource = boto3.resource(
                'dynamodb',
                aws_access_key_id=self.aws_credentials['AccessKeyId'],
                aws_secret_access_key=self.aws_credentials['SecretAccessKey'],
                aws_session_token=self.aws_credentials['SessionToken'],
                region_name=dynamodb_aws_region
            )
        except ClientError as e:
            logger.exception("Unknown problem creating boto3 resource (Code: %s Message: %s)" %
                    (e.response['Error']['Code'], e.response['Error']['Message']))
            return 1
        return dynamodb_resource

    def assume_role(self):
        """
        Assumes a DynamoDB role in 'destination' AWS account
        """
        session = boto3.Session()
        sts_client = session.client('sts')

        try:
            assumed_role = sts_client.assume_role(
                RoleArn="arn:aws:iam::%s:role/%s" % (str(DYNAMODB_AWS_ACCOUNT_NR), DYNAMODB_AWS_ROLE),
                RoleSessionName="DynamoDBReaderSession",
            ) # assume role in destination account
        except ClientError as e:
            logger.exception(
                "Couldn't assume role to read DynamoDB, account " +
                str(DYNAMODB_AWS_ACCOUNT_NR) + " (switching role) (Code: %s Message: %s)" %
                (e.response['Error']['Code'], e.response['Error']['Message']))
            return 1
            # don't continue if we can't switch to DynamoDB role
        return assumed_role['Credentials']

    def query_dynamodb(self, partition_key, key_value):
        """
        Queries DynamoDB table using partition key,
        returns the item matching key value
        """

        try:
            resource_dynamodb = self.boto_dynamodb_resource(self.dynamodb_aws_region)
            table = resource_dynamodb.Table(self.dynamodb_table)
            logger.info('Table %s: Table Item Count is: %s' % (table.table_name, table.item_count))

            # query on parition key
            response = table.query(KeyConditionExpression=Key(partition_key).eq(str(key_value)))
            if response['Items']:
                item = response['Items'][0]['Account Name']
            else:
                item = 'unIdentified'

        except ClientError as e:
            logger.exception("Couldn\'t query DynamoDB table (Code: %s Message: %s)" %
                (e.response['Error']['Code'], e.response['Error']['Message']))
            return 1
        return item

    def scan_accounts(self, account_type):
        """
        Read method for DynamoDB table
        """

        accounts, account_ids = [], []
        valid_mpc_pkgs = ['B', 'RA-PKG-B', 'RA-PKG-C', 'P', 'ATA', 'BUP', 'DXA']

        types = [x.strip(' ') for x in account_type.split(',')]    # parse types

        try:
            resource_dynamodb = self.boto_dynamodb_resource(self.dynamodb_aws_region)
            table = resource_dynamodb.Table(self.dynamodb_table)
            # scan table
            if set(types).issubset(set(valid_mpc_pkgs)):
                for type in types:
                    response = table.scan(FilterExpression=Attr('MPCPackage').eq(type))
                    for account_dict in response['Items']:
                        accounts.append(account_dict)
            elif types[0] == 'All':
                # all valid_mpc_pkgs accounts (commercial accounts)
                response = table.scan(FilterExpression=Attr('MPCPackage').ne("P"))
                for account_dict in response['Items']:
                    accounts.append(account_dict)

        except ClientError as e:
            logger.exception("Couldn\'t scan DynamoDB table (Code: %s Message: %s)" %
                    (e.response['Error']['Code'], e.response['Error']['Message']))
            return 1

        if accounts:
            for account in accounts:
                account_info = {}
                account_info['AccountName'] = account['Account Name']
                account_info['AccountId'] = account['Account ID']
                account_ids.append(account_info)
        else:
            logger.info('No items returned from DyanamoDB')
        return account_ids

"""
Summary:
    ec2_utils (python3) | Common EC2 functionality implemented by boto3 SDK

Author:
    Blake Huber
    Copyright Blake Huber, All Rights Reserved.

License:
    Permission to use, copy, modify, and distribute this software and its
    documentation for any purpose and without fee is hereby granted,
    provided that the above copyright notice appear in all copies and that
    both the copyright notice and this permission notice appear in
    supporting documentation

    Additional terms may be found in the complete license agreement located at:
    https://bitbucket.org/blakeca00/lambda-library-python/src/master/LICENSE.md

"""
import os
import json
import socket
import inspect
import boto3
from botocore.exceptions import ClientError
from pyaws.core.session import boto3_session
from pyaws.core import loggers
from pyaws._version import __version__


# global objects
REGION = os.environ['AWS_DEFAULT_REGION']

# lambda custom log object
logger = loggers.getLogger(__version__)


# -- declarations -------------------------------------------------------------


def get_instances(region, profile=None):
    """
    Returns: all EC2 instance Ids in a region
    """
    vm_ids = []
    try:
        if profile:
            session = boto3.Session(profile_name=profile, region_name=region)
            client = session.client('ec2')
        else:
            client = boto3.client('ec2', region_name=region)
        r = client.describe_instances()
        for detail in [x['Instances'] for x in r['Reservations']]:
            for instance in detail:
                vm_ids.append(instance['InstanceId'])
    except ClientError as e:
        logger.critical(
            "%s: problem retrieving instances in region %s (Code: %s Message: %s)" %
            (inspect.stack()[0][3], str(region), e.response['Error']['Code'],
            e.response['Error']['Message']))
        raise e
    return vm_ids


def get_regions(profile):
    """ Return list of all regions """
    try:
        if not profile:
            profile = 'default'
        client = boto3_session(service='ec2', profile=profile)

    except ClientError as e:
        logger.exception('%s: Boto error while retrieving regions (%s)' %
            (inspect.stack()[0][3], str(e)))
        raise e
    return [x['RegionName'] for x in client.describe_regions()['Regions']]


def dns_hostname(instanceId, profile='default'):
    """
    Summary:
        Reverse DNS for EC2 instances public or private subnets
        Really only useful when EC2 instance assigned non-AWS DNS name
    Args:
        ip_info (dict):
            {
                "Association": {
                    "IpOwnerId": "102512488663",
                    "PublicDnsName": "ec2-34-247-23-51.eu-west-1.compute.amazonaws.com",
                    "PublicIp": "34.247.23.51"
                },
                "Primary": true,
                "PrivateDnsName": "ip-172-31-28-93.eu-west-1.compute.internal",
                "PrivateIpAddress": "172.31.28.93"
            }
    Returns:
        hostname (tuple): First element of the following tuple:
            (
                'ec2-34-247-23-51.eu-west-1.compute.amazonaws.com',
                ['34.247.23.51'],
                'ip-172-31-28-93.eu-west-1.compute.internal',
                ['172.31.28.93']
            )
    """
    try:
        session = boto3.Session(profile_name=profile)
        client = session.client('ec2', region_name=REGION)
        r = client.describe_instances(InstanceIds=[instanceId])
        # dict of ip information
        ip_info = [x['PrivateIpAddresses'][0] for x in r['Reservations'][0]['Instances'][0]['NetworkInterfaces']][0]
        private_name = r['Reservations'][0]['Instances'][0]['PrivateDnsName']
        public_name = r['Reservations'][0]['Instances'][0]['PublicDnsName']
        """
        if ip_info.get('Association'):
            public_ip = ip_info['Association']['PublicIp']
            priv_ip = ip_info['PrivateIpAddress']
        else:
            public_ip = ''
            priv_ip = ip_info['PrivateIpAddress']
        return (
                socket.gethostbyaddr(public_ip),
                [public_ip],
                socket.gethostbyaddr(priv_ip),
                [priv_ip]
            )
        """
    except KeyError as e:
        logger.exception('%s: KeyError parsing ip info (%s)' % (inspect.stack()[0][3], str(e)))
        return ('', [], '', [])
    except ClientError as e:
        logger.exception('%s: Boto Error parsing ip info (%s)' % (inspect.stack()[0][3], str(e)))
        return ''
    except Exception:
        logger.exception(
            '%s: No dns info from reverse lookup - Unknown host' % inspect.stack()[0][3])
        return ('', [], '', [ip_info['PrivateIpAddress']])
    return public_name or private_name

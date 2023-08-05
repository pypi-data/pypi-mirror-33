"""
Pretest Setup | pytest

    Calls set_environment() on module import
"""
import os
import subprocess
import inspect
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def awscli_region(profile_name):
    """
    Summary:
        Extracts the STS AccessKeyId currently utilised in user's
        profile in the local awscli configuration
    Args:
        profile_name:  a username in local awscli profile
    Returns:
        key_id (str): Amazon STS AccessKeyId
    Raises:
        Exception if profile_name not found in config
    """

    awscli = 'aws'
    cmd = 'type ' + awscli + ' 2>/dev/null'

    if subprocess.getoutput(cmd):
        cmd = awscli + ' configure get ' + profile_name + '.region' + ' 2>/dev/null'
    try:
        region = subprocess.getoutput(cmd)
    except Exception as e:
        logger.exception(
            '%s: Failed to identify AccessKeyId used in %s profile.' %
            (inspect.stack()[0][3], profile_name))
        return ''
    return region


def set_default_region():
    """
    Sets AWS default region globally
    """
    if os.getenv('AWS_DEFAULT_REGION'):
        return os.getenv('AWS_DEFAULT_REGION')
    else:
        # determine default region from awscli
        default_region = awscli_region(profile_name='default')
        if not default_region:
            default_region = 'us-east-2'
    return default_region


def set_environment():
    """
    Sets global environment variables for testing
    """
    # status

    logger.info('setting global environment variables')

    # set all env vars
    os.environ['DBUGMODE'] = 'False'
    os.environ['AWS_DEFAULT_REGION'] = set_default_region()

    logger.info('AWS_DEFAULT_REGION determined as %s' % os.environ['AWS_DEFAULT_REGION'])


# execute on import
set_environment()

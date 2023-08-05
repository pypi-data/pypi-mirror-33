"""
lambda job to profile lambda container
    http://www.cloudtrek.com.au/blog/running-python-3-on-aws-lambda/
"""

import os
import subprocess

def lambda_handler(event, context):
    # print out Linux distro
    txt = open(’/etc/issue’)
    print("Lamda Environment Profile -- Begin")
    print txt.read()

   # check Linux kernel version
    args = (“uname”,“-a”)
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    print(output)

    # locate python3
     args = (“whereis”,“python3”)
     popen = subprocess.Popen(args, stdout=subprocess.PIPE)
     popen.wait()
     output = popen.stdout.read()
     print(output)
     print("Lamda Environment Profile -- End")

'''
    # build python3 venv
    args = (“venv/bin/python3.4 ”, “python3_thingamee.py”)
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    print(output)
'''

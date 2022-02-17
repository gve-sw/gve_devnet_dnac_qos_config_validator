#!/usr/bin/env python3
"""
#Copyright (c) 2020 Cisco and/or its affiliates.
#
#This software is licensed to you under the terms of the Cisco Sample
#Code License, Version 1.1 (the "License"). You may obtain a copy of the
#License at
#
#               https://developer.cisco.com/docs/licenses
#
#All use of the material herein must be in accordance with the terms of
#the License. All rights not expressly granted by the License are
#reserved. Unless required by applicable law or agreed to separately in
#writing, software distributed under the License is distributed on an "AS
#IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#or implied.
"""
import requests
import time
import pprint
import urllib3
import json

urllib3.disable_warnings()

def getAuthToken(env):
    """
    Intent-based Authentication API call
    The token obtained using this API is required to be set as value to the X-Auth-Token HTTP Header
    for all API calls to Cisco DNA Center.
    :param env:
    :return: Token STRING
    """
    url = '{}/dna/system/api/v1/auth/token'.format(env['base_url'])
    # Make the POST Request
    response = requests.post(url, auth=(env['username'], env['password']), verify=False)

    # Validate Response
    if 'error' in response.json():
        print('ERROR: Failed to retrieve Access Token!')
        print('REASON: {}'.format(response.json()['error']))

    else:
        token = response.json()['Token']
        return token  #return only the token


def getDnacDevices(env):
    url = '{}/dna/intent/api/v1/network-device'.format(env['base_url'])
    headers = {
        'x-auth-token': env['token'],
        'Content-Type': 'application/json',
        'Accept': 'application/json'
        }
    # Make the GET Request
    response = requests.get(url, headers=headers, verify=False)

    # Validate Response
    if 'error' in response.json():
        print('ERROR: Failed to retrieve Network Devices!')
        print('REASON: {}'.format(response.json()['error']))
        return []
    else:
        return response.json()['response'] #return the list of dnac devices


def getTask(env, task_id):
    url = "{}/dna/intent/api/v1/task/{}".format(env["base_url"], task_id)
    headers = {
        "x-auth-token": env["token"],
        "Content-Type": "application/json",
        }

    # Make GET request
    response = requests.get(url, headers=headers, verify=False)

    return response.json() #return response with information about specific task


def getDeviceById(env, device_id):
    url = "{}/dna/intent/api/v1/network-device/{}".format(env["base_url"], device_id)
    headers = {
        "x-auth-token": env["token"],
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, verify=False)

    return response.json()


def commandRunner(env, commands, deviceIds):
    url = "{}/dna/intent/api/v1/network-device-poller/cli/read-request".format(env["base_url"])
    headers = {
        "x-auth-token": env["token"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "commands": commands,
        "deviceUuids": deviceIds,
        "timeout": 0
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)

    return response.json()


def getFileById(env, file_id):
    url = "{}/dna/intent/api/v1/file/{}".format(env["base_url"], file_id)
    headers = {
        "x-auth-token": env["token"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, verify=False)

    return response.json()


def getPhysicalTopology(env):
    url = "{}/dna/intent/api/v1/topology/physical-topology".format(env["base_url"])
    headers = {
        "x-auth-token": env["token"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, verify=False)

    return response.json()

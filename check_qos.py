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
from dnac import *
from env import env
import sys
from datetime import datetime
from pprint import pprint


"""This function finds which access points and switches are in this network.
Then it checks the topology of the network and finds which switches the APs are
plugged into. The function returns a dictionary that maps the IDs of the
access points to the switch they are connected to (by id and series name) and
the interface of the switch where the access point is plugged in."""
def findAPs(env):
    devices = getDnacDevices(env)
    ap_ids = [] #list of AP IDs in DNA Center environment
    switches = {} #dictionary of switches - the key is the switch ID and the value is the switch series

    for device in devices:
        if "AP" in device["family"]:
            ap_ids.append(device["id"])
        elif "Switch" in device["family"]:
            if device["id"] not in switches.keys(): #if switch has not already been found, add it to dictionary
                switches[device["id"]] = device["series"]

    topology = getPhysicalTopology(env)
    links = topology["response"]["links"]
    ap_switches = {} #this dictionary is going to map the APs to the switches they're connected to - the key is the AP ID and the value is a dictionary with switch information and the switchport where the AP is connected

    #the topology links reveal where aps are connected to switches
    for link in links:
        if link["source"] in ap_ids:
            if link["target"] in switches.keys():
                device = getDeviceById(env, link["target"])
                ip = device["response"]["managementIpAddress"]
                switch = {
                    "id": link["target"],
                    "series": switches[link["target"]],
                    "ip": ip
                }
                ap_switches[link["source"]] = {
                    "switch": switch,
                    "interface": link["endPortName"]
                }

    return ap_switches


"""This function retrieves the running configuration of a given interface. Then
it checks the lines of the configuration for the line of code "auto qos trust
dscp" if the switch is a Catalyst 9000 series or "auto qos trust" if the switch
is any other series"""
def checkConfigs(env, check_devices, device_model, interface):
    commands = ["show run int {}".format(interface)]
    running_config = commandRunner(env, commands, check_devices) #run show run int command on given switches
    time.sleep(2) #pause program for 2 seconds to give DNAC time to perform the request

    task_id = running_config["response"]["taskId"]
    task = getTask(env, task_id)
    while "fileId" not in task["response"]["progress"]: #until the key "fileId" is found in the response, keep retrieving the task
        task = getTask(env, task_id)

    task_progress = json.loads(task["response"]["progress"])
    file_id = task_progress["fileId"]
    file_json = getFileById(env, file_id)
    successful_response = file_json[0]["commandResponses"]["SUCCESS"] #a successful response is indicated by the key "SUCCESS"
    if successful_response:
        running_config_lines = successful_response["show run int {}".format(interface)].splitlines()
        pprint(running_config_lines) #print the results of the command

        line_exists = False

        for line in running_config_lines: #check config for line of code
            if "Catalyst 9" in device_model and "auto qos trust dscp" in line:
                line_exists = True
            elif "Catalyst 9" not in device_model and "auto qos trust" in line:
                line_exists = True

        return line_exists
    else:
        print("There was an issue retrieving the running configuration...")
        print(file_json[0]["commandResponses"]["FAILURE"])

        sys.exit(1)


"""This function creates a file that is named with the current datetime and
contains the switch information of the switches that APs are connected to and
need configuration. The file should contain the exact lines of configuration
that the switch needs depending on its model series."""
def writeFile(filename, aps_and_switches):
    with open(filename, 'w+') as f:
        for ap in aps_and_switches:
            if not aps_and_switches[ap]["config"]: #config is false, so the line of code is needed
                switch_id = aps_and_switches[ap]["switch"]["id"]
                switch_series = aps_and_switches[ap]["switch"]["series"]
                switch_ip = aps_and_switches[ap]["switch"]["ip"]
                interface = aps_and_switches[ap]["interface"]

                if "Catalyst 9300" in switch_series:
                    data = """Switch {} has an IP address of {} and is a Catalyst
9300 series. It needs the following configuration on interface {} where AP {}
is connected:
configure terminal
interface {}
auto qos trust dscp\n\n""".format(switch_id, switch_ip, interface, ap, interface)
                elif "Catalyst 9400" in switch_series:
                    data = """Switch {} has an IP address of {} and is a Catalyst
9400 series. It needs the following configuration on interface {} where AP {}
is connected:
configure terminal
interface {}
auto qos trust dscp\n\n""".format(switch_id, switch_ip, interface, ap, interface)
                elif "Catalyst 4500" in switch_series:
                    data = """Switch {} has an IP address of {} and is a Catalyst
4500. It needs the following configuration on interface {} where AP {} is
connected:
configure terminal
interface {}
auto qos trust\n\n""".format(switch_id, switch_ip, interface, ap, interface)
                else:
                    data = """Switch {} has an IP address of {} and is not a
Catalyst 9300, 9400, or 4500. It needs the following configuration on interface
{} where AP {} is connected:
configure terminal
interface {}
auto qos trust\n\n""".format(switch_id, switch_ip, interface, ap, interface)

                f.write(data)

token = getAuthToken(env) #token needed for future API requests
env["token"] = token

aps_and_switches = findAPs(env) #find APs and the switches they're connected to
for ap in aps_and_switches:
    connect_info = aps_and_switches[ap]
    switch_id = connect_info["switch"]["id"]
    switch_series = connect_info["switch"]["series"]
    interface = connect_info["interface"]

    line_exists = checkConfigs(env, [switch_id], switch_series, interface) #check configuration of switchport with AP connected to it
    connect_info["config"] = line_exists #True if the config exists and false if config is needed
    aps_and_switches[ap] = connect_info

now = datetime.now()
dt_str = now.strftime("%m-%d-%Y_%H:%M:%S")
filename = dt_str + "_configs.txt"

writeFile(filename, aps_and_switches) #write the file which indicates what needs configuration

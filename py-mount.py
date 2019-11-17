#!/usr/bin/python3

"""
Example configuration file in JSON format
[
    {
        "target": "/path/to/target/dir1",
        "destination": "/path/to/destination/dir1"
    }, {
        "target": "/path/to/target/dir2",
        "destination": "/path/to/destination/dir2"
    }
]
"""

# imports
import sys
import os
import json
import argparse 

# functions
def checkRoot():
    return (os.getuid() == 0)

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', default='mount')
    parser.add_argument('-f', '--file', default='config.json')
    return parser

def parseArguments():
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    if not namespace.file.endswith('.json'):
        namespace.file = namespace.file + '.json'
    return namespace

# main
IS_ROOT = (os.getuid() == 0)
if not checkRoot():
    print("Use sudo!")
    sys.exit()

args = parseArguments();

command = {
    'mount': 'sudo mount --bind "__TARGET__" "__DESTINATION__"',
    'unmount': 'sudo umount "__DESTINATION__"',
}

config = None
with open(args.file) as content:
    config = json.load(content)

if config is None:
    print("Config file not exists")
    sys.exit()

for item in config:
    cmd = command[args.action]
    cmd = cmd.replace('__TARGET__', item['target'])
    cmd = cmd.replace('__DESTINATION__', item['destination'])
    os.system(cmd)

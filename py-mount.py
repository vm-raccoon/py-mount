#!/usr/bin/python3

"""
Required:
    sshfs

Example configuration file in JSON format
[
    {
        "type": "local",        
        "target": "/path/to/target/dir1",
        "destination": "/path/to/destination/dir1",
        "local_username": "LOCAL_USERNAME",
        "remove_after_umount": true
    }, {
        "type": "ssh",
        "username": "USERNAME",
        "password": "PASSWORD",
        "host": "HOST",
        "target": "/path/to/target/dir2",
        "destination": "/path/to/destination/dir2",
        "local_username": "LOCAL_USERNAME",
        "remove_after_umount": true
    }
]
"""

# imports
import sys
import os
import json
import argparse
from pwd import getpwnam

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
    'local': {
        'mount': 'sudo mount --bind "__TARGET__" "__DESTINATION__"',
        'umount': 'sudo umount "__DESTINATION__"',
    },
    'ssh': {
        'mount': 'echo __PASSWORD__ | sudo sshfs -o allow_other -o password_stdin __USERNAME__@__HOST__:"__DESTINATION__" "__TARGET__"',
        'umount': 'sudo umount "__DESTINATION__"',
    },
}

if not os.path.isfile(args.file):
    print("Config file not exists")
    sys.exit()

config = None
with open(args.file) as content:
    config = json.load(content)

if config is None:
    print("Config is none")
    sys.exit()

for item in config:
    if not item['type'] in command:
        continue
    cmd = command[item['type']][args.action]
    cmd = cmd.replace('__TARGET__', item['target'])
    cmd = cmd.replace('__DESTINATION__', item['destination'])
    if item['type'] == 'ssh':
        cmd = cmd.replace('__USERNAME__', item['username'])
        cmd = cmd.replace('__PASSWORD__', item['password'])
        cmd = cmd.replace('__HOST__', item['host'])
    if args.action == 'mount':
        if not os.path.isdir(item['destination']):
            os.makedirs(item['destination'], 777)
        user = getpwnam(item['local_username'])
        os.chown(item['destination'], user.pw_uid, user.pw_gid)
    os.system(cmd)
    if args.action == 'umount':
        if item['remove_after_umount']:
            os.rmdir(item['destination'])


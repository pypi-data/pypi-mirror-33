#!/usr/bin/env python
import json
import sys
import getpass
import subprocess
import shlex
import argparse

def validate():
    result = subprocess.check_output


def get_cmd(name):

    result = subprocess.check_output(shlex.split('sudo docker inspect %s' % (name)))

    data = json.loads(result)

    command='docker run \\ \n'

    name = data[0]['Name']
    command+='    --name={} \\ \n'.format(name)

    ulimits=data[0]['HostConfig']['Ulimits']
    if ulimits:
        command+='    --ulimit {}={}:{} \\ \n'.format(ulimits[0]['Name'],ulimits[0]['Hard'],ulimits[0]['Soft'])

    envs = data[0]['Config']['Env']
    if envs:
        for env in envs:
            command+='    --env="{}" \\ \n'.format(str(env))

    networks = data[0]["NetworkSettings"]["Networks"]
    if networks:
        for network in networks:
            command+='    --network {} \\ \n'.format(network)

    volumes = data[0]['HostConfig']['Binds']
    if volumes:
        for volume in volumes:
            command+='    --volume="{}" \\ \n'.format(volume)

    labels = data[0]['Config']['Labels']
    if labels:
        for key,value in labels.iteritems():
            command+='    --label "{}"="{}" \\ \n'.format(key,value)

    logdriver = data[0]['HostConfig']['LogConfig']
    if logdriver:
        command+='    --log-driver="{}" \\ \n'.format(logdriver['Type'])

    restart=data[0]['HostConfig']['RestartPolicy']
    if restart:
        command+='    --restart="{}" \\ \n'.format(restart['Name'])

    detach=data[0]['Config']['AttachStdout']
    if not detach:
        command+='    --detach=true \\ \n'

    config_image=data[0]['Config']['Image']
    if config_image:
        command+='    "{}"'.format(config_image)

    config_cmds=data[0]['Config']['Cmd']
    if config_cmds:
        command+=' \\ \n'
        for cmd in config_cmds:
            command+='"{}" '.format(cmd)
    else:
        command+='\n'

    print '#'+'-'*20+'Copy below this line'+'-'*20
    print command+"\n"


if __name__=='__main__':
    result = subprocess.check_output(shlex.split('sudo docker ps -a --format "{{.ID}} {{.Names}}"'))
    help="Choose from below containers\nID           Name\n"+result

    parser = argparse.ArgumentParser(description='Retrieve Docker Run Command from existing container',
                formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('name', action="store", help='docker container name\n\n'+help)
    results = parser.parse_args()
    name = results.name
    get_cmd(name)
#! /usr/bin/env python

"""
Usage:
    add_oneagent.py  <file>
    add_oneagent.py --in-place </path/to/file.yml>
    add_oneagent.py --version
    add_oneagent.py --help

Options:
    --help     Script parses Kubernetes deployment file, inserts necessary OneAgent configuration blocks and returns valid yaml, that's ready for deployment
    --in-place Will patch file where it is placed
"""

import sys
import oyaml as yaml
from docopt import docopt

__version__ = '2.0.0-github'


def main():
    def insert_oneagent(path_to_file):
        stream = open(path_to_file, 'r')
        parsed_yaml = yaml.load(stream)
        ld_preload = {"name": "LD_PRELOAD", "value": "/app/oneagent/agent/lib64/liboneagentproc.so"}
        dtenvvar = {"secretRef": {"name": "dynatrace"}}
        volume_mount = {"name": "oneagent", "value": "/app/oneagent"}
        volume = {"name": "oneagent", "emptyDir": "{}"}
        init_container = {
              "name": "install-oneagent",
              "image": "alpine:3.8",
              "command": [
                "/bin/sh"
              ],
              "args": [
                "-c",
                "ARCHIVE=$(mktemp) && wget -O $ARCHIVE \"$DT_API_URL/v1/deployment/installer/agent/unix/paas/latest?Api-Token=$DT_PAAS_TOKEN&$DT_ONEAGENT_OPTIONS\" && unzip -o -d /opt/dynatrace/oneagent $ARCHIVE && rm -f $ARCHIVE"
              ],
              "env": [
                {
                  "name": "DT_API_URL",
                  "value": "https://<Your-environment-ID>.live.dynatrace.com/api"
                },
                {
                  "name": "DT_PAAS_TOKEN",
                  "value": "<paastoken>"
                },
                {
                  "name": "DT_ONEAGENT_OPTIONS",
                  "value": "flavor=<FLAVOR>&include=<TECHNOLOGY>"
                }
              ],
              "volumeMounts": [
                {
                  "mountPath": "/app/oneagent",
                  "name": "oneagent"
                }
              ]
        }

        if 'env' not in parsed_yaml['spec']['template']['spec']['containers'][0].keys():
            parsed_yaml['spec']['template']['spec']['containers'][0]['env'] = list()
        parsed_yaml['spec']['template']['spec']['containers'][0]['env'].append(ld_preload)

        if 'envFrom' not in parsed_yaml['spec']['template']['spec']['containers'][0].keys():
            parsed_yaml['spec']['template']['spec']['containers'][0]['envFrom'] = list()
        parsed_yaml['spec']['template']['spec']['containers'][0]['envFrom'].append(dtenvvar)

        if 'volumeMounts' not in parsed_yaml['spec']['template']['spec']['containers'][0].keys():
            parsed_yaml['spec']['template']['spec']['containers'][0]['volumeMounts'] = list()
        parsed_yaml['spec']['template']['spec']['containers'][0]['volumeMounts'].append(volume_mount)

        if 'initContainers' not in parsed_yaml['spec']['template']['spec'].keys():
            parsed_yaml['spec']['template']['spec']['initContainers'] = list()
        parsed_yaml['spec']['template']['spec']['initContainers'].append(init_container)

        if 'volumes' not in parsed_yaml['spec']['template']['spec'].keys():
            parsed_yaml['spec']['template']['spec']['volumes'] = list()
        parsed_yaml['spec']['template']['spec']['volumes'].append(volume)

        return parsed_yaml

    if arguments.get("--in-place"):
        path_to_file = arguments.get("--in-place")
        patched_yaml = insert_oneagent(path_to_file)
        file = open(path_to_file, 'w')
        file.write(yaml.dump(patched_yaml))
        file.close()
    elif arguments.get('<file>'):
        path_to_file = arguments.get('<file>')
        patched_yaml = insert_oneagent(path_to_file)
        print(yaml.dump(patched_yaml))


if __name__ == "__main__":
    arguments = docopt(__doc__, version=__version__)
    main()

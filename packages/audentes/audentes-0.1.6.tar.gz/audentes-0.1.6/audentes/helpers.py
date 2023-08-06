import sys

import os
import ruamel.yaml as yaml


def docker_compose_command_with_file(file_name):
    def docker_compose_command(command, silent=False):
        cmd = "docker-compose -f {} {}".format(file_name, command)
        if not silent:
            print("> {}".format(cmd))
        process = os.popen(cmd)
        process_output = process.read()
        exit_code = process.close()
        return exit_code, process_output

    return docker_compose_command


def load_yml(file_name):
    with open(file_name) as yml_stream:
        return yaml.safe_load(yml_stream)


def fail(error):
    print(error)
    sys.exit(1)

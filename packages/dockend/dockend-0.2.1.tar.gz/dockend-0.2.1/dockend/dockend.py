#!/usr/bin/env python
from termcolor import cprint
import argparse
import docker
DOCKER_CLIENT = docker.from_env()


def main():
    try:
        not_found_for_stop = False
        not_found_for_start = False
        ARGS = parser_arguments()
        k_name_stop = 'byr' if ARGS.service == 'dla' else 'dev'
        k_name_start = 'dev' if ARGS.service == 'dla' else 'byr'
        containers_for_stop = docker_containers_list(k_name_stop)
        containers_for_start = docker_containers_list(k_name_start)
        if containers_for_stop:
            stop_containers(containers_for_stop, k_name_stop)
        else:
            cprint("WARNING! Active containers for stop not found", 'yellow')
            not_found_for_stop = True
        if containers_for_start:
            start_containers(containers_for_start, k_name_start)
        else:
            cprint("WARNING! Active containers for start not found", 'yellow')
            not_found_for_start = True
        if not not_found_for_start:
            cprint("DONE! Happy Coding", "white", "on_green")
        if not_found_for_start and not_found_for_stop:
            cprint(
                "STOP! Maybe you have problems with the containers. e.g. Containers not build", "white", "on_red")
    except Exception:
        cprint("ERROR! Docker is off or not installed", "white", "on_red")
        exit(1)


def start_containers(container_lists, k_name):
    try:
        cprint("Start containers {}...".format(k_name), 'yellow')
        for cont in container_lists:
            cont.start()
        cprint("OK containers {} up!".format(k_name), 'green')
    except Exception as exc:
        cprint("Error when starting the process (container starting process): {}".format(
            exc), 'white', 'on_red')
        exit(1)


def stop_containers(container_lists, k_name):
    try:
        cprint("Stop containers {}...".format(k_name), 'yellow')
        for cont in container_lists:
            cont.stop()
        cprint("OK containers {} down!".format(k_name), 'green')
        return True
    except Exception as exc:
        cprint("Error when starting the process (container stopping process): {}".format(
            exc), 'white', 'on_red')
        exit(1)


def docker_containers_list(key_name):
    try:
        return DOCKER_CLIENT.containers.list(filters={'name': key_name}, all=True)
    except Exception as exc:
        cprint("Error getting the list: {}".format(exc), 'red')
        raise exc


def parser_arguments():
    parser = argparse.ArgumentParser(
        description='Tool for change backend services and process in docker environment (BYR-Microservicios/API-Integrada)')
    parser.add_argument('-V',
                        '--version',
                        action='version',
                        version='%(prog)s {version}'.format(version='0.2.1'))
    parser.add_argument('service',
                        choices=['byr', 'dla'],
                        type=str,
                        help='backend type')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()

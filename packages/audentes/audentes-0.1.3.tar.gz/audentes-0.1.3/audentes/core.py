import atexit

from time import sleep

import concurrent
import socket
import requests
import pprint
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from .helpers import docker_compose_command_with_file
from .helpers import load_yml
from .helpers import fail


class System:

    def __init__(self, file_name):
        self.file_name = file_name
        self.definition = load_yml(file_name)
        self.command = docker_compose_command_with_file(file_name)

    def start(self):
        atexit.register(self.command, "down")
        result, _ = self.command("up -d")
        if result is not None:
            fail("Docker compose failed to start. Exited with {}".format(result))

    def services(self):
        return self.definition["services"]

    def service_by_name(self, service_name):
        return self.definition["services"][service_name]

    def describe(self):
        pprint.pprint(self.definition)

    def exec(self, service, bash_command):
        return self.command("exec -T {} {}".format(service, bash_command))

    def endpoint(self, service, internal_port=None):
        if service not in self.definition["services"]:
            fail("{} not defined in {}".format(service, self.file_name))

        if internal_port is None:
            if len(self.definition["services"][service]["ports"]) == 1:
                internal_port = self.definition["services"][service]["ports"][0]
            else:
                fail("Must define internal port for service {} as it's exposing multiple ports.")

        return Endpoint(self, service, internal_port)
        

    def wait_for_service(self, service, internal_port=None, response_code=200, path="", timeout=30):
        """

        :param service: The service name in the docker compose file.
        :param internal_port: Will wait for the exposed internal port if no port is provided.
        :param response_code: Which response code is expected.
        :param endpoint: If no endpoint is provided the function will wait for /.
        :param timeout: The time allowed for the service to respond. Defaults to 30 s.
        """


        return wait_for_service(self.endpoint(service, internal_port), response_code=response_code, path=path, timeout=timeout)


def load_system(file_name="docker-compose.yml"):
    """
    Loads and returns system that is defined in a docker compose file.

    :param file_name: the path to the docker compose file. Defaults to docker-compose.yml
    :return: A system instance.
    """
    return System(file_name)


def wait_for_port(port, timeout=30):
    c = None
    try:
        c = socket.create_connection(("localhost", port), timeout)
        print(c)
    except:
        print(":|")
    finally:
        if c is None:
            c.close()


class WaitForService:
    def __init__(self, endpoint, path, expected_response_code=200, timeout=30):
        self.endpoint = endpoint
        self.path = path
        self.timeout = timeout
        self.expected_response_code = expected_response_code
        self.interrupt_requested = False


    def __call__(self):

        response_code = 0
        while self.expected_response_code != response_code:
            if self.interrupt_requested:
                return False
            try:
                url = "http://{}/{}".format(self.endpoint.host(), self.path)
                response = requests.get(url, timeout=self.timeout)
                response_code = response.status_code
                print("Connected to {}:{} using external {}.".format(self.endpoint.service, self.endpoint.internal_port, self.endpoint.host()))

            except requests.exceptions.ConnectionError:
                print("Waiting for {}:{}".format(self.endpoint.service, self.endpoint.internal_port))
                sleep(1.0)
                pass

        return True

    def interrupt(self):
        self.interrupt_requested = True


def wait_for_service(endpoint, response_code=200, path="", timeout=30):

    print("Waiting for service {}:{}".format(endpoint.service, endpoint.internal_port))

    with ThreadPoolExecutor(max_workers=1) as executor:
        wait_for = WaitForService(endpoint, path, response_code)
        future = executor.submit(wait_for)

        success = False
        try:
            success = future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            wait_for.interrupt_requested = True

    if not success:
        fail("Service {}:{} did not respond with {} in {} s.".format(endpoint.service, endpoint.internal_port, response_code, timeout))


class Endpoint:

    def __init__(self, system, service, internal_port):
        self.internal_port = internal_port
        self.system = system
        self.service = service

    def host(self):
        exit_code, output = self.system.command("port {} {}".format(self.service, self.internal_port), silent=True)
        if exit_code is not None:
            fail("Could not determine external port for service {} and internal port {}".format(self.service, self.internal_port))
        host = output.strip()
        return host
import requests
import unittest
from .context import audentes


class AudentesTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_starting_and_waiting(self):
        audentes.DEBUG = True
        system = audentes.load_system("./tests/docker-compose.yml")
        system.start()
        system.wait_for_service("web")

        host = system.endpoint("web").host()

        response = requests.get("http://{}/".format(host))

        assert response.status_code == 200



if __name__ == '__main__':
    unittest.main()

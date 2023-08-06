Audentes
========

A package for writing component tests with docker compose

Example:

docker-compose.yml

~~~~
version: '2.1'
services:
  web:
    image: nginx
    ports:
     - "80"
~~~~


test.py

~~~~
import audentes
import requests

system = audentes.load_system() #Defaults to docker-comose.yml
system.start()
system.wait_for_service("web")  #Waits for web service to respond with status code 200 on /

host = system.endpoint("web").host() # Now we can do some testing
response = requests.get("http://{}/".format(host))

assert response.status_code == 200 # Assert that we get the response we expect
~~~~
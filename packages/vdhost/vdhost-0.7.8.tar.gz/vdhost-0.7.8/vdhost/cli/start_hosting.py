import click
import subprocess
import os
import requests
import json

from colored import fg
from colored import stylize
from os import environ

if environ.get('VECTORDASH_BASE_URL'):
    VECTORDASH_URL = environ.get('VECTORDASH_BASE_URL')
else:
    VECTORDASH_URL = "http://vectordash.com/"


@click.command(name='start-hosting')
def start_hosting():
    """
    Connects this machine to the Vectordash server.
    """
    try:

        # if the installation has not been completed
        if not os.path.isfile('/var/vectordash/install_complete'):
            print("The Vectordash client has not been installed. Please run " +
                  stylize("sudo vdhost install", fg("blue")))
            return

        # ensuring the login file exists
        if not os.path.isfile('/var/vectordash/login.json'):
            print("You are not logged in. Please run " +
                  stylize("vdhost login", fg("blue")) + ' to continue.')
            return

        # opening the credentials JSON
        with open('/var/vectordash/login.json', 'r') as f:
            data = json.load(f)

        # grabbing the values
        email = data["email"]
        machine_key = data["machine_key"]

        # ensuring the login information is valid
        r = requests.post(VECTORDASH_URL + "authenticate-host/", data={'email': email, 'machine_key': machine_key})

        # getting the response and loading it as a dict
        resp = r.text
        resp = json.loads(resp)

        # if the login failed we display an error and return
        if not resp['valid_authentication']:
            print("Invalid authentication information . Please run " +
                stylize("vdhost login", fg("blue")) + ' to continue.')
            return

        # Launching the the client script
        subprocess.call("sudo supervisorctl start vdclient", shell=True)

        # Printing a success message
        print(stylize("Vectordash client started.", fg("green")))

    except OSError:  # if we get a permissions error
        print(stylize("Please run this command as sudo:", fg("red"))
              + stylize("sudo vdhost start-hosting", fg("blue")))

    except Exception as e:
        print(stylize("An unexpected error has occurred: " + str(e), fg("red")))

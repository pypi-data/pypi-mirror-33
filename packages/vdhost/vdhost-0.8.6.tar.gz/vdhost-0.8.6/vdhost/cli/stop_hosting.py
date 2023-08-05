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


@click.command(name='stop')
def stop_hosting():
    """
    Stops the Vectordash client.
    """

    try:

        # ensuring the login file exists
        if not os.path.isfile('/var/vectordash/login.json'):
            print("You are not logged in. Please run " +
                  stylize("vdhost login", fg("blue")) + ' to continue.')
            return

        # if the installation process has not been completed
        if not os.path.isfile('/var/vectordash/install_complete'):
            print("You are not currently running the Vectordash hosting client because you have not setup your machine "
                  "yet. Please run " + stylize("vdhost install", fg("blue")) + " first.")
            return

        # we must check for active instances before stopping vdclient
        with open('/var/vectordash/login.json') as f:
            data = json.load(f)

        # reading in the login credentials
        email = data["email"]
        machine_key = data["machine_key"]

        # getting the active instance count for this machine
        r = requests.post(VECTORDASH_URL + "active-instance-count/",
                          data={'email': email, 'machine_key': machine_key})

        # if there was an error with the response
        if r.status_code != 200:
            print(stylize("An unexpected error has occurred. Please try again later.", fg("red")))
            return

        # getting the value from the response
        resp = r.text
        resp = json.loads(resp)
        num_instances = int(resp['active_instances'])

        # if it's a negative integer, authentication was invalid
        if num_instances < 0:
            print("Invalid authentication information . Please run " +
                  stylize("vdhost login", fg("blue")) + ' to continue.')
            return

        elif num_instances > 0:
            print(stylize("Please keep the client online until all active instances have been completed.",
                          fg("red")))
            return

        else:

            # calling stop on vclient, note that supervisor prints out a message for us
            subprocess.call("sudo supervisorctl stop vdhost", shell=True)

    except OSError:

        # if we get a permissions error
        print(stylize("Please run this command as sudo:", fg("red"))
              + stylize("sudo vdhost start-miner <gpu_id>", fg("blue")))

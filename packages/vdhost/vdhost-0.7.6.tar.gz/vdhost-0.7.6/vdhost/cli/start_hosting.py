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
    print('Using development URL:' + VECTORDASH_URL)
else:
    VECTORDASH_URL = "http://vectordash.com/"


@click.command(name='start-hosting')
def start_hosting():
    """
    args: None | Connects this machine to the Vectordash server.
    """
    try:
        # Path to vectordash client directory
        client_dir = '/var/vectordash/client'

        # If the var directory does not exist,
        if not os.path.isdir(client_dir):
            print(stylize("Error getting package. You have not ran ", fg("red")) + stylize("vdhost login", fg("blue")))
            exit(0)

        # if the installation has not been completed
        if not os.path.isfile('/var/vectordash/install_complete'):
            print("Installation has not been completed/ Please run " +
                  stylize("sudo vdhost install", fg("blue")))
            exit(0)

        # path to login file
        login_file = os.path.expanduser('/var/vectordash/login.json')
        
        try:
            with open(login_file, 'r') as f:
                data = json.load(f)
                email = data["email"]
                machine_key = data["machine_key"]
                r = requests.post(VECTORDASH_URL + "authenticate-host/",
                                  data={'email': email, 'machine_key': machine_key})
                resp = r.text
                resp = json.loads(resp)

                # if the login failed
                if not resp['valid_authentication']:
                    print(stylize("Invalid login, please run ", fg("red")) + stylize("vdhost login", fg("blue")))
                    exit(0)

        except Exception as e:
            print(stylize("An error occurred, Please make sure you have run ", fg("red")) +
                  stylize("vdhost login ", fg("blue")) +
                  stylize("and provided the correct email address and machine key.", fg("red")))
            exit(0)

        if not os.path.isfile("/etc/supervisor/conf.d/vdclient.conf"):
            print(stylize("Something went wrong during the installation process. Please try running ", fg("red")) +
                  stylize("vdhost install ", fg("blue")) +
                  stylize("again.", fg("red")))
            exit(0)

        else:
            try:
                print(stylize("Launching the Vectordash client on this machine...", fg("green")))
                # Run the client script
                subprocess.call("sudo supervisorctl start vdclient", shell=True) 
            
            except subprocess.CalledProcessError as e:
                print(stylize("An unexpected error has occured: ", fg("red")) +
                      stylize(e, fg("red")))
                exit(0)

            except OSError:
                print("You do not have permission to execute this. Try re-running the command as sudo: "
                      + stylize("sudo vdhost start-hosting", fg("blue")))
                exit(0)

    except ValueError as e:
        print(stylize("An unexpected error has occured: " + str(e), fg("red")))

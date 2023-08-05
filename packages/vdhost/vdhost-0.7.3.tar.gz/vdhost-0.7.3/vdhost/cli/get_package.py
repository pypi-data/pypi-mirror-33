import click
import os
import json
import requests
import subprocess

from colored import fg
from colored import stylize
from os import environ

if environ.get('VECTORDASH_BASE_URL'):
    VECTORDASH_URL = environ.get('VECTORDASH_BASE_URL')
    print('Using development URL:' + VECTORDASH_URL)
else:
    VECTORDASH_URL = "http://vectordash.com/"

@click.command(name='get-package')
def get_package():
    """
    args: none |
    Allows host to retrieve client package for machine to be hosted

    """
    try:
        # Path to vectordash directory
        var_folder = os.path.expanduser('/var/')
        var_vd_folder = os.path.expanduser(var_folder + 'vectordash/')
        client_vd_folder = os.path.expanduser(var_vd_folder + 'client/')

        # If the var directory does not exist, create it
        if not os.path.isdir(var_folder) or not os.path.isdir(var_vd_folder) or not os.path.isdir(client_vd_folder):
            print(stylize("Error getting package. You have not ran ", fg("red")) + stylize("vdhost login", fg("blue")))
            exit(0)

        # Save ids to gpu_ids file
        login_file = var_vd_folder + 'login.json'

        if not os.path.isfile(login_file):
            print(stylize("You are not logged in on this machine. Please run ", fg("red")) +
                  stylize("vdhost login", fg("blue")))
            exit(0)

        with open(login_file, 'r') as f:
            data = json.load(f)
            email = data["email"]
            machine_key = data["machine_key"]

        r = requests.post(VECTORDASH_URL + "machines/getpackage/",
                          data={'email': email, 'machine_key': machine_key})

        if r.status_code != 200:
            print(stylize("Your authentication information is invalid. Only VERIFIED hosts can get access.", fg("red")))
            exit(0)

        else:
            open('vectordash-host.tar.gz', 'wb').write(r.content)
            command = ['sudo', 'tar', '-C', '/var/vectordash/client/', '-xvf', 'vectordash-host.tar.gz', '--strip-components=1']
            subprocess.call(command, stdout=subprocess.PIPE)

            os.remove('vectordash-host.tar.gz')
            print(stylize("Package received.", fg("green")))

    except OSError:
        print(stylize("A Permission Denied Error was encountered. Try executing the command again with sudo: ", fg("red"))
              + stylize("sudo vdhost get-package", fg("blue")))

    except Exception as e:
        print(stylize("The following error was encountered: ", fg("red")) + str(e))

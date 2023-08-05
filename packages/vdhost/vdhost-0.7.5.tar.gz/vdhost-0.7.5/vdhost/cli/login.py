import click
import os
import json
import requests

from colored import fg
from colored import stylize
from os import environ

if environ.get('VECTORDASH_BASE_URL'):
    VECTORDASH_URL = environ.get('VECTORDASH_BASE_URL')
    print('Using development URL:' + VECTORDASH_URL)
else:
    VECTORDASH_URL = "http://vectordash.com/"


@click.command(name='login')
def login():
    """
    args: none |
    Allows host to login on machine to be hosted

    """
    try:
        # Path to vectordash directory
        var_folder = os.path.expanduser('/var/')
        var_vd_folder = os.path.expanduser(var_folder + 'vectordash/')
        client_vd_folder = os.path.expanduser(var_vd_folder + 'client/')

        # If the var directory does not exist, create it
        if not os.path.isdir(var_folder):
            os.mkdir(var_folder)

        # If the vectordash directory does not exist, create it
        if not os.path.isdir(var_vd_folder):
            os.mkdir(var_vd_folder)

        # If the client directory does not exist, create it
        if not os.path.isdir(client_vd_folder):
            os.mkdir(client_vd_folder)

        # Ask user for email address
        email = input(stylize("Email: ", fg("blue")))

        # Ask user for machine key
        machine_key = input(stylize("Machine key: ", fg("blue")))

        r = requests.post(VECTORDASH_URL + "authenticate-host/",
                          data={'email': email, 'machine_key': machine_key})

        resp = r.text
        resp = json.loads(resp)

        if not resp['valid_authentication']:
            print(stylize("Your authentication information is invalid.", fg("red")))

        else:
            # login credentials
            login_file = var_vd_folder + 'login.json'

            # Securely save data
            with open(login_file, 'w') as f:
                data = {'email': email, 'machine_key': machine_key}
                json.dump(data, f)

            print(stylize("Saved login information", fg("green")))

    except OSError:
        print(stylize("Could not save login credentials. Please run ", fg("red"))
              + stylize("sudo vdhost login", fg("blue")))
        
    except Exception as e:
        print(stylize("The following error was encountered: ", fg("red")) + str(e))

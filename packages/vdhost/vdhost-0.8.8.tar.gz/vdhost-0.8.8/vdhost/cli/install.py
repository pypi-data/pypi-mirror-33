import click
import subprocess
import os
import json
import requests
from colored import fg, stylize, attr
from os import environ


# getting the base API URL
if environ.get('VECTORDASH_BASE_URL'):
    VECTORDASH_URL = environ.get('VECTORDASH_BASE_URL')
else:
    VECTORDASH_URL = "http://vectordash.com/"


@click.command(name='install')
def install():
    """
    Installs the Vectordash hosting client.
    """

    # the prompt we display before installation
    prompt = "This command will begin the Vectordash host installation process.\nPlease note that this will download 15GB+ of " \
             "data and can take upwards of an hour to complete.\nIf prompted with any selections, please press ENTER " \
             "to pick the default values.""\n\nWould you like to begin the host installation process now? " + \
             '%s%s[yes/no]%s ' % (fg('orchid'), attr('bold'), attr('reset'))

    # the JSON file where login credentials are stored
    login_file = '/var/vectordash/login.json'

    try:

        # ensuring the login file exists
        if not os.path.isfile(login_file):
            print("You are not logged in. Please run " +
                  stylize("vdhost login", fg("blue")) + ' to continue.')
            return

        # opening the login file
        with open(login_file, 'r') as f:
            data = json.load(f)

            # grabbing the email and machine secret
            email = data["email"]
            machine_key = data["machine_key"]

        # getting the package
        r = requests.post(VECTORDASH_URL + "machines/getpackage/",
                          data={'email': email, 'machine_key': machine_key})

        # if the credentials are invalid, we display an error
        if r.status_code != 200:
            print("Invalid authentication information . Please run " +
                  stylize("vdhost login", fg("blue")) + ' to continue.')
            return

        # writing out the tarball
        open('vectordash-host.tar.gz', 'wb').write(r.content)

        # unzipping the tarball
        command = ['sudo', 'tar', '-C', '/var/vectordash/client/',
                   '-xvf', 'vectordash-host.tar.gz', '--strip-components=1']

        # calling the unzip command
        subprocess.call(command, stdout=subprocess.PIPE)

        # delete the tarball once the unzip has been completed
        os.remove('vectordash-host.tar.gz')

        # displaying the prompt and asking the user if they want to continue with the installation process
        response = input(prompt)

        if "y" not in response:
            return

        # Running the installation script
        args = ['bash', '/var/vectordash/client/install.sh']
        subprocess.check_call(args)

    except OSError:
        print('Please run this command with sudo:' + stylize("sudo vdhost install", fg("blue")))

    except Exception as e:
        print("An unexpected error has occurred: " + stylize(e, fg("red")) + str(e))

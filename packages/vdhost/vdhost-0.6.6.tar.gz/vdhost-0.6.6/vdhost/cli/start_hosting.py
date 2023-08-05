import click
import subprocess
import os
import requests
import json

from colored import fg
from colored import stylize

from vdhost import VECTORDASH_URL


@click.command(name='start-hosting')
def start_hosting():
    """
    args: None |
    Runs the Vectordash client on the host's machine

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

        if not os.path.isfile(var_vd_folder + 'install_complete'):
            print("You cannot start hosting until you have setup your machine. Please run " +
                  stylize("vdhost install", fg("blue")) + " first!")
            exit(0)

        # path to login file
        login_file = os.path.expanduser(var_vd_folder + 'login.json')
        
        try:
            with open(login_file, 'r') as f:
                data = json.load(f)
                email = data["email"]
                machine_key = data["machine_key"]
                r = requests.post(VECTORDASH_URL + "authenticate-host/",
                                  data={'email': email, 'machine_key': machine_key})
                resp = r.text
                resp = json.loads(resp)
                if not resp['valid_authentication']:
                    print(stylize("Invalid authentication information. You are not a verified host.", fg("red")))
                    exit(0)

        except Exception as e:
            print(stylize("An error occurred, Please make sure you have run ", fg("red")) +
                  stylize("vdhost login ", fg("blue")) +
                  stylize("and provided the correct email address and machine key.", fg("red")))
            exit(0)

        # If directories don't exist, exit the program and instruct user to run 'vdhost install'
        if not os.path.isdir(var_folder) or not os.path.isdir(var_vd_folder):
            print(stylize("Could not launch", fg("red")))
            print(stylize("Are you sure have run: ", fg("red")), stylize("vdhost install", fg("blue")))
            exit(0)

        # Client file and its dependencies - should all be in /var/vectordash/client/
        client_py = os.path.expanduser(var_vd_folder + 'client.cpython-35.pyc')
        sshtunnel_py = os.path.expanduser(var_vd_folder + 'SSHtunnel.cpython-35.pyc')
        networkingprotocol_py = os.path.expanduser(var_vd_folder + 'NetworkingProtocol.cpython-35.pyc')
        specs_py = os.path.expanduser(var_vd_folder + 'specs.cpython-35.pyc')
        containercontroller_py = os.path.expanduser(var_vd_folder + 'ContainerController.cpython-35.pyc')
        helper_py = os.path.expanduser(var_vd_folder + 'helper.cpython-35.pyc')

        # If any of the client files are missing, program will not execute
        if not os.path.isfile(client_py) or not os.path.isfile(sshtunnel_py) or not os.path.isfile(specs_py) or \
                not os.path.isfile(networkingprotocol_py) or not os.path.isfile(containercontroller_py) or \
                not os.path.isfile(helper_py):

            print(stylize("You are missing the Vectordash client package. Please run ", fg("red")) +
                  stylize("vdhost get-package ", fg("blue")) +
                  stylize("to get all missing files.", fg("red")))
            print(stylize("\nPlease note: Only VERIFIED hosts can run this command.", fg("violet")))
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
            
            except subprocess.CalledProcessError:
                print(stylize("It looks as if your files have been corrupted. Please run ", fg("red")) +
                      stylize("vdhost get-package ", fg("blue")) +
                      stylize("to get all missing files.", fg("red")))
                exit(0)

            except OSError:
                print("You do not have permission to execute this. Try re-running the command as sudo: "
                      + stylize("sudo vdhost start-hosting", fg("blue")))
                exit(0)

    except ValueError as e:
        print(stylize("The following error was encountered: " + str(e), fg("red")))
        print(stylize("The Vectordash client could not be launched.", fg("red")))

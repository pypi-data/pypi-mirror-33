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


@click.command(name='stop-hosting')
def stop_hosting():
    """
    args: None |
    Stops the Vectordash client daemon on the host's machine

    """
    try:
        print(stylize("Stopping the Vectordash client on this machine", fg("green")))

        # Path to vectordash directory
        var_folder = os.path.expanduser('/var/')
        var_vd_folder = os.path.expanduser(var_folder + 'vectordash/')
       
        if not os.path.isfile(var_vd_folder + 'install_complete'):
            print("You are not currently running the Vectordash hosting client because you have not setup your machine "
                  "yet. Please run " + stylize("vdhost install", fg("blue")) + " first!")
            exit(0)

        # If directories don't exist, exit the program and instruct user to run 'vdhost install'
        if not os.path.isdir(var_folder) or not os.path.isdir(var_vd_folder):
            print(stylize("Could not exit the program", fg("red")))
            print(stylize("Are you sure have run:", fg("red")) + stylize("vdhost install", fg("blue")))
            exit(0)

        if not os.path.isfile("/etc/supervisor/conf.d/vdclient.conf"):
            print(stylize("Something went wrong during the installation. Please try running ", fg("red")) +
                  stylize("vdhost install", fg("blue")) + stylize(" again.", fg("red")))
            exit(0)

        # check for active instances
        login_file = os.path.expanduser(var_vd_folder + 'login.json')
        try:
            with open(login_file) as f:
                data = json.load(f)
                email = data["email"]
                machine_key = data["machine_key"]
                r = requests.post(VECTORDASH_URL + "active-instance-count/",
                                  data={'email': email, 'machine_key': machine_key})
                resp = r.text
                resp = json.loads(resp)
                num_instances = int(resp['active_instance'])
                if num_instances < 0:
                    print(stylize("You do not have valid authentication. Did you run ", fg("red")) +
                          stylize("vdhost login", fg("blue")))
                    exit(0)
                elif num_instances > 0:
                    print("There are active sessions running on your machine. You cannot stop hosting until "
                          "those sessions are complete.")
                    exit(0)
        except Exception:
            print(stylize("An error occurred, Please make sure you have run ", fg("red")) +
                  stylize("vdhost login ", fg("blue")) +
                  stylize("and provided the correct email address and machine key", fg("red")))

        # File for checking if the client is running or not
        client_running_file = os.path.expanduser(var_vd_folder + 'client_running')

        # If the client pid file exists, stop the client
        if os.path.exists(client_running_file):

            # Read in pid (number)
            print("Checking if the client hosting process is running...")
            f = open(client_running_file, 'r')
            p = f.read()
            f.close()

            # If the pid is below 0, then it is currently not running
            if int(p) == -1:
                print("You are not currently running the client hosting process. Run " +
                      stylize("vdhost start-hosting", fg("blue")) + " to start hosting on Vectordash")
                exit(0)

            subprocess.call("sudo supervisorctl stop vdclient", shell=True)

            # write -1 to pid file (indicating the hosting has stopped)
            f = open(client_running_file, 'w')
            f.write("-1")
            f.close()

        else:
            print("Could not check the client_running file for process id.")
            exit(0)

    except ValueError as e:
        print(stylize("The following error was encountered: ", fg("red")) + str(e))


def pid_exists(pid):
    """
    Check whether pid exists in the current process table.
    """
    try:
        print("Double-checking to ensure client hosting was stopped")
        os.kill(int(pid), 0)
    except OSError:
        print("Pid: " + pid + " killed")
        return False
    else:
        print("Pid: " + pid + " still exists")
        return True

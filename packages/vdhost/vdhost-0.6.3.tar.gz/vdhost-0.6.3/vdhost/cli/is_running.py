import click
import subprocess
import os

from colored import fg
from colored import stylize


@click.command(name='is-running')
def is_running():
    """
    args: None |
    Checks if the Vectordash client is running on the host's machine

    """
    try:
        print(stylize("Checking...", fg("green")))

        # Path to vectordash directory
        var_folder = os.path.expanduser('/var/')
        var_vd_folder = os.path.expanduser(var_folder + 'vectordash/')

        if not os.path.isfile(var_vd_folder + 'install_complete'):
            print("The Vectordash hosting client is NOT running because you have not setup your machine. Please run " +
                  stylize("vdhost install", fg("blue")) + " first!")
            exit(0)
        
        client_running_file = os.path.expanduser(var_vd_folder + 'client_running')
        
        if os.path.exists(client_running_file):

            f = open(client_running_file, 'r')
            p = f.read()
            f.close()
            
            if int(p) != -1:
                print(stylize("The Vectordash hosting client is currently running on this machine", fg("green")))

            else:
                print(stylize("The Vectordash hosting client is NOT running on this machine", fg("red")))

        else:
            print("There was an error in the installation step. Please try running " +
                  stylize("vdhost install ", fg("blue")) + "again.")

    except ValueError as e:
        print(stylize("The following error was encountered: " + str(e), fg("red")))

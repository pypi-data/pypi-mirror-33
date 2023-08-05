import click
import subprocess
import os

from colored import fg
from colored import stylize


@click.command()
def install():
    """
    args: None |
    Runs the install process on the host machine to configure it with ML libraries
    and any other dependencies

    """
    try:
        print(stylize("Launching the Vectordash installation process on this machine", fg("green")))
        print(stylize("If prompted with any questions, please hit ENTER and leave default values", fg("green")))
        response = input(stylize("This process can take 20 minutes to a few hours depending on your download speeds. "
                                 "Do you want to begin the installation process now? [yes/no]", fg("green")))

        if "y" not in response:
            return

        # Path to install script and pip requirements file - should be in the current directory when this is executed
        install_script = os.path.expanduser('/var/vectordash/client/install.sh')

        # If either install script or requirements file is missing, exit the program
        if not os.path.isfile(install_script):
            print(stylize("You are missing the Vectordash client files. Please run ", fg("red")) +
                  stylize("vdhost get-package ", fg("blue")) +
                  stylize("to get all missing files.", fg("red")))

            exit(0)

        else:
            try:
                # Run the installation script
                args = ['bash', install_script]
                subprocess.check_call(args)

            except subprocess.CalledProcessError:
                print(stylize("It looks as if your files have been corrupted. Please run ", fg("red")) +
                      stylize("vdhost get-package ", fg("blue")) +
                      stylize("to get all missing files.", fg("red")))
                exit(0)

            except OSError:
                print("You do not have permission to execute this. Try re-running the command as sudo: "
                      + stylize("sudo vdhost install", fg("blue")))
                exit(0)

    except ValueError as e:
        print(stylize("The following error was encountered: " + str(e), fg("red")))
        print(stylize("The Vectordash client could not be launched.", fg("red")))

import click

from vdhost.cli.install import install
from vdhost.cli.status import status
from vdhost.cli.login import login
from vdhost.cli.set_commands import set_commands
from vdhost.cli.start_hosting import start_hosting
from vdhost.cli.start_miner import start_miner
from vdhost.cli.stop_hosting import stop_hosting
from vdhost.cli.stop_miner import stop_miner


@click.group()
def cli():
    """
    Allows hosts to list their GPUs on Vectordash and
    gives the option of auto-switching to a miner.

    More help is available under each command listed below.
    """
    pass


# adding the commands
cli.add_command(login)                  # Authenticates a machine
cli.add_command(install)                # Installs all the dependencies for hosting on the machine
cli.add_command(status)                 # Checks if the client is running
cli.add_command(start_hosting)          # Bring the hosts machine online for guests to rent
cli.add_command(stop_hosting)           # Stop the client on the host machine to take the machines offline
cli.add_command(set_commands)           # Allows to user to set auto-switching miner
cli.add_command(start_miner)            # Run the miner on the host machine while it is idle
cli.add_command(stop_miner)             # Stop the miner on the host machine



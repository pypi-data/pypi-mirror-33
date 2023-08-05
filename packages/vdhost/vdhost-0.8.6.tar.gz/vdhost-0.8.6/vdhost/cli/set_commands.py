import click
import os
from colored import fg
from colored import stylize
import json


@click.command(name='set-commands')
@click.argument('gpu_id', required=True, nargs=1, type=int)
def set_commands(gpu_id):
    """
    args: gpu_id | Sets a GPU's mining command.
    """
    try:

        # if the installation has not been completed
        if not os.path.isfile('/var/vectordash/install_complete'):
            print("The Vectordash client has not been installed. Please run " +
                  stylize("sudo vdhost install", fg("blue")))
            return

        # ensuring the login file exists
        if not os.path.isfile('/var/vectordash/login.json'):
            print("You are not logged in. Please run " +
                  stylize("vdhost login", fg("blue")) + ' to continue.')
            return

        # create the mining directory if it doesn't exist
        commands_json = '/var/vectordash/mining.json'

        # if mining.json doesn't exist, we create it
        if not os.path.isfile(commands_json):

            # creating mining.json
            with open(commands_json, 'w+') as f:
                f.write('{}')

        # read from commands file
        with open(commands_json, 'r') as f:
            data = f.read()

        # loading the json text as a python dict
        command_dict = json.loads(data)

        # prompting the user to enter a command for this GPU
        prompt = "Enter a bash command that will start the miner on GPU {}. Be sure to provide absolute paths.\n".format(gpu_id)

        # getting the command
        mining_command = input(prompt)

        # updating the command dictionary
        command_dict[gpu_id] = mining_command

        # writing out the updated commands dict
        with open(commands_json, 'w') as f:
            f.write(json.dumps(command_dict))

        print(stylize("Mining command successfully saved.", fg("green")))

    except Exception as e:
        print(stylize("The following error was encountered: " + str(e), fg("red")))

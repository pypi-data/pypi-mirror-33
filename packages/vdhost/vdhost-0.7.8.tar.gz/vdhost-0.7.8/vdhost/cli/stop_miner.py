import click
import subprocess
import os
import json
import xml.etree.ElementTree as ET
import signal
import time

from colored import fg
from colored import stylize


@click.command(name='stop-miner')
@click.argument('gpu_id', nargs=1, type=int, required=True)
def stop_miner(gpu_id):
    """
    args: gpu_id |
    Stop the mining process on the host's machine

    """
    try:
        # Path to vectordash directory
        var_vd_folder = '/var/vectordash/'

        if not os.path.isfile(var_vd_folder + 'install_complete'):
            print("Your machine has not yet been setup and thus is not running a miner. Please run " +
                  stylize("vdhost install", fg("blue")) + " first!")
            exit(0)

        print("Stopping the mining process now...")

        result = subprocess.run(['nvidia-smi', '-q', '-i', str(gpu_id), '-x'], stdout=subprocess.PIPE)
        result = result.stdout.decode()

        # No matching GPUs, so we don't need to stop any processes
        if "No devices" in result:
            exit(0)

        # Parsing the XML tree response
        root = ET.fromstring(result)
        gpu = root.find('gpu')
        processes = gpu.find('processes')

        # killing each of the processes
        for process in processes:
            pid = int(process.find('pid').text)
            pgrp = os.getpgid(pid)

            os.killpg(pgrp, signal.SIGTERM)
            time.sleep(5)

            # If the pids have not yet been killed, try again
            while pid_exists(str(pid)):
                print("Attempting to stop mining")
                os.killpg(pgrp, signal.SIGKILL)
                time.sleep(3)

        else:
            print("Your miner was not started with vdhost. Please run " +
                  stylize("vdhost start-miner " + str(gpu_id), fg("blue")) + " before trying to stop mining.")
            exit(0)
  
    except ValueError as e:
        print(stylize("The following error was encountered: " + str(e), fg("red")))
        print(stylize("Your miner could not be stopped. Are you sure you are using absolute paths?", fg("red")))


def pid_exists(pid):
    """
    Check whether pid exists in the current process table.
    """
    try:
        print("Double-checking to ensure mining was stopped")
        os.kill(int(pid), 0)
    except OSError:
        print("Pid: " + pid + " killed")
        return False
    else:
        print("Pid: " + pid + " still exists")
        return True


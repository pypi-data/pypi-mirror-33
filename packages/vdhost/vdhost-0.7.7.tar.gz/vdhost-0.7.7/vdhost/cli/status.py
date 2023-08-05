import click
import subprocess
import os

from colored import fg, bg, attr, stylize


@click.command(name='status')
def status():
    """
    Checks the status of the Vectordash client.
    """
    try:
        # Path to vectordash directory
        var_folder = os.path.expanduser('/var/')
        var_vd_folder = os.path.expanduser(var_folder + 'vectordash/')

        if not os.path.isfile(var_vd_folder + 'install_complete'):
            print('Vectordash status: ' + '%s%sDisabled %s' % (fg('red'), attr('bold'), attr('reset')))
            exit(0)
        
        client_running_file = os.path.expanduser(var_vd_folder + 'client_running')
        
        if os.path.exists(client_running_file):

            f = open(client_running_file, 'r')
            p = f.read()
            f.close()
            
            if int(p) != -1:
                print('Vectordash status: ' + '%s%sRunning %s' % (fg('chartreuse_4'), attr('bold'), attr('reset')))

            else:
                print('Vectordash status: ' + '%s%sDisabled %s' % (fg('red'), attr('bold'), attr('reset')))

        else:
            print('Vectordash status: ' + '%s%sDisabled %s' % (fg('red'), attr('bold'), attr('reset')))

    except ValueError as e:
        print('Vectordash status: ' + '%s%sDisabled %s' % (fg('red'), attr('bold'), attr('reset')))

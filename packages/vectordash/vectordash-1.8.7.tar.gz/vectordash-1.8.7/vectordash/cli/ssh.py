import click
import requests
import json
import os
import subprocess
from colored import fg
from colored import stylize
from os import environ


# getting the base API URL
if environ.get('VECTORDASH_BASE_URL'):
    VECTORDASH_URL = environ.get('VECTORDASH_BASE_URL')
else:
    VECTORDASH_URL = "https://vectordash.com/"


@click.command(name='ssh')
@click.argument('machine', required=True, nargs=1)
def ssh(machine):
    """
    args: <machine>
    Runs an ssh command to the machine to allow user to connect.

    """
    try:
        # retrieve the secret token from the config folder
        dot_folder = os.path.expanduser('~/.vectordash/')
        token = os.path.join(dot_folder, 'token')

        if os.path.isfile(token):
            with open(token, 'r') as f:
                secret_token = f.readline()

            # API endpoint for machine information
            full_url = VECTORDASH_URL + "api/list_machines/" + str(secret_token)
            r = requests.get(full_url)

            # API connection is successful, retrieve the JSON object
            if r.status_code == 200:
                data = r.json()

                # machine provided is one this user has access to
                if data.get(machine):
                    gpu_mach = (data.get(machine))

                    # Machine pem
                    pem = gpu_mach['pem']

                    # name for pem key file, formatted to be stored
                    machine_name = (gpu_mach['name'].lower()).replace(" ", "")
                    key_file = os.path.expanduser(dot_folder + machine_name + '-key.pem')

                    # create new file ~/.vectordash/<key_file>.pem to write into
                    with open(key_file, "w") as h:
                        h.write(pem)

                    # give key file permissions for ssh
                    os.chmod(key_file, 0o600)

                    # Port, IP address, and user information for ssh command
                    port = str(gpu_mach['port'])
                    ip = str(gpu_mach['ip'])
                    user = str(gpu_mach['user'])

                    # execute ssh command
                    ssh_command = ["ssh", user + "@" + ip, "-p", port, "-i", key_file]
                    try:
                        subprocess.check_call(ssh_command)
                    except subprocess.CalledProcessError:
                        pass

                else:
                    print(stylize(machine + " is not a valid machine id.", fg("red")))
                    print("Please make sure you are connecting to a valid machine")

            else:
                print(stylize("Could not connect to vectordash API with provided token", fg("red")))

        else:
            # If token is not stored, the command will not execute
            print(stylize("Unable to connect with stored token. Please make sure a valid token is stored.", fg("red")))
            print("Run " + stylize("vectordash secret <token>", fg("blue")))
            print("Your token can be found at " + stylize("https://vectordash.com/edit/verification/", fg("blue")))

    except TypeError:
        type_err = "There was a problem with ssh. Please ensure your command is of the format "
        print(type_err + stylize("vectordash ssh <id>", fg("blue")))

import click
import requests
import paramiko
import uuid
import os
import subprocess
from colored import fg
from colored import stylize
from os import environ


# getting the base API URL
if environ.get('VECTORDASH_BASE_URL'):
    VECTORDASH_URL = environ.get('VECTORDASH_BASE_URL')
else:
    VECTORDASH_URL = "http://vectordash.com/"


@click.command(name='jupyter')
@click.argument('machine', required=True, nargs=1)
def jupyter(machine):
    """
    args: <machine>
    Creates a reverse SSH tunnel to allow you to work on a remote jupyter notebook in a local browser

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

                    # give key file permissions for jupyter
                    os.chmod(key_file, 0o600)

                    # Port, IP address, and user information for jupyter command
                    port = str(gpu_mach['port'])
                    ip = str(gpu_mach['ip'])
                    user = str(gpu_mach['user'])

                    ssh = paramiko.SSHClient()

                    # adding the hostkeys automatically
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                    ssh.connect(hostname=ip,
                                port=int(port),
                                username=user,
                                key_filename=key_file)

                    # Serve Jupyter from remote location
                    jupyter_token = str(uuid.uuid4().hex)
                    ssh.exec_command('touch hi')
                    cmd = 'nohup jupyter notebook --no-browser --port=8889 --NotebookApp.token=' + jupyter_token + ' >/dev/null 2>&1 &'
                    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
                    outlines = ssh_stdout.readlines()
                    resp = ''.join(outlines)
                    # print(resp)
                    ssh.exec_command('touch bye')
                    ssh.close()

                    # execute ssh command
                    jupyter_command = ["ssh", "-i", key_file, "-N", "-f", "-L", "localhost:8890:localhost:8889",
                                       user + "@" + ip, "-p", port]
                    try:
                        subprocess.call(jupyter_command)
                        print(stylize("To access your jupyter notebook, please open the following URL in your browser:",
                                      fg("green")))
                        print("http://localhost:8890/?token=" + jupyter_token)
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
        type_err = "There was a problem with entry. Please ensure your command is of the format "
        print(type_err + stylize("vectordash jupyter <id>", fg("blue")))

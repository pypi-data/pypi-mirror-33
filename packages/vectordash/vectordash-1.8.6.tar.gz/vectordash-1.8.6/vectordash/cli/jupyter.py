import click
import requests
import uuid
import os
import subprocess
import paramiko
import random
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
    Serves a remote jupyter notebook in a local browser

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

                    # give key file permissions
                    os.chmod(key_file, 0o600)

                    # Port, IP address, and user information
                    port = str(gpu_mach['port'])
                    ip = str(gpu_mach['ip'])
                    user = str(gpu_mach['user'])

                    # Paramiko ssh client for jupyter serving on remote machine
                    ssh = paramiko.SSHClient()

                    # adding the hostkeys automatically
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                    # ssh connect to remote machine
                    ssh.connect(hostname=ip,
                                port=int(port),
                                username=user,
                                key_filename=key_file)

                    # Token generation for jupyter server
                    jupyter_token = str(uuid.uuid4().hex)

                    #remote_port = 8889
                    #local_port = 8890
                    
                    # grab a remote port that isn't being used
                    remote_port = None
                    while remote_port is None:
                        try_port = random.randint(1024, 49152)
                        cmd = 'lsof -i :{}'.format(try_port)
                        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
                        if ssh_stdout.readline() == "":
                            remote_port = try_port
                            break
                
                    # grab a local port that isn't being used
                    local_port = None
                    while local_port is None:
                        try_port = random.randint(1024, 49152)
                        cmd = ['lsof', '-i', ':{}'.format(try_port)]
                        res = subprocess.call(cmd)
                        if res != 0:
                            local_port = try_port
                            break                    

                    # Serve Jupyter from REMOTE location
                    # remote port (container)
                    # make sure to first set path variables by sourcing bash_profile
                    cmd = 'source /home/{}/.bash_profile; '.format(user)
                    cmd += 'jupyter notebook --no-browser --port={} --NotebookApp.token={} > /dev/null 2>&1 & disown'.format(remote_port, jupyter_token)
                    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)

                    # Jupyter localhost port forwarding command on LOCAL machine, will run in foreground
                    # first port is local port (guest machine), second port is remote port (container)
                    jupyter_cmd = ['ssh', '-i', key_file, '-N', '-L', 'localhost:{}:localhost:{}'.format(local_port, remote_port),
                                   '{}@{}'.format(user, ip), '-p', port]

                    try:
                        # Instructions and URL for browser to open up jupyter notebook
                        print(stylize("To access your jupyter notebook, open this URL in your browser:", fg("green")))
                        print(stylize("http://localhost:{}/?token={}".format(local_port, jupyter_token), fg("green")))
                        print("To close the notebook server, press CTRL + C")

                        # Start local port forwarding
                        subprocess.call(jupyter_cmd)

                    except subprocess.CalledProcessError:
                        pass

                    except KeyboardInterrupt:
                        # On KeyboardInterrupt (CTRL + C), kill both remote and local jupyter processes
                        kill_cmd = "ps -ef | grep {} | grep -v grep | awk '{{print $2}}' | xargs kill".format(jupyter_token)
                        kill_stdin, kill_stdout, kill_stderr = ssh.exec_command(kill_cmd)
                        reset_cmd = "rm -r /home/ubuntu/.ipython"
                        reset_stdin, reset_stdout, reset_stderr = ssh.exec_command(reset_cmd)
                        print("Killed.")

                    # Close remote connection
                    ssh.close()

                else:
                    print(stylize(machine + " is not a valid machine id.", fg("red")))
                    print("Please make sure you are trying to use a valid machine")

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



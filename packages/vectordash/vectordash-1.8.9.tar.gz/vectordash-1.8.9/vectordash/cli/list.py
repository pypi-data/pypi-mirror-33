import click
import requests
import json
import os
from os import environ
from colored import fg
from colored import stylize
from colored import attr


# getting the base API URL
if environ.get('VECTORDASH_BASE_URL'):
    VECTORDASH_URL = environ.get('VECTORDASH_BASE_URL')
    print("Using development URL: {}".format(VECTORDASH_URL))
else:
    VECTORDASH_URL = "https://vectordash.com/"


@click.command(name='list')
def list():
    """
    Lists your active GPU instances.
    """
    try:
        token = os.path.expanduser('~/.vectordash/token')

        if os.path.isfile(token):
            with open(token, 'r') as f:
                secret_token = f.readline()

                # building the full URL
                full_url = VECTORDASH_URL + "api/list_machines/" + str(secret_token)

            r = requests.get(full_url)

            if r.status_code == 200:
                data = r.json()

                if len(data) > 0:
                    green_bolded = fg("green") + attr("bold")
                    print("Your Vectordash machines:")
                    for i in range(len(data)):

                        # getting the machine dict (we add one since we don't zero index the list we print out)
                        machine = data[str(i + 1)]
                        pretty_id = stylize("[" + str(i + 1) + "]", green_bolded)

                        # building the string to print out
                        machine_string = str(pretty_id) + " " + str(machine['name'])

                        # if an error has occurred, we display an error
                        if machine['error_occurred']:
                            machine_string = machine_string + stylize(" (unexpected error)", fg("red"))

                        # if the machine is not ready yet
                        elif not machine['ready']:
                            machine_string = machine_string + " (starting)"

                        print(machine_string)
                else:
                    vd = stylize(VECTORDASH_URL + "create/", fg("blue"))
                    print("You currently haven no instances. Go to " + vd + " to start an instance.")
            else:
                print(stylize("Invalid token. Please enter a valid token.", fg("red")))

        else:
            print(stylize("Unable to locate token. Please make sure a valid token is stored.", fg("red")))
            print("Run " + stylize("vectordash secret <token>", fg("blue")))
            print("Your token can be found at " + stylize("https://vectordash.com/edit/verification", fg("blue")))

    except TypeError:
        type_err = "Please make sure a valid token is stored. Run "
        print(type_err + stylize("vectordash secret <token>", fg("blue")))

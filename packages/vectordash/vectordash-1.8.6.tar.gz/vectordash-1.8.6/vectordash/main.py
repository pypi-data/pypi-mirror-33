import click

from vectordash.cli.jupyter import jupyter
from vectordash.cli.list import list
from vectordash.cli.pull import pull
from vectordash.cli.push import push
from vectordash.cli.secret import secret
from vectordash.cli.ssh import ssh


@click.group()
def cli():
    """
    Vectordash CLI interacts with Vectordash server and executes your commands.
    More help is available under each command listed below.
    """
    pass


# adding the commands
cli.add_command(jupyter)
cli.add_command(list)
cli.add_command(push)
cli.add_command(pull)
cli.add_command(secret)
cli.add_command(ssh)

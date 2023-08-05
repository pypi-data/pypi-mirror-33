import click
from epistle.epistle import Epistle

@click.group()
def epistle():
    """ Epistle is a tool for taking notes in Vim and saving them using Git.
    
    See more at http://github.com/msharp/epistle
    """
    pass


@epistle.command()
def list():
    """ List available Epistles
    """
    Epistle().list()


@epistle.command()
@click.argument('name')
def view(name):
    """ View the contents of an Epistles
    """
    Epistle().view(name)


@epistle.command()
@click.argument('name')
def new(name):
    """ Create a new Epistle
    """
    Epistle().new(name)


@epistle.command()
@click.argument('name')
def edit(name):
    """ Edit an Epistle
    """
    Epistle().edit(name)


@epistle.command()
@click.argument('name')
def delete(name):
    """ Delete an Epistle
    """
    epistle = Epistle()
    epistle.git.delete(name)
    epistle.git.commit(f"deleted {name}")
    epistle.git.push()


@epistle.command()
@click.argument('name')
@click.argument('new_name')
def rename(name, new_name):
    """ Rename an Epistle
    """
    epistle = Epistle()
    epistle.git.rename(name, new_name)
    epistle.git.commit(f"Renamed {name} to {new_name}")
    epistle.git.push()


@epistle.command()
@click.option('--pull', 'action', flag_value='pull')
@click.option('--push', 'action', flag_value='push')
def git(action):
    """ Interact with the remote Git repo

    """
    epistle = Epistle()

    if action == 'pull':
        click.echo(f"Pull from git remote: {epistle.git.remote}")
        epistle.git.pull()

    if action == 'push':
        click.echo(f"Push to git remote: {epistle.git.remote}")
        epistle.git.push()



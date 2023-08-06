import click

from kapp import Kapp


@click.group()
def cli():
    pass


@cli.command()
def up():
    Kapp().up()


@cli.command()
def down():
    Kapp().deploy()


@cli.command()
def deploy():
    Kapp().deploy()

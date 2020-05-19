import click


@click.group()
def cli():
    pass


@click.command()
@click.option("engine_type", "-t", "--engine-type",
              help="The kind of type of the tra")
def sync(type):
    pass


@click.command()
@click.option("engine_type", "-t", "engine_type")
def apps(engine_type):
    pass

import click
import os

@click.command()

@click.option('--file', '-f', is_flag=True,
              help="Count files only.")
@click.option('--dir', '-d', is_flag=True,
              help="Count directories only.")

#Maybe is better to define this argument to the type of 'click.Path'
@click.argument('path', nargs=1, default='.')
def fdc(path, file, dir):
    """Count the number of files or dirs in a given dirs."""
    absPath = os.path.abspath(path)
    #click.echo(absPath)
    iter = os.scandir(absPath)
    if file:
        click.echo(len([x for x in iter if x.is_file()]))
    elif dir:
        click.echo(len([x for x in iter if x.is_dir()]))
    else:
        click.echo(len([x for x in iter]))

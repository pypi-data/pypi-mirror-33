from pathlib import Path

import click

from upersetter.make import SetUp
from upersetter.scan import Scanner


@click.group()
def cli():
    pass


@click.group()
def setup():
    pass


@click.command()
@click.argument('structure')
@click.option('--options', default=None)
@click.option('--outdir', default='.')
@click.option('--templates', default='./templates')
@click.option('--metadata', default=None)
@click.option('--unsafe', is_flag=True)
@click.option('--background', is_flag=True)
@click.argument('params', nargs=-1)
def files(structure, options, outdir, templates, metadata, unsafe, background, params):
    # TODO: overrides = dict([param.split('=') for param in params])
    # TODO: if we introduce overrides we should read the yaml here and merge overrides and options dicts
    setup = SetUp(structure)
    setup.options = options
    setup.templates = templates
    setup.out_dir = outdir
    setup.unsafe = unsafe
    setup.metadata = metadata
    setup.setup(not background)


@click.command()
@click.argument('path')
@click.option('--outdir', default='./')
@click.option('--unsafe', is_flag=True)
@click.option('--background', is_flag=True)
@click.argument('params', nargs=-1)
def folder(path, outdir, unsafe, background, params):
    metadata = Path(path).joinpath('metadata.yaml')
    options = Path(path).joinpath('options.yaml')
    templates = Path(path).joinpath('templates')

    setup = SetUp(str(Path(path).joinpath('structure.yaml')))
    setup.out_dir = outdir
    setup.unsafe = unsafe

    if metadata.exists():
        setup.metadata = str(metadata)
    if options.exists():
        setup.options = str(options)
    if templates.exists():
        setup.templates = str(templates)
    setup.setup(not background)


@click.command()
@click.argument('scandir')
@click.argument('outdir')
@click.option('--inline', is_flag=True)
def scan(scandir, outdir, inline):
    Scanner(scandir, outdir, inline_content=inline).scan()


setup.add_command(folder)
setup.add_command(files)
cli.add_command(setup)
cli.add_command(scan)

if __name__ == '__main__':
    cli()

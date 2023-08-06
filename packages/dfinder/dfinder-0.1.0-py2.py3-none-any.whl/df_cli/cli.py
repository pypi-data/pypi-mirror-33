# -*- coding: utf-8 -*-

"""Console script for df_cli."""

from __future__ import print_function

import json
import sys

import click
from tabulate import tabulate

from .df_request import search_images


class SoftwareType(click.ParamType):
    name = 'software_type'

    def convert(self, value, param, ctx):
        try:
            software, version = value.split(':')
            # TODO: check that the software version is correctlly formatted
            return software, version
        except ValueError:
            self.fail('%s is not a valid software version' % value, param, ctx)


@click.command()
@click.argument('software', nargs=-1, required=True, type=SoftwareType())
@click.option('--sort', '-s',
              type=click.Choice(['+size', '-size',
                                 '+pulls', '-pulls',
                                 '+stars', '-stars']),
              multiple=True,
              default=('+stars', '+pulls', '-size'))
def main(software, sort):
    """Command line interface for DockerFinder"""

    # request images
    params = { s:v for s, v in software }
    params['sort'] = [ s[1:] if s[0] == '+' else s for s in sort ]
    try:
        count, images = search_images(params)
    except Exception as e:
        raise click.ClickException(e.args)

    # Print founded images
    click.echo('Finded {} images.'.format(count))
    if count == 0:
        return 0

    click.echo()
    table = tabulate(
        [[i+1, img['name'], img['size']/1000/1000, img['pulls'], img['stars']]
        for i, img in enumerate(images[:10])],
        headers=['#', 'Name', 'Size (MB)', 'Pulls', 'Stars'])
    click.echo(table)

    # Select an image
    click.echo()
    selection = click.prompt('Please select an image', type=int, default=-1)
    if selection < 0:
        return 0
    try:
        click.echo(json.dumps(images[selection + 1], sort_keys=True, indent=2))
    except IndexError:
        raise click.ClickException('Not a valid image id.')
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

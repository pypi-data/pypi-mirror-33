# -*- coding: utf-8 -*-

"""Console script for dayiwasborn."""
import sys
import click


#@click.command()
#def main(args=None):
#    """Console script for dayiwasborn."""
#    click.echo("Replace this message by putting your code into "
#               "dayiwasborn.cli.main")
#    click.echo("See click documentation at http://click.pocoo.org/")
#    return 0

from dayiwasborn.dayiwasborn import dayiwasborn

@click.command()
@click.argument('name', type=str)
@click.argument('year', type=int)
@click.argument('month', type=int)
@click.argument('day', type=int)
def main(name, year, month, day):
    click.echo(dayiwasborn(name, year, month, day))
    if year < 2000:
        click.echo("You're old!")
    return 0



if __name__ == "__main__":
    import sys
    sys.exit(main())  # pragma: no cover

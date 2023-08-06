# -*- coding: utf-8 -*-
"""Console script for udserver."""
import sys
import click
from udserver import udserver


@click.command()
def main(args=None):
    udserver.show_localip()
    udserver.app.run(host='0.0.0.0', debug=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

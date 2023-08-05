# -*- coding: utf-8 -*-

"""Console script for mcore_organization_chart."""
import sys
import click

from .core import OrganizationTreeBuilder

@click.command()
@click.argument('input', type=click.Path(exists=True))
def main(input):
    with open(input) as fp:
        target_employees = [line.strip() for line in fp]

    tree_builder = OrganizationTreeBuilder(target_employees)
    tree_builder.build()
    tree_builder.print()
    
if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

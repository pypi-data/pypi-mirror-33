import click
import sys

from weighted_choice import alive as alive_function


@click.group()
@click.option('--verbose/--quiet', default=False)
@click.pass_context
def cli(ctx, verbose):
    ctx.obj['VERBOSE'] = verbose


@cli.command()
@click.pass_context
def alive(ctx):
    verbose = ctx.obj['VERBOSE']
    if alive_function():
        if verbose:
            print("Weighted Choice is alive and well!")
    else:
        if verbose:
            print("Something is wrong with Weighted Choice")
        sys.exit(1)


def main():
    cli(obj={})


if __name__ == '__main__':
    main()

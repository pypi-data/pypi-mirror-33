import click


def share_validator(ctx, param, value):
    if value:
        if value > 1:
            raise click.BadParameter('Share needs to be lower than 1.')

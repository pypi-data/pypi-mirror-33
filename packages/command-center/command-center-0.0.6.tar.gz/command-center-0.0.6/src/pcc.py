from subprocess import Popen, PIPE
import click
from utils import load_scripts


def print_commands(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    for command in load_scripts().keys():
        click.echo(command)
    ctx.exit()


@click.command()
@click.option('--commands', is_flag=True, callback=print_commands,
              expose_value=False, is_eager=True,
              help='Display the list of available commands in your pcc file')
@click.argument('script_keys', nargs=-1)
def main(script_keys):
    scripts = load_scripts()
    for key in script_keys:
        command_call = scripts[key]
        with Popen(command_call.split(' '), stdout=PIPE) as proc:
            click.echo(proc.stdout.read())


if __name__ == '__main__':
    main()

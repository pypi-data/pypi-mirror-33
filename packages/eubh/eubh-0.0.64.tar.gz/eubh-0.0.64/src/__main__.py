from os import system

import click
from click import echo

import eubh.get as get_package
import eubh.put as put_package
import eubh.utils as utils
import eubh.watch as watch_package
from eubh.config import VERSION, HTTP_ADDRESS, WS_ADDRESS

_global_options = [
    click.option('--verbose', '-v', 'verbosity', flag_value=2, default=1, help='Enable verbose output'),
]


def global_options(func):
    for option in reversed(_global_options):
        func = option(func)
    return func


@click.group()
def get_group():
    pass


@get_group.command()
@click.argument('key', required=True)
@click.argument('path', required=True)
@click.option('--code/--no-code', default=True, help='Get code source')
@click.option('--result/--no-result', default=True, help='Get result')
@click.option('--unzip/--no-unzip', default=False, help='Unzip input')
@click.option('-ho', '--host', default=HTTP_ADDRESS, help="Server host")
def get(key, path, code, result, unzip, host):
    if code:
        get_package.Get(key).get(path, unzip, host)
    if result:
        get_package.Get(key, 'result').get(path, unzip, host)


@click.group()
def put_group():
    pass


@put_group.command()
@click.argument('key', required=True)
@click.argument('path', required=True)
@click.option('--folder/--no-folder', default=True, help='Upload directory')
@click.option('--code/--no-code', default=False, help='Upload code')
@click.option('--result/--no-result', default=False, help='Put result')
@click.option('-ho', '--host', default=HTTP_ADDRESS, help='Server host')
def put(key, path, folder, code, result, host):
    if code:
        put_package.Put(key).put(path, folder, host)
    if result:
        put_package.Put(key, 'result').put(path, folder, host)


@click.group()
def watch_group():
    pass


@watch_group.command()
@global_options
@click.option('-k', '--key')
@click.option('-t', '--time', default=10, help='Loop time (s)')
@click.option('-v', '--verbosity', default=True, help='Verbose mode')
@click.option('-ho', '--host', default=HTTP_ADDRESS, help='Watch server address')
@click.option('-w', '--webscoket', default=WS_ADDRESS, help='Webscoket server address')
@click.option('-m','--miner', default='', help='Miner docker cmd')
@click.option('-o','--outname', default='minerout', help='Miner logs out')
def watch(key, time, verbosity, host, webscoket, miner, outname):
    watch_package.Watch(key, time, verbosity, host, webscoket, miner, outname).watch()


@click.group()
def init_group():
    pass


@init_group.command()
def init():
    utils.init_environment()


@click.group()
def upgrade_group():
    pass


@upgrade_group.command()
def upgrade():
    system('pip install --upgrade eubh --no-cache-dir')


@click.group()
def version_group():
    pass


@version_group.command()
def version():
    echo(VERSION)


@click.group()
def container_group():
    pass


cli = click.CommandCollection(
    sources=[get_group, put_group, watch_group, init_group, upgrade_group, version_group])


def main():
    cli()


if __name__ == "__main__":
    cli()

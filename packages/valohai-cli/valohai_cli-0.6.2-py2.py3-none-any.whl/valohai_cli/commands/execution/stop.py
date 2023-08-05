import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import success, warn
from valohai_cli.range import IntegerRange


@click.argument('counters', required=False, nargs=-1)
@click.option('--all', default=None, is_flag=True, help='Stop all in-progress executions.')
@click.command()
def stop(counters, all=False):
    """
    Stop one or more in-progress executions.
    """
    project = get_project(require=True)
    params = {'project': project.id}
    if counters and all:
        raise click.UsageError('Pass either an execution # or `--all`, not both.')
    elif counters:
        params['counter'] = sorted(IntegerRange.parse(counters).as_set())
    elif all:
        params['status'] = 'incomplete'
    else:
        warn('Nothing to stop (pass #s or `--all`)')
        return 1

    for execution in request('get', '/api/v0/executions/', params=params).json()['results']:
        click.echo('Stopping #{counter}... '.format(counter=execution['counter']), nl=False)
        resp = request('post', execution['urls']['stop'])
        click.echo(resp.text)
    success('Done.')

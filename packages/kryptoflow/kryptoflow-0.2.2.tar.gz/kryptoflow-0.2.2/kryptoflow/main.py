
import click
from kryptoflow.cli.train import train
from kryptoflow.cli.serve import serve
from kryptoflow.cli.scrape import
# from polyaxon_cli.cli.build import build
# from polyaxon_cli.cli.check import check
# from polyaxon_cli.cli.cluster import cluster
# from polyaxon_cli.cli.upload import upload
# from polyaxon_cli.cli.user import user
# from polyaxon_cli.cli.version import check_cli_version, upgrade, version
# from polyaxon_cli.logger import clean_outputs, configure_logger
# from polyaxon_cli.managers.config import GlobalConfigManager


@click.group()
@click.option('-v', '--verbose', is_flag=True, default=False, help='Turn on debug logging')
@click.option('--version', help='Show which version is installed')

@click.pass_context
# @clean_outputs
def cli(context, verbose):
    """ Polyaxon CLI tool to:
        * Parse, Validate, and Check Polyaxonfiles.
        * Interact with Polyaxon server.
        * Run and Monitor experiments.
    Check the help available for each command listed below.
    """
    configure_logger(verbose or GlobalConfigManager.get_value('verbose'))
    if context.invoked_subcommand not in ['config', 'version', 'login', 'logout']:
        check_cli_version()


cli.add_command(train)
cli.add_command(serve)
cli.add_command(whoami)
cli.add_command(user)
cli.add_command(superuser)
cli.add_command(upgrade)
cli.add_command(version)
cli.add_command(config)
cli.add_command(check)
cli.add_command(init)
cli.add_command(cluster)
cli.add_command(project)
cli.add_command(build)
cli.add_command(tensorboard)
cli.add_command(notebook)
cli.add_command(group)
cli.add_command(experiment)
cli.add_command(job)
cli.add_command(upload)
cli.add_command(run)
cli.add_command(dashboard)

from __future__ import unicode_literals

import os

import click

from cis_client import cli
from cis_client.commands import utils
from cis_client.lib.cis_gateway import http_upload_client
from cis_client.lib.cis_gateway import aspera_client
from cis_client.lib.cis_gateway import sftp_client
from cis_client import exception


@click.command('upload', context_settings=utils.CONTEXT_SETTINGS, help='Uploads content via HTTP/Aspera/SFTP.')
@click.option('--protocol', type=click.Choice(['http', 'aspera', 'sftp']), default='http',
              help='Protocol for loading. Can be http, aspera or sftp.')
@click.option('--ingest-point', required=True, type=click.STRING,
              help='Ingest point to load content to.')
@click.option('--source-file-list', type=click.Path(resolve_path=True),
              help='Path to file that contains list of full source paths to content separated by new line symbol. '
                   'Files from the list will be uploaded.')
@click.option('--source-file', type=click.STRING,
              help='Comma separated list of full source paths to content that will be uploaded. '
                   'Can contain path to directory with files if upload protocol is aspera.')
@click.option('--skip-errors', type=click.BOOL, default=False,
              help='Continue upload other files if some file upload was failed.')
@click.option('--destination-path', type=click.STRING,
              help='Destination path. '
                   'Can be directory like dir1/dir2/. If value ends with / destination '
                   'file path will be composed from this value + source filename. '
                   'If this value doesn\'t end with / so destination path will be the same.'
                   'In case when full destination path is specified input path list can contain only one input file.')
@utils.add_host_options
@utils.add_auth_options
@utils.add_credentials_options
@cli.pass_context
@utils.handle_exceptions
@utils.check_cis_version
def cli(ctx, **kwargs):
    paths = utils.get_source_file_list_from_kwargs(**kwargs)
    aaa_host = kwargs.pop('aaa_host')
    username = kwargs.pop('username')
    password = kwargs.pop('password')
    north_host = kwargs.pop('north_host')
    ingest_point = kwargs.pop('ingest_point')
    destination_path = kwargs.pop('destination_path')
    skip_errors = kwargs.pop('skip_errors')
    if destination_path and len(destination_path.split(',')) > 1:
        raise exception.OptionException(
            "Option --destination-path can contain only one path: "
            "directory with '/' suffix or full destination path for single source file.")
    if (destination_path and not destination_path.endswith('/') and
            len(paths) != 1):
        raise exception.OptionException(
            "To upload several files you need to specify destination directory in "
            "--destination-path option. Directory must contain suffix '/'. "
            "For example --destination-path {}/".format(destination_path))

    for path in paths:
        if destination_path:
            if destination_path.endswith('/'):
                full_dst_path = ''.join([destination_path, os.path.basename(path)])
            else:
                full_dst_path = destination_path
        else:
            full_dst_path = os.path.basename(path)
        utils.display("Uploading {} ... to {}".format(path, full_dst_path))
        try:
            if kwargs['protocol'] == 'aspera':
                aspera_client.aspera_upload(
                    aaa_host, username, password,
                    north_host, ingest_point, path, destination_path=full_dst_path, **kwargs)
            else:
                total_size = os.path.getsize(path)
                with utils.ProgressBar(max_value=total_size) as progress_bar:
                    if kwargs['protocol'] == 'http':
                        response = http_upload_client.http_upload(
                            aaa_host, username, password, north_host,
                            ingest_point, path, destination_path=full_dst_path,
                            progress_callback=lambda transfered: progress_bar.update(transfered),
                            **kwargs)
                    elif kwargs['protocol'] == 'sftp':
                        response = sftp_client.sftp_upload(
                            aaa_host, username, password, north_host,
                            ingest_point, path, destination_path=full_dst_path,
                            progress_callback=lambda transfered, whole: progress_bar.update(transfered),
                            **kwargs)
            utils.display("File {} was successfully uploaded to {}".format(path, full_dst_path))
        except Exception as e:
            if skip_errors:
                utils.display("Error: {}".format(e))
            else:
                raise

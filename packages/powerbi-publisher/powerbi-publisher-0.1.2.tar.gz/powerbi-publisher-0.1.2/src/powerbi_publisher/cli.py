import click
import os

from powerbi_publisher.powerbi import PowerBiClient


@click.group()
def main():
    pass


@click.option('--username', default=lambda: os.environ.get('PBI_USERNAME', ''))
@click.option('--password', default=lambda: os.environ.get('PBI_PASSWORD', ''))
@click.option('--report-name', default="")
@click.option('--file', default="")
@click.option('--workspace-id',
              default=lambda: os.environ.get('PBI_WORKSPACE_ID', None))
@click.option('--tenant', default=lambda: os.environ.get('PBI_TENANT', ''))
@click.option('--client-id',
              default=lambda: os.environ.get('PBI_CLIENT_ID', ''))
@click.option('--client-secret',
              default=lambda: os.environ.get('PBI_CLIENT_SECRET', ''))
@main.command('import-pbix')
def import_pbix(username, password, report_name, file, workspace_id,
                tenant, client_id, client_secret):
    config = {
        'resource': 'https://analysis.windows.net/powerbi/api',
        'tenant': tenant,
        'authority_host_url': 'https://login.microsoftonline.com',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password
    }

    powerbi = PowerBiClient(config)

    with open(file, 'rb') as f:
        powerbi.upload_pbix(report_name, f, workspace_id)


if __name__ == "__main__":
    main()
